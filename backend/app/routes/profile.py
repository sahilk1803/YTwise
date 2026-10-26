from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.user import UserModel, UserProfileModel, UserProfileSchema, UserProfileUpdate

router = APIRouter(prefix="/profile", tags=["Profile"])

def get_or_create_profile(db: Session, user_id: str = "default_user") -> UserProfileModel:
    profile = db.query(UserProfileModel).filter(UserProfileModel.user_id == user_id).first()
    if not profile:
        user = db.query(UserModel).filter(UserModel.id == user_id).first()
        if not user:
            user = UserModel(id=user_id, email=f"{user_id}@example.com", name="Aditya")
            db.add(user)
            db.commit()

        profile = UserProfileModel(
            user_id=user_id,
            daily_budget_min=120,
            category_limits={
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
            },
            custom_useful_categories=["Education", "Career", "Technology", "Productivity"],
            primary_goal="Placement Preparation (DSA, AI/ML, System Design)",
            learning_topics=["DSA", "Machine Learning", "System Design", "Python", "Web Development"]
        )
        db.add(profile)
        db.commit()
        db.refresh(profile)
    return profile

@router.get("", response_model=UserProfileSchema)
def get_profile(user_id: str = "default_user", db: Session = Depends(get_db)):
    profile = get_or_create_profile(db, user_id)
    return UserProfileSchema(
        user_id=profile.user_id,
        daily_budget_min=profile.daily_budget_min,
        category_limits=profile.category_limits,
        custom_useful_categories=profile.custom_useful_categories,
        primary_goal=profile.primary_goal,
        learning_topics=profile.learning_topics
    )

@router.put("", response_model=UserProfileSchema)
def update_profile(update_data: UserProfileUpdate, user_id: str = "default_user", db: Session = Depends(get_db)):
    profile = get_or_create_profile(db, user_id)

    if update_data.daily_budget_min is not None:
        profile.daily_budget_min = update_data.daily_budget_min
    if update_data.category_limits is not None:
        # Merge or update
        current_limits = dict(profile.category_limits or {})
        current_limits.update(update_data.category_limits)
        profile.category_limits = current_limits
    if update_data.custom_useful_categories is not None:
        profile.custom_useful_categories = update_data.custom_useful_categories
    if update_data.primary_goal is not None:
        profile.primary_goal = update_data.primary_goal
    if update_data.learning_topics is not None:
        profile.learning_topics = update_data.learning_topics

    db.commit()
    db.refresh(profile)

    return UserProfileSchema(
        user_id=profile.user_id,
        daily_budget_min=profile.daily_budget_min,
        category_limits=profile.category_limits,
        custom_useful_categories=profile.custom_useful_categories,
        primary_goal=profile.primary_goal,
        learning_topics=profile.learning_topics
    )
