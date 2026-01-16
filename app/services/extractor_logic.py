import json
import re
import logging
from app.domain.schemas import PlotData

logger = logging.getLogger("DocumentAuditor")

class DocumentAgent:
    def __init__(self):
        from app.infrastructure.qwen_service import QwenService
        self.ai = QwenService()

    def process(self, image) -> PlotData:
        # --- PASS 1: FAST SCAN ---
        # We ask for a confidence score immediately
        p1_prompt = (
            "Extract Lot No, Block, Address, Model, and Exterior Structures into JSON. "
            "Include a 'confidence_score' (0-100) based on text clarity."
        )
        
        # Limit tokens on Pass 1 to be ultra-fast
        first_pass_raw = self.ai.query(image, p1_prompt, max_tokens=150)
        data = self._clean_and_parse(first_pass_raw)

        # --- SPEED OPTIMIZATION: THE EARLY EXIT ---
        # If the model is confident and data is present, SKIP Pass 2.
        if data.get("confidence_score", 0) > 85 and data.get("lot_no"):
            logger.info(f"Fast-Path Success: {data.get('confidence_score')}%")
            return self._map_to_schema(data, "Fast-Path Verification")

        # --- PASS 2: DEEP AUDIT (Only for complex/messy files) ---
        p2_prompt = f"""
        Review previous scan: {first_pass_raw}
        Verify: 
        1. Is Lot No confused with Lot ID? 
        2. Format exterior structures as 'Name (Dimensions)'. 
        If missing, return null. Return JSON only.
        """
        final_raw = self.ai.query(image, p2_prompt, max_tokens=256)
        data = self._clean_and_parse(final_raw)

        return self._map_to_schema(data, "Deep-Audit Verification")

    def _map_to_schema(self, data, method):
        return PlotData(
            lot_no=data.get("lot_no"),
            block=data.get("block"),
            address=data.get("address"),
            model_selected=data.get("model"),
            external_structure=data.get("exterior_structures"),
            optional_notes=f"Method: {method} | Confidence: {data.get('confidence_score', 'N/A')}%"
        )

    def _clean_and_parse(self, text):
        try:
            json_match = re.search(r'\{.*\}', text, re.DOTALL)
            if json_match:
                parsed = json.loads(json_match.group(0))
                return parsed[0] if isinstance(parsed, list) else parsed
        except:
            pass
        return {}