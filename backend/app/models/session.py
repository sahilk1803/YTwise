from sqlalchemy import Column, String, Integer, Float, DateTime, JSON, ForeignKey
from datetime import datetime, timezone
from app.core.database import Base
from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any

def get_utc_now():
    return datetime.now(timezone.utc)

def get_today_str():
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")

class WatchSessionModel(Base):
    __tablename__ = "watch_sessions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String, index=True, default="default_user")
    video_id = Column(String, index=True, nullable=False)
    video_title = Column(String, default="")
    channel = Column(String, default="")
    category = Column(String, nullable=False)
    duration_sec = Column(Integer, default=0)
    session_date = Column(String, index=True, default=get_today_str)
    timestamp = Column(DateTime, default=get_utc_now)

class IntentLogModel(Base):
    __tablename__ = "intent_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String, index=True, default="default_user")
    intent_text = Column(String, nullable=False)
    target_category = Column(String, default="Education")
    target_minutes = Column(Integer, default=60)
    session_date = Column(String, index=True, default=get_today_str)
    start_time = Column(DateTime, default=get_utc_now)
    end_time = Column(DateTime, nullable=True)
    is_active = Column(Integer, default=1)

# API Schemas
class WatchEventInput(BaseModel):
    user_id: Optional[str] = "default_user"
    video_id: str
    video_title: Optional[str] = "Untitled Video"
    channel: Optional[str] = ""
    category: str
    duration_sec: int = 5

class IntentInput(BaseModel):
    user_id: Optional[str] = "default_user"
    intent_text: str
    target_category: Optional[str] = None
    target_minutes: Optional[int] = 60

class ActiveSessionStatus(BaseModel):
    user_id: str
    current_intent: Optional[str] = None
    target_category: Optional[str] = None
    target_minutes: Optional[int] = 60
    today_total_minutes: float
    category_minutes: Dict[str, float]
    category_limits: Dict[str, int]
    category_usage_pct: Dict[str, float]
    warnings: List[str]
    is_any_limit_exceeded: bool
    productivity_score: float

class DailySummaryResponse(BaseModel):
    date: str
    total_watch_minutes: float
    category_breakdown: Dict[str, float]
    category_limits: Dict[str, int]
    productivity_score: float
    current_intent: Optional[str]
    intent_match_pct: float
    intent_vs_reality_summary: str
    ai_wellness_tip: str
    top_videos: List[Dict[str, Any]]

class WeeklyTrendDay(BaseModel):
    date: str
    day_name: str
    total_minutes: float
    productivity_score: float
    category_breakdown: Dict[str, float]
    intent_match_pct: float

class WeeklyAnalyticsResponse(BaseModel):
    days: List[WeeklyTrendDay]
    average_daily_minutes: float
    average_productivity_score: float
    top_categories: List[Dict[str, Any]]
    top_channels: List[Dict[str, Any]]
    overall_intent_match_avg: float
    weekly_ai_assessment: str
