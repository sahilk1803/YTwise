# Chrome Web Store Listing — YouTubeWise

## 1. Store Metadata

- **Name:** YouTubeWise — AI YouTube Content Intelligence & Digital Wellbeing
- **Summary:** AI-powered YouTube content classification, personalized usefulness scoring, intent tracking, and wellbeing limits.
- **Category:** Productivity / Workflow & Planning
- **Default Language:** English

## 2. Detailed Description

YouTubeWise is your intelligent companion for conscious and goal-aligned YouTube viewing. Unlike blunt blockers that blindly shut down access, YouTubeWise uses natural language understanding to assess the video you are currently watching, calculate a personalized usefulness score based on your learning goals, and help you track your intent versus reality in real time.

### Key Features:
- 🧠 **Real-Time Video Intelligence:** Automatically classifies YouTube videos across 11 categories (Education, Career, Technology, Productivity, Gaming, etc.) and scores content usefulness from 0 to 100.
- 🎯 **Personalized Scoring:** Scores adapt to your personal goals (e.g. an AI development video scores high educational value for an engineering student).
- ⏱️ **Category Budget Limits:** Set daily allowances for leisure content and receive gentle, dismissible warnings when limits are approached.
- ⚖️ **Intent vs. Reality Tracking:** Set a focus goal for your session and visualize how your actual viewing compares against your intentions.
- 💬 **AI Advisor Chatbot:** Ask "Should I watch this for placement prep?" or "Summarize key concepts" in the side panel for instant reasoned advice.
- 📊 **Productivity Analytics Dashboard:** Review daily breakdown doughnuts, 7-day weekly stacked category trends, and topic rankings.

---

## 3. Permissions Justification

| Permission | Justification |
|---|---|
| `storage` | Required to cache video classifications locally, store user daily budgets, and track session watch duration without loss across browser restarts. |
| `alarms` | Required to schedule periodic wellbeing check-ins and session interval checks. |
| `notifications` | Required to notify users when they approach or exceed their user-defined category time limits. |
| `sidePanel` | Required to host the YouTubeWise AI companion alongside the active YouTube video. |
| `tabs` | Required to detect the active YouTube video tab URL and title to trigger intelligence classification. |
| `host_permissions: https://www.youtube.com/*` | Required to extract video metadata and inject the non-intrusive in-video usefulness HUD. |
| `host_permissions: http://localhost:8000/*` | Required to communicate with the local YouTubeWise AI classification and analytics backend API. |

---

## 4. Privacy & Data Use

- **Data Collected:** YouTube video metadata (title, channel, public transcript excerpt) and watch duration per category.
- **Data Sharing:** No personal data is sold or shared with third parties. All classification is processed through the user's configured backend API.
