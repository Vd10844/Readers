import torch
from transformers import Qwen2VLForConditionalGeneration, AutoProcessor
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
        # Qwen2-VL-2B-Instruct is the sweet spot for 4GB VRAM
        model_id = "Qwen/Qwen2-VL-2B-Instruct"
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        
        # We use bfloat16 for better precision on GTX 16-series cards
        self.model = Qwen2VLForConditionalGeneration.from_pretrained(
            model_id,
            torch_dtype=torch.bfloat16 if torch.cuda.is_bf16_supported() else torch.float16,
            device_map="auto",
            trust_remote_code=True
        ).eval()
        
        # The processor handles the "Patching" of the image
        self.processor = AutoProcessor.from_pretrained(model_id, trust_remote_code=True)

    @torch.no_grad()
    def query_document(self, image: Image.Image):
        # We use a very specific, high-intent prompt for architectural data
        prompt = (
            "Analyze this plot plan or architectural report carefully. "
            "Locate and extract the following fields. If a field is handwritten, read it carefully. "
            "1. Lot Number (just the digits) "
            "2. Block Number "
            "3. Full Property Address "
            "4. House Model/Plan Name "
            "5. Elevation "
            "6. Garage Swing (Left, Right, or Straight) "
            "Return the data in a valid JSON format with these keys: "
            "lot_no, block, address, model, elevation, swing."
        )

        messages = [
            {
                "role": "user",
                "content": [
                    {"type": "image", "image": image, "min_pixels": 256*28*28, "max_pixels": 1280*28*28},
                    {"type": "text", "text": prompt},
                ],
            }
        ]

        # Process inputs
        text = self.processor.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
        image_inputs, _ = process_vision_info(messages)
        inputs = self.processor(
            text=[text],
            images=image_inputs,
            padding=True,
            return_tensors="pt",
        ).to(self.device)

        # Inference
        generated_ids = self.model.generate(**inputs, max_new_tokens=1024)
        generated_ids_trimmed = [
            out_ids[len(in_ids):] for in_ids, out_ids in zip(inputs.input_ids, generated_ids)
        ]
        
        return self.processor.batch_decode(
            generated_ids_trimmed, skip_special_tokens=True, clean_up_tokenization_spaces=False
        )[0]