import torch
from transformers import Qwen2VLForConditionalGeneration, AutoProcessor, BitsAndBytesConfig
from qwen_vl_utils import process_vision_info
from PIL import Image

class QwenService:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(QwenService, cls).__new__(cls)
            cls._instance._initialize_model()
        return cls._instance

    def _initialize_model(self):
        model_id = "Qwen/Qwen2-VL-2B-Instruct"
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        
        # 4-Bit Quantization: Massive Speedup & VRAM reduction for GTX 1650
        bnb_config = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_compute_dtype=torch.float16,
            bnb_4bit_use_double_quant=True,
            bnb_4bit_quant_type="nf4",
        )

        self.model = Qwen2VLForConditionalGeneration.from_pretrained(
            model_id,
            quantization_config=bnb_config,
            device_map="auto",
            trust_remote_code=True
        ).eval()
        
        self.processor = AutoProcessor.from_pretrained(model_id, trust_remote_code=True)

    @torch.no_grad()
    def query(self, image: Image.Image, prompt: str, max_tokens: int = 256):
        messages = [
            {
                "role": "user",
                "content": [
                    {
                        "type": "image", 
                        "image": image, 
                        # Slightly reduced max_pixels for 3x faster processing
                        "min_pixels": 256*28*28, 
                        "max_pixels": 768*28*28 
                    },
                    {"type": "text", "text": prompt},
                ],
            }
        ]

        text = self.processor.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
        image_inputs, _ = process_vision_info(messages)
        
        inputs = self.processor(
            text=[text], images=image_inputs, padding=True, return_tensors="pt"
        ).to(self.device)

        # Optimization: use_cache=True and lower max_new_tokens
        generated_ids = self.model.generate(
            **inputs, 
            max_new_tokens=max_tokens, 
            repetition_penalty=1.1,
            use_cache=True,
            do_sample=False # Greedy search is much faster than sampling
        )
        
        generated_ids_trimmed = [out_ids[len(in_ids):] for in_ids, out_ids in zip(inputs.input_ids, generated_ids)]
        output = self.processor.batch_decode(generated_ids_trimmed, skip_special_tokens=True)[0]
        
        torch.cuda.empty_cache()
        return output