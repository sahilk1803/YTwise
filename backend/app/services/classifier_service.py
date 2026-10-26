import json
import re
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from app.core.config import settings
from app.models.video import (
    VideoMetadataInput,
    VideoClassificationModel,
    VideoClassificationResponse,
    ScoreBreakdown
)

# 11 Standardized Content Types
CONTENT_TYPES = [
    "Education", "Career", "Technology", "News", "Productivity",
    "Entertainment", "Gaming", "Vlog", "Music", "Shorts", "Other"
]

def score_to_band(score: float) -> str:
    if score >= 81:
        return "Highly Useful"
    elif score >= 61:
        return "Useful"
    elif score >= 31:
        return "Moderate"
    else:
        return "Low"

class ClassifierService:
    @staticmethod
    def _call_gemini_classification(title: str, description: str, channel: str, transcript: str) -> Optional[Dict[str, Any]]:
        """Attempt classification via official google-genai SDK if API key configured."""
        if not settings.GEMINI_API_KEY:
            return None
        
        try:
            from google import genai
            from google.genai import types
            
            client = genai.Client(api_key=settings.GEMINI_API_KEY)
            
            prompt = f"""
Analyze this YouTube video metadata and return a JSON object with strict classification.
Title: {title}
Channel: {channel}
Description: {description[:1200]}
Transcript excerpt: {transcript[:2000]}

Allowed Content Types: ["Education", "Career", "Technology", "News", "Productivity", "Entertainment", "Gaming", "Vlog", "Music", "Shorts", "Other"]

Return ONLY a valid JSON object matching this schema:
{{
  "content_type": "Education",
  "base_value_score": 85.0,
  "educational_value": 90.0,
  "entertainment_value": 30.0,
  "career_relevance": 85.0,
  "summary": "Brief 1-2 sentence overview of core concepts covered in the video.",
  "key_takeaways": ["Takeaway 1", "Takeaway 2", "Takeaway 3"],
  "tags": ["algorithm", "dsa", "python"]
}}
"""
            response = client.models.generate_content(
                model=settings.GEMINI_MODEL,
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    temperature=0.2
                )
            )
            data = json.loads(response.text)
            return data
        except Exception as e:
            print(f"[ClassifierService] Gemini API call fallback triggered: {e}")
            return None

    @staticmethod
    def _heuristic_nlp_classify(title: str, description: str, channel: str, transcript: str) -> Dict[str, Any]:
        """High accuracy NLP keyword & pattern matching fallback for offline/local use."""
        text = f"{title} {description} {channel} {transcript}".lower()
        
        # Keyword patterns with weights
        edu_keywords = ["tutorial", "course", "learn", "how to", "explained", "lecture", "dsa", "data structures", 
                        "algorithm", "system design", "physics", "math", "history", "biology", "calculus", "machine learning",
                        "deep learning", "ai", "roadmap", "architecture", "neet", "gate", "jee", "exam", "study with me"]
        career_keywords = ["interview", "placement", "resume", "salary", "faang", "job", "career", "mock interview", 
                           "internship", "hiring", "recruitment", "portfolio", "offer letter", "promotion"]
        tech_keywords = ["coding", "python", "javascript", "react", "fastapi", "golang", "rust", "c++", "sql", "git",
                         "docker", "kubernetes", "aws", "gcp", "azure", "linux", "backend", "frontend", "api", "database",
                         "hardware", "benchmark", "rtx", "cpu", "gpu", "apple", "m4", "tech review"]
        prod_keywords = ["productivity", "time management", "habit", "routine", "focus", "deep work", "notion", 
                         "discipline", "obsidian", "study tips", "mindset", "finance", "investing", "budget"]
        gaming_keywords = ["gameplay", "walkthrough", "let's play", "minecraft", "gta", "valorant", "bgmi", "fps",
                           "stream highlights", "speedrun", "roblox", "fortnite", "elden ring", "ps5", "xbox"]
        vlog_keywords = ["vlog", "day in the life", "travel", "my morning routine", "house tour", "q&a", "what i eat", "mukbang"]
        music_keywords = ["music", "official audio", "lyrics", "song", "remix", "beat", "album", "cover", "soundtrack", "lofi"]
        news_keywords = ["news", "breaking", "politics", "analysis", "geopolitics", "documentary", "report", "crisis"]

        edu_score = sum(3 for w in edu_keywords if re.search(r'\b' + re.escape(w) + r'\b', text))
        career_score = sum(3 for w in career_keywords if re.search(r'\b' + re.escape(w) + r'\b', text))
        tech_score = sum(3 for w in tech_keywords if re.search(r'\b' + re.escape(w) + r'\b', text))
        prod_score = sum(3 for w in prod_keywords if re.search(r'\b' + re.escape(w) + r'\b', text))
        gaming_score = sum(4 for w in gaming_keywords if re.search(r'\b' + re.escape(w) + r'\b', text))
        vlog_score = sum(4 for w in vlog_keywords if re.search(r'\b' + re.escape(w) + r'\b', text))
        music_score = sum(4 for w in music_keywords if re.search(r'\b' + re.escape(w) + r'\b', text))
        news_score = sum(3 for w in news_keywords if re.search(r'\b' + re.escape(w) + r'\b', text))

        scores = {
            "Education": edu_score,
            "Career": career_score,
            "Technology": tech_score,
            "Productivity": prod_score,
            "Gaming": gaming_score,
            "Vlog": vlog_score,
            "Music": music_score,
            "News": news_score
        }

        # Determine dominant category
        max_cat = max(scores, key=scores.get)
        max_val = scores[max_cat]

        if max_val == 0:
            content_type = "Entertainment"
            base_value = 35.0
            edu_val = 20.0
            ent_val = 80.0
            career_rel = 15.0
        elif max_cat in ["Education", "Technology", "Career", "Productivity"]:
            content_type = max_cat
            base_value = min(98.0, 70.0 + max_val * 3.0)
            edu_val = min(98.0, 75.0 + edu_score * 3.0)
            career_rel = min(95.0, 60.0 + career_score * 5.0 + tech_score * 2.0)
            ent_val = max(10.0, 40.0 - max_val * 1.5)
        elif max_cat == "Gaming":
            content_type = "Gaming"
            base_value = 25.0
            edu_val = 15.0
            ent_val = 92.0
            career_rel = 10.0
        elif max_cat == "Music":
            content_type = "Music"
            base_value = 30.0
            edu_val = 10.0
            ent_val = 90.0
            career_rel = 5.0
        elif max_cat == "Vlog":
            content_type = "Vlog"
            base_value = 30.0
            edu_val = 20.0
            ent_val = 85.0
            career_rel = 10.0
        elif max_cat == "News":
            content_type = "News"
            base_value = 60.0
            edu_val = 65.0
            ent_val = 50.0
            career_rel = 40.0
        else:
            content_type = "Entertainment"
            base_value = 40.0
            edu_val = 30.0
            ent_val = 80.0
            career_rel = 20.0

        summary = f"{content_type} content: '{title}' by {channel}."
        if content_type in ["Education", "Technology", "Career"]:
            summary += " Features technical insights, instructional explanations, and practical learning concepts."
            takeaways = [
                f"Core topic coverage related to {title.split('-')[0].split('|')[0].strip()}",
                f"Practical knowledge shared by {channel}",
                "Applicable for skill enhancement and conceptual clarity"
            ]
        elif content_type in ["Gaming", "Entertainment", "Vlog", "Music"]:
            summary += " Focuses on leisure, amusement, and entertainment."
            takeaways = [
                "Recreational viewing and downtime relaxation",
                "Non-academic / general amusement focus",
                "Best consumed within designated leisure limits"
            ]
        else:
            summary += " General informative and perspective-building content."
            takeaways = [
                "General awareness and industry context",
                "Productive insights for daily workflow",
                "Moderate applicability to long-term goals"
            ]

        return {
            "content_type": content_type,
            "base_value_score": round(base_value, 1),
            "educational_value": round(edu_val, 1),
            "entertainment_value": round(ent_val, 1),
            "career_relevance": round(career_rel, 1),
            "summary": summary,
            "key_takeaways": takeaways,
            "tags": [content_type.lower(), channel.lower().replace(" ", "-")]
        }

    @classmethod
    def classify_video(cls, video_data: VideoMetadataInput, db: Session) -> Dict[str, Any]:
        """Classifies video with caching in DB."""
        # Check cache
        cached = db.query(VideoClassificationModel).filter(
            VideoClassificationModel.video_id == video_data.video_id
        ).first()

        if cached:
            return {
                "video_id": cached.video_id,
                "title": cached.title,
                "channel": cached.channel,
                "content_type": cached.content_type,
                "base_value_score": cached.base_value_score,
                "score_breakdown": {
                    "educational_value": cached.educational_value,
                    "entertainment_value": cached.entertainment_value,
                    "career_relevance": cached.career_relevance,
                },
                "summary": cached.summary,
                "key_takeaways": cached.key_takeaways or [],
                "tags": cached.tags or [],
                "cached": True
            }

        # Not in cache: perform classification
        ai_res = cls._call_gemini_classification(
            title=video_data.title,
            description=video_data.description or "",
            channel=video_data.channel or "",
            transcript=video_data.transcript_text or ""
        )

        if not ai_res:
            ai_res = cls._heuristic_nlp_classify(
                title=video_data.title,
                description=video_data.description or "",
                channel=video_data.channel or "",
                transcript=video_data.transcript_text or ""
            )

        # Ensure valid types and defaults
        content_type = ai_res.get("content_type", "Entertainment")
        if content_type not in CONTENT_TYPES:
            content_type = "Other"

        base_val = float(ai_res.get("base_value_score", 50.0))
        edu_val = float(ai_res.get("educational_value", 50.0))
        ent_val = float(ai_res.get("entertainment_value", 50.0))
        car_val = float(ai_res.get("career_relevance", 50.0))
        summary = ai_res.get("summary", f"Classification for {video_data.title}")
        takeaways = ai_res.get("key_takeaways", [])
        tags = ai_res.get("tags", [])

        # Store in DB cache
        new_record = VideoClassificationModel(
            video_id=video_data.video_id,
            title=video_data.title,
            channel=video_data.channel or "",
            description=video_data.description or "",
            content_type=content_type,
            base_value_score=base_val,
            educational_value=edu_val,
            entertainment_value=ent_val,
            career_relevance=car_val,
            summary=summary,
            key_takeaways=takeaways,
            tags=tags,
            cached_at=datetime.now(timezone.utc)
        )
        db.add(new_record)
        db.commit()
        db.refresh(new_record)

        return {
            "video_id": new_record.video_id,
            "title": new_record.title,
            "channel": new_record.channel,
            "content_type": new_record.content_type,
            "base_value_score": new_record.base_value_score,
            "score_breakdown": {
                "educational_value": new_record.educational_value,
                "entertainment_value": new_record.entertainment_value,
                "career_relevance": new_record.career_relevance,
            },
            "summary": new_record.summary,
            "key_takeaways": new_record.key_takeaways or [],
            "tags": new_record.tags or [],
            "cached": False
        }
