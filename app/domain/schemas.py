from pydantic import BaseModel
from typing import Optional

class PlotData(BaseModel):
    lot_no: Optional[str] = None
    block: Optional[str] = None
    address: Optional[str] = None
    model_selected: Optional[str] = None
    elevation: Optional[str] = None
    garage_swing: Optional[str] = "Unknown"
    external_structure: Optional[str] = None # For Patio/Lanai with dims
    optional_notes: Optional[str] = None