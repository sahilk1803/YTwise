import json
import re
from typing import Dict, Any, Optional
from app.core.config import settings
from app.models.chat import ChatRequestInput, ChatResponse
from app.models.user import UserProfileModel

class ChatbotService:
    @staticmethod
    def _call_gemini_chat(
        req: ChatRequestInput,
        profile: UserProfileModel,
        budget_context: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Call Gemini API with structured prompt for video evaluation & wellbeing advice."""
        if not settings.GEMINI_API_KEY:
            return None

        try:
            from google import genai
            from google.genai import types

            client = genai.Client(api_key=settings.GEMINI_API_KEY)

            prompt = f"""
You are YouTubeWise AI, a personal learning and digital wellbeing advisor.
The user is considering watching a YouTube video and asked: "{req.question}"

Video Details:
- Title: {req.video_title}
- Channel: {req.channel}
- Category: {req.category}
- Description: {req.description[:1000] if req.description else 'N/A'}
- Transcript Excerpt: {req.transcript_excerpt[:1500] if req.transcript_excerpt else 'N/A'}

User Context:
- Primary Goal: {profile.primary_goal}
- Learning Focus Topics: {', '.join(profile.learning_topics or [])}
- Active Session Intent: {req.user_intent or 'None logged'}
- Category Time Used Today: {budget_context.get('used_min', 0):.1f}m / {budget_context.get('limit_min', 0)}m (Limit for {req.category or 'this category'})
- Remaining Time in Budget: {budget_context.get('remaining_min', 0):.1f}m

Provide a clear, honest, and supportive answer in JSON matching this schema:
{{
  "verdict": "Strongly Recommended" | "Recommended" | "Neutral / Break" | "Off-Goal / Skip",
  "usefulness_score": 88.0,
  "answer": "Clear, concise direct answer to the user's query explaining whether it's worth watching.",
  "key_reason": "One-line specific reason referencing the video's actual content or concepts.",
  "goal_fit_analysis": "Explanation of how this directly supports or hinders their stated goal.",
  "budget_context_note": "Acknowledge their time limit (e.g., 'You have 12 minutes of entertainment budget left today').",
  "suggested_action": "Watch full video | Watch 10 min excerpt | Bookmark for later | Skip to stay on track"
}}
"""
            response = client.models.generate_content(
                model=settings.GEMINI_MODEL,
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    temperature=0.3
                )
            )
            return json.loads(response.text)
        except Exception as e:
            print(f"[ChatbotService] Gemini API chat fallback: {e}")
            return None

    @staticmethod
    def _heuristic_chat(
        req: ChatRequestInput,
        profile: UserProfileModel,
        budget_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Intelligent heuristic response generator when offline / no API key."""
        category = req.category or "Entertainment"
        title = req.video_title.lower()
        channel = (req.channel or "").lower()
        goal = (profile.primary_goal or "").lower()
        question = req.question.lower()

        rem_min = budget_context.get("remaining_min", 30)
        used_min = budget_context.get("used_min", 0)
        limit_min = budget_context.get("limit_min", 60)

        # Check topic overlap
        topics = [t.lower() for t in (profile.learning_topics or [])]
        matched_topics = [t for t in topics if t in title or t in (req.description or "").lower()]

        # Determine verdict & score
        if category in ["Education", "Technology", "Career"] or matched_topics:
            if matched_topics:
                verdict = "Strongly Recommended"
                score = 92.0
                action = "Watch with active note-taking"
                key_reason = f"Directly covers {matched_topics[0]} which is one of your core target learning topics."
                goal_fit = f"Highly aligned with '{profile.primary_goal}'. Helps reinforce theoretical understanding and interview readiness."
            else:
                verdict = "Recommended"
                score = 80.0
                action = "Worth watching for conceptual depth"
                key_reason = f"Provides valuable instructional content on '{req.video_title.split('-')[0].strip()}'."
                goal_fit = f"Good supportive knowledge for your broader engineering and career goals."
        elif category in ["Gaming", "Entertainment", "Vlog", "Music"]:
            if rem_min <= 5:
                verdict = "Off-Goal / Skip"
                score = 25.0
                action = "Skip and switch to your learning goal"
                key_reason = f"This is leisure content and you have only {max(0, round(rem_min))}m remaining in your {category} daily budget."
                goal_fit = f"Does not contribute to your primary goal: '{profile.primary_goal}'."
            else:
                verdict = "Neutral / Break"
                score = 45.0
                action = f"Safe for a quick break ({min(15, max(5, int(rem_min)))}m max)"
                key_reason = f"Pure leisure content from {req.channel or 'creator'}, suitable for intentional downtime."
                goal_fit = f"Non-academic content. Keep viewing brief to preserve focus for '{profile.primary_goal}'."
        else:
            verdict = "Recommended"
            score = 65.0
            action = "Watch at 1.25x speed or skim"
            key_reason = f"General perspective-building content relevant to tech and productivity."
            goal_fit = f"Broadly useful context, though not a direct requirement for '{profile.primary_goal}'."

        # Budget note
        if rem_min <= 0:
            budget_note = f"⚠️ Alert: You have exceeded your daily {category} limit ({used_min:.0f}m / {limit_min}m used)."
        else:
            budget_note = f"⏱️ You have {rem_min:.0f} minutes left for {category} today ({used_min:.0f}m / {limit_min}m used)."

        # Formulate direct answer
        if "worth" in question or "should i" in question:
            if score >= 75:
                answer = f"Yes, this video is worth your time! It offers strong instructional value and supports your preparation for '{profile.primary_goal}'."
            elif score >= 50:
                answer = f"It's decent for general awareness, but if you're in a focused study block, consider bookmarking it for later."
            else:
                answer = f"I'd recommend skipping this right now. It doesn't align with '{profile.primary_goal}' and would eat into your limited daily downtime budget."
        elif "placement" in question or "prep" in question or "exam" in question:
            if score >= 75:
                answer = f"Absolutely! The core concepts in '{req.video_title.split('-')[0].strip()}' frequently appear in technical interviews and assessments."
            else:
                answer = f"Not directly relevant for placement prep. Prioritize your core topics ({', '.join(topics[:3])}) first."
        else:
            answer = f"Based on your profile ('{profile.primary_goal}'), this video scores {score:.0f}/100. Verdict: {verdict}."

        return {
            "verdict": verdict,
            "usefulness_score": score,
            "answer": answer,
            "key_reason": key_reason,
            "goal_fit_analysis": goal_fit,
            "budget_context_note": budget_note,
            "suggested_action": action
        }

    @classmethod
    def evaluate_video(
        cls,
        req: ChatRequestInput,
        profile: UserProfileModel,
        budget_context: Dict[str, Any]
    ) -> ChatResponse:
        """Evaluates video and produces structured AI chatbot advice."""
        ai_res = cls._call_gemini_chat(req, profile, budget_context)
        if not ai_res:
            ai_res = cls._heuristic_chat(req, profile, budget_context)

        return ChatResponse(
            verdict=ai_res.get("verdict", "Recommended"),
            usefulness_score=float(ai_res.get("usefulness_score", 60.0)),
            answer=ai_res.get("answer", "Here is my assessment of the video."),
            key_reason=ai_res.get("key_reason", "Content evaluation based on video metadata."),
            goal_fit_analysis=ai_res.get("goal_fit_analysis", "Evaluated against your profile goals."),
            budget_context_note=ai_res.get("budget_context_note", "Category time tracked."),
            suggested_action=ai_res.get("suggested_action", "Proceed with conscious awareness.")
        )
