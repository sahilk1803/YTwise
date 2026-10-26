from sqlalchemy import Column, String, Integer, Float, DateTime, JSON, Text
from datetime import datetime, timezone
from app.core.database import Base
from pydantic import BaseModel, Field
from typing import List, Dict, Optional

def get_utc_now():
    return datetime.now(timezone.utc)

class VideoClassificationModel(Base):
    __tablename__ = "video_classifications"

    video_id = Column(String, primary_key=True, index=True)
    title = Column(String, nullable=False)
    channel = Column(String, default="")
    description = Column(Text, default="")
    content_type = Column(String, nullable=False)
    base_value_score = Column(Float, default=50.0)
    educational_value = Column(Float, default=50.0)
    entertainment_value = Column(Float, default=50.0)
    career_relevance = Column(Float, default=50.0)
    key_takeaways = Column(JSON, default=list)
    tags = Column(JSON, default=list)
    summary = Column(Text, default="")
    cached_at = Column(DateTime, default=get_utc_now)

# Pydantic models for API
class VideoMetadataInput(BaseModel):
    video_id: str
    title: str
    channel: Optional[str] = ""
    description: Optional[str] = ""
    category_tag: Optional[str] = ""
    duration_sec: Optional[int] = 0
    transcript_text: Optional[str] = ""
    user_id: Optional[str] = "default_user"
    user_intent: Optional[str] = ""

class ScoreBreakdown(BaseModel):
    educational_value: float = Field(..., ge=0, le=100)
    entertainment_value: float = Field(..., ge=0, le=100)
    career_relevance: float = Field(..., ge=0, le=100)

class VideoClassificationResponse(BaseModel):
    video_id: str
    title: str
    channel: str
    content_type: str
    base_value_score: float
    base_value_band: str
    score_breakdown: ScoreBreakdown
    personalized_score: float
    personalized_band: str
    is_useful_for_user: bool
    summary: str
    key_takeaways: List[str]
    goal_alignment_reasoning: str
    cached: bool = False
