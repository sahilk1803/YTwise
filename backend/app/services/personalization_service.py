import re
from typing import Dict, Any, List
from app.models.user import UserProfileModel
from app.services.classifier_service import score_to_band

class PersonalizationService:
    @staticmethod
    def personalize_score(
        base_classification: Dict[str, Any],
        profile: UserProfileModel,
        current_intent: str = ""
    ) -> Dict[str, Any]:
        """
        Adjusts base classification scores dynamically based on the user's explicit profile,
        primary goal, custom useful categories, learning topics, and current session intent.
        """
        content_type = base_classification.get("content_type", "Other")
        base_score = float(base_classification.get("base_value_score", 50.0))
        breakdown = base_classification.get("score_breakdown", {})
        edu_val = float(breakdown.get("educational_value", 50.0))
        ent_val = float(breakdown.get("entertainment_value", 50.0))
        car_val = float(breakdown.get("career_relevance", 50.0))
        title = base_classification.get("title", "").lower()
        channel = base_classification.get("channel", "").lower()
        summary = base_classification.get("summary", "").lower()

        text_corpus = f"{title} {channel} {summary}"

        # 1. Custom Useful Category Boost / Normalization
        custom_categories = profile.custom_useful_categories or ["Education", "Career", "Technology", "Productivity"]
        is_custom_useful = content_type in custom_categories

        # 2. Check overlap with user's specific learning topics
        learning_topics = [t.lower() for t in (profile.learning_topics or [])]
        topic_matches = [t for t in learning_topics if t in text_corpus]

        # 3. Check overlap with primary goal (e.g. "game development", "DSA", "placement")
        goal_text = (profile.primary_goal or "").lower()
        goal_keywords = [w for w in re.split(r'[\s,()/-]+', goal_text) if len(w) > 2]
        goal_matches = [w for w in goal_keywords if w in text_corpus]

        # 4. Check current session intent
        intent_matches = []
        if current_intent:
            intent_words = [w for w in re.split(r'[\s,()/-]+', current_intent.lower()) if len(w) > 2]
            intent_matches = [w for w in intent_words if w in text_corpus]

        # Calculate Personalized Multipliers & Bonus
        personalized_score = base_score
        personalized_edu = edu_val
        personalized_career = car_val

        # Case: User learning game dev watching gaming or unity content
        if "game dev" in goal_text or "game development" in goal_text or "unity" in goal_text or "unreal" in goal_text:
            if content_type == "Gaming" or "unity" in text_corpus or "unreal" in text_corpus:
                personalized_score = max(personalized_score, 82.0)
                personalized_edu = max(personalized_edu, 85.0)
                personalized_career = max(personalized_career, 80.0)

        # Case: Strong topic / goal match
        if topic_matches or goal_matches:
            match_bonus = min(25.0, len(topic_matches) * 8.0 + len(goal_matches) * 6.0)
            personalized_score = min(100.0, personalized_score + match_bonus)
            personalized_edu = min(100.0, personalized_edu + match_bonus)
            personalized_career = min(100.0, personalized_career + match_bonus * 1.2)

        # Case: Matches active session intent
        if intent_matches:
            personalized_score = min(100.0, personalized_score + 15.0)

        # Case: Category explicitly marked as custom useful by user
        if is_custom_useful and content_type not in ["Education", "Technology", "Career", "Productivity"]:
            personalized_score = min(90.0, personalized_score + 20.0)

        # Case: Video is pure entertainment and user's goal is strict placement / exam
        if not is_custom_useful and content_type in ["Gaming", "Entertainment", "Vlog", "Music"] and not (topic_matches or goal_matches):
            personalized_score = min(35.0, personalized_score * 0.7)
            personalized_career = min(20.0, personalized_career * 0.5)

        personalized_score = round(max(5.0, min(100.0, personalized_score)), 1)
        personalized_edu = round(max(5.0, min(100.0, personalized_edu)), 1)
        personalized_career = round(max(5.0, min(100.0, personalized_career)), 1)

        # Generate Goal Alignment Reasoning
        if personalized_score >= 80:
            if topic_matches or goal_matches:
                matched_items = ", ".join(list(set(topic_matches + goal_matches))[:3])
                reasoning = f"High goal alignment: Directly matches your focus areas ({matched_items})."
            else:
                reasoning = f"High educational & practical value for your '{profile.primary_goal}' goal."
        elif personalized_score >= 60:
            reasoning = f"Moderately aligned with '{profile.primary_goal}'. Good supportive knowledge."
        elif is_custom_useful:
            reasoning = f"Marked as useful per your custom category settings ('{content_type}')."
        else:
            reasoning = f"Low alignment with your stated target: '{profile.primary_goal}'. Best treated as leisure time."

        return {
            "personalized_score": personalized_score,
            "personalized_band": score_to_band(personalized_score),
            "is_useful_for_user": is_custom_useful or personalized_score >= 60,
            "personalized_breakdown": {
                "educational_value": personalized_edu,
                "entertainment_value": ent_val,
                "career_relevance": personalized_career
            },
            "goal_alignment_reasoning": reasoning
        }
