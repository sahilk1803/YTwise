from typing import Dict, Any, List, Optional
from datetime import datetime, timezone, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.session import (
    WatchSessionModel,
    IntentLogModel,
    ActiveSessionStatus,
    DailySummaryResponse,
    WeeklyAnalyticsResponse,
    WeeklyTrendDay
)
from app.models.user import UserProfileModel

class AnalyticsService:
    @staticmethod
    def get_today_str() -> str:
        return datetime.now(timezone.utc).strftime("%Y-%m-%d")

    @classmethod
    def record_watch_tick(
        cls,
        db: Session,
        user_id: str,
        video_id: str,
        video_title: str,
        channel: str,
        category: str,
        duration_sec: int
    ) -> WatchSessionModel:
        """Records active viewing duration tick."""
        today = cls.get_today_str()
        session = WatchSessionModel(
            user_id=user_id,
            video_id=video_id,
            video_title=video_title or "Untitled",
            channel=channel or "",
            category=category or "Other",
            duration_sec=duration_sec,
            session_date=today,
            timestamp=datetime.now(timezone.utc)
        )
        db.add(session)
        db.commit()
        db.refresh(session)
        return session

    @classmethod
    def log_intent(
        cls,
        db: Session,
        user_id: str,
        intent_text: str,
        target_category: Optional[str] = None,
        target_minutes: int = 60
    ) -> IntentLogModel:
        """Logs or updates current session intent."""
        today = cls.get_today_str()
        
        # Deactivate previous active intents for today
        db.query(IntentLogModel).filter(
            IntentLogModel.user_id == user_id,
            IntentLogModel.is_active == 1
        ).update({"is_active": 0, "end_time": datetime.now(timezone.utc)})
        db.commit()

        # Inferred target category if not provided
        if not target_category:
            lower = intent_text.lower()
            if any(w in lower for w in ["dsa", "study", "learn", "course", "lecture", "algorithm", "python", "exam"]):
                target_category = "Education"
            elif any(w in lower for w in ["interview", "placement", "career", "resume", "job"]):
                target_category = "Career"
            elif any(w in lower for w in ["build", "code", "tech", "react", "fastapi", "project"]):
                target_category = "Technology"
            elif any(w in lower for w in ["relax", "game", "gaming"]):
                target_category = "Gaming"
            else:
                target_category = "Education"

        intent = IntentLogModel(
            user_id=user_id,
            intent_text=intent_text,
            target_category=target_category,
            target_minutes=target_minutes or 60,
            session_date=today,
            start_time=datetime.now(timezone.utc),
            is_active=1
        )
        db.add(intent)
        db.commit()
        db.refresh(intent)
        return intent

    @classmethod
    def get_active_session_status(
        cls,
        db: Session,
        user_id: str,
        profile: UserProfileModel
    ) -> ActiveSessionStatus:
        """Returns real-time watch tally, limits, warnings, and productivity."""
        today = cls.get_today_str()

        # Fetch today's watch sessions
        sessions = db.query(
            WatchSessionModel.category,
            func.sum(WatchSessionModel.duration_sec).label("total_sec")
        ).filter(
            WatchSessionModel.user_id == user_id,
            WatchSessionModel.session_date == today
        ).group_by(WatchSessionModel.category).all()

        category_minutes: Dict[str, float] = {}
        total_sec = 0
        for cat, sec in sessions:
            m = round(float(sec or 0) / 60.0, 1)
            category_minutes[cat] = m
            total_sec += (sec or 0)

        today_total_minutes = round(total_sec / 60.0, 1)

        # Active intent
        active_intent = db.query(IntentLogModel).filter(
            IntentLogModel.user_id == user_id,
            IntentLogModel.session_date == today,
            IntentLogModel.is_active == 1
        ).order_by(IntentLogModel.id.desc()).first()

        category_limits = profile.category_limits or {}
        category_usage_pct: Dict[str, float] = {}
        warnings: List[str] = []
        is_any_exceeded = False

        for cat, used_m in category_minutes.items():
            limit_m = category_limits.get(cat, 60)
            pct = round((used_m / max(1, limit_m)) * 100.0, 1)
            category_usage_pct[cat] = pct

            if used_m >= limit_m and cat in ["Entertainment", "Gaming", "Vlog", "Music", "Shorts"]:
                warnings.append(f"Limit reached for {cat}: {used_m:.0f}/{limit_m} min used.")
                is_any_exceeded = True
            elif pct >= 80.0 and cat in ["Entertainment", "Gaming", "Vlog", "Music", "Shorts"]:
                warnings.append(f"Approaching {cat} limit: {used_m:.0f}/{limit_m} min ({pct:.0f}%).")

        # Productivity calculation
        prod_score = cls._calculate_productivity_score(category_minutes, profile.custom_useful_categories)

        return ActiveSessionStatus(
            user_id=user_id,
            current_intent=active_intent.intent_text if active_intent else None,
            target_category=active_intent.target_category if active_intent else "Education",
            target_minutes=active_intent.target_minutes if active_intent else 60,
            today_total_minutes=today_total_minutes,
            category_minutes=category_minutes,
            category_limits=category_limits,
            category_usage_pct=category_usage_pct,
            warnings=warnings,
            is_any_limit_exceeded=is_any_exceeded,
            productivity_score=prod_score
        )

    @classmethod
    def _calculate_productivity_score(
        cls,
        category_minutes: Dict[str, float],
        custom_useful: List[str]
    ) -> float:
        """Calculates 0-100 productivity score based on time distribution and category weights."""
        if not category_minutes:
            return 100.0

        total_m = sum(category_minutes.values())
        if total_m <= 0:
            return 100.0

        weighted_sum = 0.0
        for cat, mins in category_minutes.items():
            if cat in (custom_useful or ["Education", "Career", "Technology", "Productivity"]):
                weight = 1.0
            elif cat in ["News"]:
                weight = 0.6
            elif cat in ["Other"]:
                weight = 0.4
            else:  # Entertainment, Gaming, Vlog, Music, Shorts
                weight = 0.15

            weighted_sum += mins * weight

        score = (weighted_sum / total_m) * 100.0
        return round(max(0.0, min(100.0, score)), 1)

    @classmethod
    def get_daily_summary(
        cls,
        db: Session,
        user_id: str,
        profile: UserProfileModel,
        target_date: Optional[str] = None
    ) -> DailySummaryResponse:
        """Generates comprehensive daily review including Intent vs. Reality analysis."""
        date_str = target_date or cls.get_today_str()

        # Sessions for the day
        sessions = db.query(
            WatchSessionModel.category,
            func.sum(WatchSessionModel.duration_sec).label("total_sec")
        ).filter(
            WatchSessionModel.user_id == user_id,
            WatchSessionModel.session_date == date_str
        ).group_by(WatchSessionModel.category).all()

        category_breakdown: Dict[str, float] = {}
        total_sec = 0
        for cat, sec in sessions:
            m = round(float(sec or 0) / 60.0, 1)
            category_breakdown[cat] = m
            total_sec += (sec or 0)

        total_mins = round(total_sec / 60.0, 1)

        # Top videos watched
        top_vids = db.query(
            WatchSessionModel.video_title,
            WatchSessionModel.category,
            func.sum(WatchSessionModel.duration_sec).label("v_sec")
        ).filter(
            WatchSessionModel.user_id == user_id,
            WatchSessionModel.session_date == date_str
        ).group_by(WatchSessionModel.video_title, WatchSessionModel.category).order_by(
            func.sum(WatchSessionModel.duration_sec).desc()
        ).limit(5).all()

        top_videos_list = [
            {"title": v[0], "category": v[1], "minutes": f"{round(float(v[2] or 0)/60.0, 1)}m"}
            for v in top_vids if v[0]
        ]

        # Intent for the day
        intent = db.query(IntentLogModel).filter(
            IntentLogModel.user_id == user_id,
            IntentLogModel.session_date == date_str
        ).order_by(IntentLogModel.id.desc()).first()

        intent_text = intent.intent_text if intent else None
        target_cat = intent.target_category if intent else "Education"

        # Intent vs Reality Match Calculation
        if total_mins > 0:
            target_mins = category_breakdown.get(target_cat, 0.0)
            useful_categories = profile.custom_useful_categories or ["Education", "Career", "Technology", "Productivity"]
            total_useful_mins = sum(mins for cat, mins in category_breakdown.items() if cat in useful_categories)
            
            # Primary weight on intended category, secondary on general useful categories
            match_pct = round(((target_mins * 0.7 + total_useful_mins * 0.3) / total_mins) * 100.0, 1)
            match_pct = max(0.0, min(100.0, match_pct))
        else:
            match_pct = 100.0

        # Natural language Intent vs Reality summary
        if intent_text and total_mins > 0:
            ent_mins = sum(mins for cat, mins in category_breakdown.items() if cat in ["Entertainment", "Gaming", "Vlog", "Music", "Shorts"])
            ent_pct = round((ent_mins / total_mins) * 100.0)
            target_time = category_breakdown.get(target_cat, 0.0)

            if match_pct >= 80:
                summary_text = f"🎯 Excellent discipline! You intended to '{intent_text}' and achieved {match_pct:.0f}% goal alignment with {target_time:.0f}m spent on {target_cat}."
                tip = "Keep this momentum going! You're consistently protecting your high-focus learning hours."
            elif match_pct >= 50:
                summary_text = f"⚖️ Moderate alignment: You intended to '{intent_text}'. You spent {target_time:.0f}m on {target_cat}, but drifted {ent_pct}% of the time into leisure content."
                tip = "Consider activating the extension's HUD warning modal to catch tab-switching early."
            else:
                summary_text = f"⚠️ Goal Discrepancy: You intended to '{intent_text}', but {ent_pct}% of your {total_mins:.0f} minutes was spent on non-goal entertainment."
                tip = "Try setting a 25-minute Pomodoro timer before opening YouTube to anchor your learning session."
        elif total_mins > 0:
            useful_mins = sum(mins for cat, mins in category_breakdown.items() if cat in (profile.custom_useful_categories or []))
            prod_pct = round((useful_mins / total_mins) * 100.0)
            summary_text = f"You watched {total_mins:.0f} minutes total today across all categories ({prod_pct}% productive)."
            tip = "Log an intent goal before your next session to unlock real-time goal tracking!"
        else:
            summary_text = "No watch activity recorded yet today."
            tip = "Open YouTube and start learning to track your progress in real time!"

        prod_score = cls._calculate_productivity_score(category_breakdown, profile.custom_useful_categories)

        return DailySummaryResponse(
            date=date_str,
            total_watch_minutes=total_mins,
            category_breakdown=category_breakdown,
            category_limits=profile.category_limits or {},
            productivity_score=prod_score,
            current_intent=intent_text,
            intent_match_pct=match_pct,
            intent_vs_reality_summary=summary_text,
            ai_wellness_tip=tip,
            top_videos=top_videos_list
        )

    @classmethod
    def get_weekly_analytics(
        cls,
        db: Session,
        user_id: str,
        profile: UserProfileModel
    ) -> WeeklyAnalyticsResponse:
        """Returns 7-day stacked category distribution, top topics, and weekly assessment."""
        today = datetime.now(timezone.utc).date()
        days_list: List[WeeklyTrendDay] = []
        all_categories_tally: Dict[str, float] = {}
        all_channels_tally: Dict[str, float] = {}
        total_week_mins = 0.0
        total_week_prod = 0.0
        total_week_intent = 0.0

        for i in range(6, -1, -1):
            day_date = today - timedelta(days=i)
            day_str = day_date.strftime("%Y-%m-%d")
            day_name = day_date.strftime("%a")

            # Sessions for day
            sessions = db.query(
                WatchSessionModel.category,
                WatchSessionModel.channel,
                func.sum(WatchSessionModel.duration_sec).label("total_sec")
            ).filter(
                WatchSessionModel.user_id == user_id,
                WatchSessionModel.session_date == day_str
            ).group_by(WatchSessionModel.category, WatchSessionModel.channel).all()

            cat_day: Dict[str, float] = {}
            day_sec = 0
            for cat, ch, sec in sessions:
                m = round(float(sec or 0) / 60.0, 1)
                cat_day[cat] = cat_day.get(cat, 0.0) + m
                day_sec += (sec or 0)
                all_categories_tally[cat] = all_categories_tally.get(cat, 0.0) + m
                if ch:
                    all_channels_tally[ch] = all_channels_tally.get(ch, 0.0) + m

            day_mins = round(day_sec / 60.0, 1)
            prod_score = cls._calculate_productivity_score(cat_day, profile.custom_useful_categories)

            # Intent for day
            intent = db.query(IntentLogModel).filter(
                IntentLogModel.user_id == user_id,
                IntentLogModel.session_date == day_str
            ).first()

            if day_mins > 0 and intent:
                target_m = cat_day.get(intent.target_category or "Education", 0.0)
                match_pct = round((target_m / day_mins) * 100.0, 1)
            elif day_mins > 0:
                match_pct = prod_score
            else:
                match_pct = 100.0

            days_list.append(WeeklyTrendDay(
                date=day_str,
                day_name=day_name,
                total_minutes=day_mins,
                productivity_score=prod_score,
                category_breakdown=cat_day,
                intent_match_pct=match_pct
            ))

            total_week_mins += day_mins
            total_week_prod += prod_score
            total_week_intent += match_pct

        avg_daily_mins = round(total_week_mins / 7.0, 1)
        avg_prod = round(total_week_prod / 7.0, 1)
        avg_intent = round(total_week_intent / 7.0, 1)

        # Ranked categories & channels
        sorted_cats = [{"category": k, "minutes": round(v, 1)} for k, v in sorted(all_categories_tally.items(), key=lambda x: x[1], reverse=True)]
        sorted_chs = [{"channel": k, "minutes": round(v, 1)} for k, v in sorted(all_channels_tally.items(), key=lambda x: x[1], reverse=True)[:5]]

        if avg_prod >= 75:
            assessment = "🌟 Outstanding weekly performance! You maintained high discipline with strong focus on Educational & Career topics."
        elif avg_prod >= 50:
            assessment = "📈 Solid consistency, with room for improvement in curbing late-evening entertainment drift."
        else:
            assessment = "⚡ High leisure drift detected this week. Try tightening your category limits on Gaming & Entertainment."

        return WeeklyAnalyticsResponse(
            days=days_list,
            average_daily_minutes=avg_daily_mins,
            average_productivity_score=avg_prod,
            top_categories=sorted_cats,
            top_channels=sorted_chs,
            overall_intent_match_avg=avg_intent,
            weekly_ai_assessment=assessment
        )
