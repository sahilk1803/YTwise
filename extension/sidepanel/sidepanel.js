document.addEventListener("DOMContentLoaded", async () => {
  // Navigation Tabs
  const tabs = document.querySelectorAll(".sp-tab");
  const tabContents = document.querySelectorAll(".sp-tab-content");

  tabs.forEach((tab) => {
    tab.addEventListener("click", () => {
      tabs.forEach((t) => t.classList.remove("active"));
      tabContents.forEach((c) => c.classList.remove("active"));

      tab.classList.add("active");
      const targetId = tab.getAttribute("data-tab");
      document.getElementById(targetId)?.classList.add("active");
    });
  });

  // Intelligence Elements
  const catTag = document.getElementById("sp-cat-tag");
  const bandTag = document.getElementById("sp-band-tag");
  const videoTitle = document.getElementById("sp-video-title");
  const videoChannel = document.getElementById("sp-video-channel");
  const scoreNum = document.getElementById("sp-score-num");
  const eduVal = document.getElementById("sp-edu-val");
  const carVal = document.getElementById("sp-car-val");
  const entVal = document.getElementById("sp-ent-val");
  const alignmentText = document.getElementById("sp-alignment-text");
  const takeawaysList = document.getElementById("sp-takeaways-list");

  // Chat Elements
  const chatMessages = document.getElementById("chat-messages");
  const chatInput = document.getElementById("chat-input");
  const sendChatBtn = document.getElementById("send-chat-btn");
  const chipButtons = document.querySelectorAll(".chip-btn");

  // Wellbeing Elements
  const intentInput = document.getElementById("sp-intent-input");
  const setIntentBtn = document.getElementById("sp-set-intent-btn");
  const currentIntentDisplay = document.getElementById("sp-current-intent-display");
  const totalTimePill = document.getElementById("sp-total-time-pill");
  const metersList = document.getElementById("sp-meters-list");

  // Settings Elements
  const primaryGoalInput = document.getElementById("goal-primary-input");
  const topicsInput = document.getElementById("goal-topics-input");
  const budgetInput = document.getElementById("goal-budget-input");
  const entLimitInput = document.getElementById("goal-ent-limit-input");
  const saveGoalsBtn = document.getElementById("save-goals-btn");
  const saveGoalsStatus = document.getElementById("save-goals-status");

  let activeClassification = null;

  // Load video intelligence
  async function refreshIntelligence() {
    const { lastClassification } = await chrome.storage.local.get("lastClassification");
    if (lastClassification) {
      activeClassification = lastClassification;
      const score = Math.round(lastClassification.personalized_score || lastClassification.base_value_score || 50);
      const category = lastClassification.content_type || "Other";
      const band = lastClassification.personalized_band || "Moderate";

      catTag.textContent = category;
      bandTag.textContent = band;
      videoTitle.textContent = lastClassification.title || "YouTube Video";
      videoChannel.textContent = lastClassification.channel || "Creator";
      scoreNum.textContent = score;

      const breakdown = lastClassification.score_breakdown || {};
      eduVal.textContent = `${Math.round(breakdown.educational_value || 50)}%`;
      carVal.textContent = `${Math.round(breakdown.career_relevance || 50)}%`;
      entVal.textContent = `${Math.round(breakdown.entertainment_value || 50)}%`;

      if (lastClassification.goal_alignment_reasoning) {
        alignmentText.textContent = lastClassification.goal_alignment_reasoning;
      }

      if (lastClassification.key_takeaways && lastClassification.key_takeaways.length > 0) {
        takeawaysList.innerHTML = lastClassification.key_takeaways.map((t) => `<li>${t}</li>`).join("");
      }
    }
  }

  // Load wellbeing session data
  async function refreshWellbeing() {
    chrome.runtime.sendMessage({ type: "GET_ACTIVE_SESSION" }, (res) => {
      if (res?.success && res.data) {
        const data = res.data;
        totalTimePill.textContent = `${data.today_total_minutes.toFixed(0)}m Total Today`;

        if (data.current_intent) {
          currentIntentDisplay.innerHTML = `Active: <strong>${data.current_intent}</strong>`;
        }

        metersList.innerHTML = "";
        const trackedCategories = ["Education", "Career", "Technology", "Productivity", "Entertainment", "Gaming", "Vlog"];
        
        trackedCategories.forEach((cat) => {
          const used = data.category_minutes[cat] || 0;
          const limit = data.category_limits[cat] || 60;
          const pct = Math.min(100, Math.round((used / limit) * 100));

          let barColor = "#6366F1";
          if (["Entertainment", "Gaming", "Vlog"].includes(cat)) {
            barColor = pct >= 100 ? "#EF4444" : pct >= 80 ? "#F59E0B" : "#38BDF8";
          } else {
            barColor = "#10B981";
          }

          const meter = document.createElement("div");
          meter.className = "sp-meter-row";
          meter.innerHTML = `
            <div class="sp-meter-header">
              <span>${cat}</span>
              <span style="color: ${pct >= 100 ? '#EF4444' : '#94A3B8'}">${used.toFixed(0)} / ${limit}m (${pct}%)</span>
            </div>
            <div class="sp-track">
              <div class="sp-bar" style="width: ${pct}%; background-color: ${barColor};"></div>
            </div>
          `;
          metersList.appendChild(meter);
        });
      }
    });
  }

  // Load Profile Settings
  async function refreshProfile() {
    chrome.runtime.sendMessage({ type: "GET_PROFILE" }, (res) => {
      if (res?.success && res.data) {
        const p = res.data;
        primaryGoalInput.value = p.primary_goal || "";
        topicsInput.value = (p.learning_topics || []).join(", ");
        budgetInput.value = p.daily_budget_min || 120;
        entLimitInput.value = p.category_limits?.Entertainment || 25;
      }
    });
  }

  // AI Chat Handler
  async function handleSendChat(queryText) {
    const text = queryText || chatInput.value.trim();
    if (!text) return;

    chatInput.value = "";

    // Append user bubble
    const userBubble = document.createElement("div");
    userBubble.className = "chat-bubble user-bubble";
    userBubble.textContent = text;
    chatMessages.appendChild(userBubble);
    chatMessages.scrollTop = chatMessages.scrollHeight;

    // Append loading bot bubble
    const botBubble = document.createElement("div");
    botBubble.className = "chat-bubble bot-bubble";
    botBubble.innerHTML = `<span style="color: #94A3B8;">Thinking...</span>`;
    chatMessages.appendChild(botBubble);
    chatMessages.scrollTop = chatMessages.scrollHeight;

    const payload = {
      video_id: activeClassification?.video_id || "active_video",
      video_title: activeClassification?.title || "Current YouTube Video",
      channel: activeClassification?.channel || "",
      category: activeClassification?.content_type || "Entertainment",
      description: activeClassification?.summary || "",
      question: text
    };

    chrome.runtime.sendMessage({
      type: "ASK_CHATBOT",
      data: payload
    }, (res) => {
      if (res?.success && res.data) {
        const resp = res.data;
        let verdictClass = "verdict-recommended";
        if (resp.verdict.includes("Skip") || resp.verdict.includes("Off-Goal")) {
          verdictClass = "verdict-skip";
        } else if (resp.verdict.includes("Neutral") || resp.verdict.includes("Break")) {
          verdictClass = "verdict-neutral";
        }

        botBubble.innerHTML = `
          <div class="bubble-header" style="display: flex; justify-content: space-between; align-items: center;">
            <span class="bot-name">🧠 YouTubeWise AI</span>
            <span class="verdict-tag ${verdictClass}">${resp.verdict} (${resp.usefulness_score.toFixed(0)}/100)</span>
          </div>
          <p style="margin: 4px 0;">${resp.answer}</p>
          <div style="font-size: 11px; color: #94A3B8; border-top: 1px solid rgba(255,255,255,0.08); padding-top: 4px;">
            <strong>Reason:</strong> ${resp.key_reason}<br/>
            <strong>Goal Fit:</strong> ${resp.goal_fit_analysis}<br/>
            <strong>Budget:</strong> ${resp.budget_context_note}
          </div>
        `;
      } else {
        botBubble.innerHTML = `<span style="color: #EF4444;">Failed to get AI assessment. Check backend connection.</span>`;
      }
      chatMessages.scrollTop = chatMessages.scrollHeight;
    });
  }

  // Event Listeners
  sendChatBtn.addEventListener("click", () => handleSendChat());
  chatInput.addEventListener("keydown", (e) => {
    if (e.key === "Enter") handleSendChat();
  });

  chipButtons.forEach((chip) => {
    chip.addEventListener("click", () => {
      const q = chip.getAttribute("data-query");
      handleSendChat(q);
    });
  });

  // Intent Update
  setIntentBtn.addEventListener("click", () => {
    const text = intentInput.value.trim();
    if (!text) return;

    chrome.runtime.sendMessage({
      type: "LOG_INTENT",
      data: { intent_text: text }
    }, (res) => {
      if (res?.success) {
        currentIntentDisplay.innerHTML = `Active: <strong>${text}</strong>`;
        intentInput.value = "";
        setIntentBtn.textContent = "Saved!";
        setTimeout(() => { setIntentBtn.textContent = "Update Intent"; }, 1500);
      }
    });
  });

  // Save Goals & Profile Settings
  saveGoalsBtn.addEventListener("click", async () => {
    const primaryGoal = primaryGoalInput.value.trim();
    const topics = topicsInput.value.split(",").map((t) => t.trim()).filter(Boolean);
    const dailyBudget = parseInt(budgetInput.value) || 120;
    const entLimit = parseInt(entLimitInput.value) || 25;

    try {
      const res = await fetch("http://localhost:8000/api/profile", {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          primary_goal: primaryGoal,
          learning_topics: topics,
          daily_budget_min: dailyBudget,
          category_limits: { Entertainment: entLimit }
        })
      });

      if (res.ok) {
        saveGoalsStatus.textContent = "✅ Settings updated!";
        setTimeout(() => { saveGoalsStatus.textContent = ""; }, 2500);
        refreshWellbeing();
      }
    } catch (err) {
      saveGoalsStatus.textContent = "❌ Error saving settings.";
    }
  });

  // Open Dashboard link
  document.getElementById("open-dashboard-top")?.addEventListener("click", () => {
    chrome.tabs.create({ url: "http://localhost:5173" });
  });

  // Initial load
  await refreshIntelligence();
  await refreshWellbeing();
  await refreshProfile();
});
