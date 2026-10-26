import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health_check():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["status"] == "online"

def test_profile_get_and_update():
    # Test Get Profile
    get_res = client.get("/api/profile?user_id=test_user_1")
    assert get_res.status_code == 200
    data = get_res.json()
    assert data["user_id"] == "test_user_1"
    assert "Education" in data["category_limits"]

    # Test Update Profile
    update_payload = {
        "daily_budget_min": 180,
        "primary_goal": "Master Machine Learning and Python DSA",
        "custom_useful_categories": ["Education", "Technology", "Productivity", "Gaming"],
        "category_limits": {"Gaming": 30, "Entertainment": 15}
    }
    put_res = client.put("/api/profile?user_id=test_user_1", json=update_payload)
    assert put_res.status_code == 200
    put_data = put_res.json()
    assert put_data["daily_budget_min"] == 180
    assert put_data["primary_goal"] == "Master Machine Learning and Python DSA"
    assert "Gaming" in put_data["custom_useful_categories"]
    assert put_data["category_limits"]["Gaming"] == 30

def test_video_classification_and_caching():
    # Educational video classification
    edu_payload = {
        "video_id": "test_edu_123",
        "title": "Dynamic Programming Tutorial for Placement Interviews",
        "channel": "NeetCode",
        "description": "Learn 1D and 2D DP algorithms in Python with step by step LeetCode solutions.",
        "category_tag": "Education",
        "duration_sec": 1200,
        "transcript_text": "Today we will solve the coin change problem using memoization and tabulation.",
        "user_id": "test_user_1",
        "user_intent": "Study DSA algorithms"
    }
    res = client.post("/api/classify", json=edu_payload)
    assert res.status_code == 200
    data = res.json()
    assert data["video_id"] == "test_edu_123"
    assert data["content_type"] in ["Education", "Technology", "Career"]
    assert data["base_value_score"] >= 60.0
    assert data["personalized_score"] >= 60.0
    assert data["is_useful_for_user"] is True
    assert len(data["key_takeaways"]) > 0

    # Test Cache on second call
    res2 = client.post("/api/classify", json=edu_payload)
    assert res2.status_code == 200
    assert res2.json()["cached"] is True

def test_personalized_gaming_video():
    # Test video personalization: user with "Gaming" marked as custom useful
    game_payload = {
        "video_id": "test_game_456",
        "title": "Minecraft Speedrun World Record Breakdown",
        "channel": "SpeedrunKing",
        "description": "Insane strategies and logic breakdown in Minecraft.",
        "category_tag": "Gaming",
        "duration_sec": 900,
        "user_id": "test_user_1"  # test_user_1 has Gaming in custom_useful_categories
    }
    res = client.post("/api/classify", json=game_payload)
    assert res.status_code == 200
    data = res.json()
    assert data["content_type"] == "Gaming"
    assert data["is_useful_for_user"] is True

def test_session_intent_and_watch_tracking():
    # Set Intent
    intent_payload = {
        "user_id": "test_session_user",
        "intent_text": "Study System Design for 1 hour",
        "target_category": "Career",
        "target_minutes": 60
    }
    intent_res = client.post("/api/session/intent", json=intent_payload)
    assert intent_res.status_code == 200
    assert intent_res.json()["success"] is True

    # Record Watch Ticks
    watch_tick_1 = {
        "user_id": "test_session_user",
        "video_id": "vid_sys_design",
        "video_title": "System Design: Microservices vs Monolith",
        "channel": "ByteByteGo",
        "category": "Career",
        "duration_sec": 300  # 5 min
    }
    watch_res_1 = client.post("/api/session/watch", json=watch_tick_1)
    assert watch_res_1.status_code == 200
    assert watch_res_1.json()["category_minutes"]["Career"] >= 5.0

    # Get Active Session Status
    active_res = client.get("/api/session/active?user_id=test_session_user")
    assert active_res.status_code == 200
    active_data = active_res.json()
    assert active_data["current_intent"] == "Study System Design for 1 hour"
    assert active_data["today_total_minutes"] >= 5.0

def test_ai_chatbot_video_evaluation():
    chat_payload = {
        "video_id": "vid_dsa_trees",
        "video_title": "Binary Tree Inversion & BFS/DFS",
        "channel": "Tech Lead",
        "description": "Essential coding interview questions on trees.",
        "category": "Education",
        "question": "Is this video worth watching for my placement preparation?",
        "user_id": "test_session_user",
        "user_intent": "Study for upcoming coding placement"
    }
    res = client.post("/api/chat", json=chat_payload)
    assert res.status_code == 200
    data = res.json()
    assert data["verdict"] in ["Strongly Recommended", "Recommended", "Neutral / Break", "Off-Goal / Skip"]
    assert data["usefulness_score"] > 0
    assert len(data["key_reason"]) > 0
    assert len(data["goal_fit_analysis"]) > 0
    assert len(data["budget_context_note"]) > 0

def test_daily_and_weekly_analytics_and_seed():
    # Seed demo data
    seed_res = client.post("/api/analytics/seed-demo?user_id=demo_analyst")
    assert seed_res.status_code == 200

    # Check daily analytics
    daily_res = client.get("/api/analytics/daily?user_id=demo_analyst")
    assert daily_res.status_code == 200
    daily_data = daily_res.json()
    assert "total_watch_minutes" in daily_data
    assert "productivity_score" in daily_data
    assert "intent_vs_reality_summary" in daily_data
    assert len(daily_data["top_videos"]) > 0

    # Check weekly analytics
    weekly_res = client.get("/api/analytics/weekly?user_id=demo_analyst")
    assert weekly_res.status_code == 200
    weekly_data = weekly_res.json()
    assert len(weekly_data["days"]) == 7
    assert weekly_data["average_daily_minutes"] >= 0
    assert len(weekly_data["top_categories"]) > 0
    assert len(weekly_data["weekly_ai_assessment"]) > 0
