# YouTubeWise 🧠
### AI-Powered YouTube Content Intelligence & Digital Wellbeing System

YouTubeWise is a complete, production-grade system comprising a **Chrome/Edge Extension (Manifest V3)**, a **FastAPI AI Backend**, and a **React + Vite Analytics Dashboard**.

Unlike generic screen-time blockers, YouTubeWise understands **video content** using NLP/LLM classification, computes **personalized usefulness scores** tailored to your learning goals, measures **intent vs. actual behavior**, and provides an **in-context AI Advisor chatbot** to help you make conscious viewing choices in real time.

---

## 🌟 Key Features

1. **In-Video Content Intelligence (Extension HUD)**
   - Automatically detects YouTube video changes without page reloads (SPA navigation support).
   - Classifies videos across **11 content types**: `Education`, `Career`, `Technology`, `Productivity`, `Entertainment`, `Gaming`, `Vlog`, `Music`, `News`, `Shorts`, `Other`.
   - Computes a **Personalized Value Score (0–100)** with ratings (*Low*, *Moderate*, *Useful*, *Highly Useful*).
   - Injects a sleek floating HUD pill directly on YouTube with score breakdown (Educational, Career Relevance, Entertainment).

2. **Personalized Relevance Engine**
   - Videos are dynamically evaluated based on your primary goals (e.g. a game development tutorial scores high educational value for a game-dev student).
   - Supports user-defined custom categories marked as productive.

3. **Digital Wellbeing & Dismissible Interventions**
   - Active watch time tracker monitoring only when videos are playing.
   - Real-time category budget meters (e.g. *20m daily entertainment limit*).
   - Non-intrusive warning alert when approaching threshold (80%).
   - Dismissible intervention modal on limit exceeded with quick redirection to learning topics.

4. **Conversational AI Advisor Chatbot**
   - Integrated into the Chrome Side Panel companion.
   - Natural language queries: *"Should I watch this for placement prep?"*, *"Summarize key concepts"*, *"Check remaining budget"*.
   - Returns structured verdict (*Strongly Recommended*, *Neutral*, *Off-Goal / Skip*), justification referencing content, and contextual budget awareness.

5. **Intent vs. Reality Analytics Engine**
   - Log a session focus goal (e.g. *"Study DSA for 1 hour"*).
   - Compares your stated intent against actual watch distribution to compute an **Intent Alignment Match %**.
   - Generates plain-language behavioral summaries and actionable AI productivity tips.

6. **Full-Featured Analytics Dashboard (React + Vite)**
   - Category time allocation Doughnut chart.
   - 7-Day Stacked Bar Chart for habit trends.
   - Top watched videos & creators ranking.
   - Goal customizer modal to edit budgets, topics, and productive category definitions.
   - 1-click **"Load Demo Data"** feature for instant rich demonstrations.

---

## 🏗️ System Architecture

```
                                 ┌──────────────────────────────────────────────┐
                                 │              YouTube Browser Tab             │
                                 │   (YouTube Video DOM + SPA Navigation)      │
                                 └──────────────────────┬───────────────────────┘
                                                        │ Metadata & Watch Events
                                                        ▼
┌────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                   Chrome Extension (Manifest V3)                                       │
│                                                                                                        │
│  ┌─────────────────────────────┐   ┌─────────────────────────────┐   ┌──────────────────────────────┐  │
│  │   Content Script            │   │  Background Service Worker  │   │  Popup & Side Panel UI       │  │
│  │  - DOM Metadata Extractor   │◄──┤  - Active watch aggregator  │◄──┤  - Real-time Value Card      │  │
│  │  - SPA URL Change Observer  │   │  - Storage state manager    │   │  - Intent Quick Logger       │  │
│  │  - Non-intrusive Overlay HUD│   │  - Budget limit tracker     │   │  - AI Chatbot Assistant      │  │
│  │  - Soft Warning/Nudge Modal │   │  - Notification dispatcher  │   │  - Category Time Meters      │  │
│  └─────────────────────────────┘   └──────────────┬──────────────┘   └──────────────────────────────┘  │
└───────────────────────────────────────────────────┼────────────────────────────────────────────────────┘
                                                    │ REST API
                                                    ▼
┌────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                   FastAPI AI Backend (Python)                                          │
│                                                                                                        │
│  ┌─────────────────────────────┐   ┌─────────────────────────────┐   ┌──────────────────────────────┐  │
│  │   Classification Service    │   │   Personalization Engine    │   │   Analytics & Intent Engine  │  │
│  │  - Dual-mode: Gemini / NLP  │   │  - Goal-aligned scoring     │   │  - Intent vs Reality gap     │  │
│  │  - Base Value Score (0-100) │   │  - Custom categories        │   │  - Productivity scoring      │  │
│  │  - SQLite Cache by Video ID │   │  - Value breakdown (Edu/Ent)│   │  - Daily / Weekly summary    │  │
│  └─────────────────────────────┘   └─────────────────────────────┘   └──────────────────────────────┘  │
└───────────────────────────────────────────────────┬────────────────────────────────────────────────────┘
                                                    │
                                                    ▼
┌────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│                              React + Vite Analytics Dashboard UI                                       │
│                                                                                                        │
│  ┌─────────────────────────────┐   ┌─────────────────────────────┐   ┌──────────────────────────────┐  │
│  │   Daily Time & Limit Meters │   │   Weekly Breakdown Charts   │   │   Intent vs Reality Insights │  │
│  │  - Category Doughnut Chart  │   │  - Stacked Bar Charts       │   │  - Gap analysis & AI advice  │  │
│  │  - Real-time limit progress │   │  - Top topic / channel rank │   │  - Goal & Category settings  │  │
│  └─────────────────────────────┘   └─────────────────────────────┘   └──────────────────────────────┘  │
└────────────────────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 🚀 Quickstart & Setup Guide

### 1. Start the FastAPI Backend

```bash
# Navigate to backend directory
cd backend

