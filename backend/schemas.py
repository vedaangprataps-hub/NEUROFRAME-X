from pydantic import BaseModel
from typing import List, Optional

class ActionItem(BaseModel):
    verb: str
    noun: str
    start: float
    end: float

class HighlightItem(BaseModel):
    start: float
    end: float
    importance: float

class VideoResult(BaseModel):
    video_id: str
    label: str = "action_summary"
    actions: List[ActionItem]
    highlights: List[HighlightItem]
    thumbnail: Optional[str] = None

    class Config:
        json_encoders = {float: lambda v: round(v, 3)}
