PROMPT = """
Extract semantic candidates for each field listed below.
Return ALL plausible candidates, not just one.

For each candidate:
- value
- page number
- bounding box
- brief rationale explaining why this could match

Fields:
- lot_no
- block
- address
- model_selected
- elevation
- garage_swing
- external_structure
- optional_notes

Rules:
- Return ONLY JSON matching the schema
- Do NOT rank candidates
- Do NOT discard weaker candidates
- If no candidates exist, return an empty list
"""
