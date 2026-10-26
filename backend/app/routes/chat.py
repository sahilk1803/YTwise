from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.chat import ChatRequestInput, ChatResponse
from app.services.chatbot_service import ChatbotService
from app.services.analytics_service import AnalyticsService
from app.routes.profile import get_or_create_profile

router = APIRouter(prefix="/chat", tags=["Chatbot"])

@router.post("", response_model=ChatResponse)
def video_chat_endpoint(
    chat_req: ChatRequestInput,
    db: Session = Depends(get_db)
):
    if not chat_req.question:
        raise HTTPException(status_code=400, detail="Question cannot be empty")

    user_id = chat_req.user_id or "default_user"
    profile = get_or_create_profile(db, user_id)

    # Fetch live session and category budget info
    session_status = AnalyticsService.get_active_session_status(db, user_id, profile)

    category = chat_req.category or "Entertainment"
    used_min = session_status.category_minutes.get(category, 0.0)
    limit_min = session_status.category_limits.get(category, 60)
    remaining_min = max(0.0, limit_min - used_min)

    budget_context = {
        "category": category,
        "used_min": used_min,
        "limit_min": limit_min,
        "remaining_min": remaining_min,
        "today_total_minutes": session_status.today_total_minutes
    }

    # Evaluate question with context
    response = ChatbotService.evaluate_video(chat_req, profile, budget_context)
    return response
