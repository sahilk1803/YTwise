from fastapi import APIRouter, Depends, Query
from typing import Optional
from sqlalchemy.orm import Session
from datetime import datetime, timezone, timedelta
import random
from app.core.database import get_db
from app.models.session import DailySummaryResponse, WeeklyAnalyticsResponse, WatchSessionModel, IntentLogModel
from app.services.analytics_service import AnalyticsService
from app.routes.profile import get_or_create_profile

router = APIRouter(prefix="/analytics", tags=["Analytics"])

@router.get("/daily", response_model=DailySummaryResponse)
def get_daily_analytics(
    user_id: str = "default_user",
    date: Optional[str] = None,
    db: Session = Depends(get_db)
):
    profile = get_or_create_profile(db, user_id)
    return AnalyticsService.get_daily_summary(db, user_id, profile, target_date=date)

@router.get("/weekly", response_model=WeeklyAnalyticsResponse)
def get_weekly_analytics(
    user_id: str = "default_user",
    db: Session = Depends(get_db)
):
    profile = get_or_create_profile(db, user_id)
    return AnalyticsService.get_weekly_analytics(db, user_id, profile)

@router.post("/seed-demo")
def seed_demo_data(
    user_id: str = "default_user",
    db: Session = Depends(get_db)
):
    """Populates realistic 7-day watch history and intent logs for demo purposes."""
    profile = get_or_create_profile(db, user_id)
    today = datetime.now(timezone.utc).date()

    demo_videos = [
        {"title": "NeetCode 150 - Dynamic Programming Deep Dive", "category": "Education", "channel": "NeetCode"},
        {"title": "System Design Interview – Step by Step Guide", "category": "Career", "channel": "ByteByteGo"},
        {"title": "FastAPI & Python 3.14 Crash Course", "category": "Technology", "channel": "freeCodeCamp"},
        {"title": "Building Production AI Agents with Gemini", "category": "Technology", "channel": "Google Cloud Tech"},
        {"title": "GTA 6 Gameplay Reactions & Speculations", "category": "Gaming", "channel": "GamerRealm"},
        {"title": "How to Build Unshakeable Focus & Discipline", "category": "Productivity", "channel": "Ali Abdaal"},
        {"title": "Weekend in Tokyo - 4K Walking Vlog", "category": "Vlog", "channel": "TokyoExplorer"},
        {"title": "Lofi Hip Hop Radio - Beats to Study To", "category": "Music", "channel": "Lofi Girl"},
    ]

    for days_ago in range(7):
        curr_date = today - timedelta(days=days_ago)
        date_str = curr_date.strftime("%Y-%m-%d")

        # Intent
        intent_texts = [
            "Study DSA trees & graphs for placement prep",
            "Learn System Design architectural patterns",
            "Work on FastAPI & AI project portfolio",
            "Prepare 5 LeetCode medium problems",
            "Review Python async features & database indexing"
        ]
        intent_choice = random.choice(intent_texts)
        
        # Check if intent exists for day
        existing_intent = db.query(IntentLogModel).filter(
            IntentLogModel.user_id == user_id,
            IntentLogModel.session_date == date_str
        ).first()
        if not existing_intent:
            db.add(IntentLogModel(
                user_id=user_id,
                intent_text=intent_choice,
                target_category="Education" if "DSA" in intent_choice or "LeetCode" in intent_choice else "Technology",
                target_minutes=60,
                session_date=date_str,
                start_time=datetime.now(timezone.utc) - timedelta(days=days_ago, hours=3),
                is_active=0 if days_ago > 0 else 1
            ))

        # Check if sessions exist for day
        count = db.query(WatchSessionModel).filter(
            WatchSessionModel.user_id == user_id,
            WatchSessionModel.session_date == date_str
        ).count()

        if count == 0:
            # Seed 3 to 6 video sessions
            num_vids = random.randint(3, 6)
            for _ in range(num_vids):
                v = random.choice(demo_videos)
                dur = random.randint(300, 1500)
                db.add(WatchSessionModel(
                    user_id=user_id,
                    video_id=f"demo_vid_{random.randint(100, 999)}",
                    video_title=v["title"],
                    channel=v["channel"],
                    category=v["category"],
                    duration_sec=dur,
                    session_date=date_str,
                    timestamp=datetime.now(timezone.utc) - timedelta(days=days_ago, minutes=random.randint(10, 300))
                ))

    db.commit()
    return {"message": "Demo data populated successfully for the past 7 days."}
