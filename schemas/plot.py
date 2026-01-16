from pydantic import BaseModel
from schemas.field import CandidateField

class PlotExtractionCandidates(BaseModel):
    lot_no: CandidateField
    block: CandidateField
    address: CandidateField
    model_selected: CandidateField
    elevation: CandidateField
    garage_swing: CandidateField
    external_structure: CandidateField
    optional_notes: CandidateField
