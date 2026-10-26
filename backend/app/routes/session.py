from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.session import WatchEventInput, IntentInput, ActiveSessionStatus
from app.services.analytics_service import AnalyticsService
from app.routes.profile import get_or_create_profile

router = APIRouter(prefix="/session", tags=["Session"])

@router.post("/intent")
def set_intent_endpoint(
    intent_input: IntentInput,
    db: Session = Depends(get_db)
):
    if not intent_input.intent_text.strip():
        raise HTTPException(status_code=400, detail="Intent text cannot be empty")

    user_id = intent_input.user_id or "default_user"
    intent = AnalyticsService.log_intent(
        db=db,
        user_id=user_id,
        intent_text=intent_input.intent_text,
        target_category=intent_input.target_category,
        target_minutes=intent_input.target_minutes or 60
    )
    return {
        "success": True,
        "intent_id": intent.id,
        "intent_text": intent.intent_text,
        "target_category": intent.target_category,
        "target_minutes": intent.target_minutes
    }

@router.post("/watch")
def record_watch_endpoint(
    watch_event: WatchEventInput,
    db: Session = Depends(get_db)
):
    user_id = watch_event.user_id or "default_user"
    session = AnalyticsService.record_watch_tick(
        db=db,
        user_id=user_id,
        video_id=watch_event.video_id,
        video_title=watch_event.video_title or "Untitled Video",
        channel=watch_event.channel or "",
        category=watch_event.category,
        duration_sec=watch_event.duration_sec
    )
    
    profile = get_or_create_profile(db, user_id)
    status = AnalyticsService.get_active_session_status(db, user_id, profile)
    
    return {
        "success": True,
        "recorded_sec": session.duration_sec,
        "category": session.category,
        "today_total_minutes": status.today_total_minutes,
        "category_minutes": status.category_minutes,
        "warnings": status.warnings,
        "is_any_limit_exceeded": status.is_any_limit_exceeded
    }

@router.get("/active", response_model=ActiveSessionStatus)
def get_active_session_endpoint(
    user_id: str = "default_user",
    db: Session = Depends(get_db)
):
    profile = get_or_create_profile(db, user_id)
    return AnalyticsService.get_active_session_status(db, user_id, profile)
