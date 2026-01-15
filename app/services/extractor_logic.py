import json
import re
from app.domain.schemas import PlotData

class DocumentExtractor:
    def __init__(self):
        from app.infrastructure.qwen_service import QwenService
        self.ai = QwenService()

    def process(self, image) -> PlotData:
        raw_response = self.ai.query_document(image)
        
        # 1. STRIP MARKDOWN & FIND JSON
        # This regex looks for anything between [ ] or { }
        json_match = re.search(r'(\[.*\]|\{.*\})', raw_response, re.DOTALL)
        data = {}
        
        if json_match:
            try:
                # 2. PARSE THE CLEANED STRING
                parsed = json.loads(json_match.group(0))
                
                # 3. HANDLE LIST OUTPUT
                # If the model returns a list, take the first item as the "Primary" data
                if isinstance(parsed, list) and len(parsed) > 0:
                    data = parsed[0]
                else:
                    data = parsed
            except Exception as e:
                print(f"Failed to parse JSON content: {e}")

        # 4. MAP TO SCHEMA
        return PlotData(
            lot_no=data.get("lot_no"),
            block=data.get("block"),
            address=data.get("address"),
            model_selected=data.get("model"),
            elevation=data.get("elevation"),
            garage_swing=data.get("swing", "Unknown"),
            optional_notes=f"Processed from {type(data).__name__} structure"
        )