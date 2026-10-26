from sqlalchemy import Column, String, Integer, DateTime, JSON
from datetime import datetime, timezone
from app.core.database import Base
from pydantic import BaseModel, Field
from typing import List, Dict, Optional

def get_utc_now():
    return datetime.now(timezone.utc)

# SQLAlchemy Models
class UserModel(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, index=True, default="default_user")
    email = Column(String, unique=True, index=True, default="user@example.com")
    name = Column(String, default="Aditya")
    created_at = Column(DateTime, default=get_utc_now)

class UserProfileModel(Base):
    __tablename__ = "user_profiles"

    user_id = Column(String, primary_key=True, index=True, default="default_user")
    daily_budget_min = Column(Integer, default=120)
    category_limits = Column(JSON, default=lambda: {
        "Education": 90,
        "Career": 60,
        "Technology": 60,
        "Productivity": 45,
        "Entertainment": 25,
        "Gaming": 15,
        "Vlog": 15,
        "Music": 30,
        "Shorts": 15,
        "News": 20,
        "Other": 20
    })
    custom_useful_categories = Column(JSON, default=lambda: ["Education", "Career", "Technology", "Productivity"])
    primary_goal = Column(String, default="Placement Preparation (DSA, AI/ML, System Design)")
    learning_topics = Column(JSON, default=lambda: ["DSA", "Machine Learning", "System Design", "Python", "Web Development"])
    updated_at = Column(DateTime, default=get_utc_now, onupdate=get_utc_now)

# Pydantic Schemas
class UserProfileSchema(BaseModel):
    user_id: str = "default_user"
    daily_budget_min: int = 120
    category_limits: Dict[str, int] = Field(default_factory=lambda: {
        "Education": 90,
        "Career": 60,
        "Technology": 60,
        "Productivity": 45,
        "Entertainment": 25,
        "Gaming": 15,
        "Vlog": 15,
        "Music": 30,
        "Shorts": 15,
        "News": 20,
        "Other": 20
    })
    custom_useful_categories: List[str] = Field(default_factory=lambda: ["Education", "Career", "Technology", "Productivity"])
    primary_goal: str = "Placement Preparation (DSA, AI/ML, System Design)"
    learning_topics: List[str] = Field(default_factory=lambda: ["DSA", "Machine Learning", "System Design", "Python", "Web Development"])

class UserProfileUpdate(BaseModel):
    daily_budget_min: Optional[int] = None
    category_limits: Optional[Dict[str, int]] = None
    custom_useful_categories: Optional[List[str]] = None
    primary_goal: Optional[str] = None
    learning_topics: Optional[List[str]] = None
