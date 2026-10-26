from pydantic import BaseModel, Field
from typing import List, Dict, Optional

class ChatRequestInput(BaseModel):
    video_id: str
    video_title: str
    channel: Optional[str] = ""
    description: Optional[str] = ""
    category: Optional[str] = ""
    transcript_excerpt: Optional[str] = ""
    question: str
    user_id: Optional[str] = "default_user"
    user_intent: Optional[str] = None

class ChatResponse(BaseModel):
    verdict: str  # "Strongly Recommended", "Recommended", "Neutral / Break", "Off-Goal / Skip"
    usefulness_score: float  # 0 to 100
    answer: str
    key_reason: str
    goal_fit_analysis: str
    budget_context_note: str
    suggested_action: str