# Activate virtual environment
# Windows:
.\venv\Scripts\activate

# Run FastAPI server with Uvicorn
uvicorn app.main:app --reload --port 8000
```
Backend API will be accessible at `http://localhost:8000` with interactive docs at `http://localhost:8000/docs`.

*(Optional)* To use live Gemini LLM generation, set your API key in `backend/.env`:
```env
GEMINI_API_KEY=your_gemini_api_key_here
GEMINI_MODEL=gemini-2.5-flash
```
*Note: If no API key is provided, the backend seamlessly runs with its built-in zero-shot NLP heuristics engine.*

---

### 2. Start the Analytics Dashboard

```bash
# In a separate terminal, navigate to frontend directory
cd frontend

# Install dependencies (if not already installed)
npm install

# Start Vite development server
npm run dev
```
Dashboard will open at `http://localhost:5173`.

---

### 3. Load the Chrome/Edge Extension

1. Open **Google Chrome** or **Microsoft Edge**.
2. Navigate to `chrome://extensions` (or `edge://extensions`).
3. Enable **Developer mode** toggle in the top-right corner.
4. Click **Load unpacked**.
5. Select the `extension/` directory (`C:\Users\dell7\.gemini\antigravity\scratch\youtubewise\extension`).
6. Navigate to [YouTube](https://www.youtube.com) and click any video to see the YouTubeWise floating HUD pill, popup, and side panel companion!

---

## 🧪 Running Automated Tests

Run the complete backend test suite:
```bash
cd backend
.\venv\Scripts\python -m pytest tests/test_api.py -v
```

---

## 📁 Repository Structure

```
youtubewise/
├── backend/
│   ├── app/
│   │   ├── core/           # Config & SQLite database setup
│   │   ├── models/         # User, Video, Session, Chat models & schemas
│   │   ├── routes/         # Classify, Chat, Session, Analytics, Profile endpoints
│   │   ├── services/       # AI Classifier, Personalization, Chatbot, Analytics
│   │   └── main.py         # FastAPI application entry point
│   ├── tests/
│   │   └── test_api.py     # Comprehensive automated test suite
│   ├── requirements.txt    # Python dependencies
│   └── .env.example
├── extension/
│   ├── manifest.json       # Manifest V3 configuration
│   ├── background/         # Background service worker (state, alarms, API sync)
│   ├── content/            # DOM metadata extraction, in-page HUD, watch tracking
│   ├── popup/              # Quick glance popup UI
│   ├── sidepanel/          # AI companion with chat, intelligence & settings tabs
│   ├── icons/              # Valid PNG icons (16, 48, 128)
│   └── CHROMEWEBSTORE.md   # Chrome Web Store listing & permissions justification
├── frontend/
│   ├── src/
│   │   ├── components/     # DailyOverview, WeeklyTrend, IntentRealityCard, etc.
│   │   ├── services/       # Backend API client
│   │   ├── styles/         # Modern responsive dark theme CSS
│   │   └── App.jsx         # Main dashboard layout
│   └── package.json        # Frontend React & Chart.js dependencies
└── README.md
```
#   Y T w i s e  
 