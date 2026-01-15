from pydantic import BaseModel, Field
from typing import Optional, Literal

class PlotData(BaseModel):
    lot_no: Optional[str] = Field(None, description="Extracted Lot Number")
    block: Optional[str] = Field(None, description="Extracted Block identifier")
    address: Optional[str] = Field(None, description="Full property address")
    model_selected: Optional[str] = Field(None, description="House model/plan name")
    elevation: Optional[str] = Field(None, description="Architectural elevation")
    garage_swing: Optional[Literal['Left', 'Right', 'Straight', 'Unknown']] = 'Unknown'
    external_structure: Optional[str] = Field(None, description="Materials: Brick, Stone, etc.")
    optional_notes: Optional[str] = Field(None, description="Miscellaneous notes")
