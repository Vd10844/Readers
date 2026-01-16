from pydantic import BaseModel
from typing import List, Optional

class FieldCandidate(BaseModel):
    value: Optional[str]
    page: int
    bounding_box: List[int]
    rationale: Optional[str]

class CandidateField(BaseModel):
    candidates: List[FieldCandidate]
