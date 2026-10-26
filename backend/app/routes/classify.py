from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.video import VideoMetadataInput, VideoClassificationResponse, ScoreBreakdown
from app.services.classifier_service import ClassifierService, score_to_band
from app.services.personalization_service import PersonalizationService
from app.routes.profile import get_or_create_profile

router = APIRouter(prefix="/classify", tags=["Classify"])

@router.post("", response_model=VideoClassificationResponse)
def classify_video_endpoint(
    video_input: VideoMetadataInput,
    db: Session = Depends(get_db)
):
    if not video_input.video_id:
        raise HTTPException(status_code=400, detail="video_id is required")

    # 1. Get base classification (cached or computed)
    base_res = ClassifierService.classify_video(video_input, db)

    # 2. Get user profile for personalization
    user_id = video_input.user_id or "default_user"
    profile = get_or_create_profile(db, user_id)

    # 3. Personalize score
    pers_res = PersonalizationService.personalize_score(
        base_classification=base_res,
        profile=profile,
        current_intent=video_input.user_intent or ""
    )

    base_score = float(base_res.get("base_value_score", 50.0))
    breakdown_data = base_res.get("score_breakdown", {})

    return VideoClassificationResponse(
        video_id=base_res["video_id"],
        title=base_res["title"],
        channel=base_res.get("channel", ""),
        content_type=base_res["content_type"],
        base_value_score=base_score,
        base_value_band=score_to_band(base_score),
        score_breakdown=ScoreBreakdown(
            educational_value=float(breakdown_data.get("educational_value", 50.0)),
            entertainment_value=float(breakdown_data.get("entertainment_value", 50.0)),
            career_relevance=float(breakdown_data.get("career_relevance", 50.0))
        ),
        personalized_score=pers_res["personalized_score"],
        personalized_band=pers_res["personalized_band"],
        is_useful_for_user=pers_res["is_useful_for_user"],
        summary=base_res.get("summary", ""),
        key_takeaways=base_res.get("key_takeaways", []),
        goal_alignment_reasoning=pers_res["goal_alignment_reasoning"],
        cached=base_res.get("cached", False)
    )
