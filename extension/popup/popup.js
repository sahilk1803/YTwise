document.addEventListener("DOMContentLoaded", async () => {
  // Elements
  const videoCategoryEl = document.getElementById("video-category");
  const scorePillEl = document.getElementById("score-pill");
  const videoTitleEl = document.getElementById("video-title");
  const videoChannelEl = document.getElementById("video-channel");
  const breakdownGridEl = document.getElementById("breakdown-grid");
  const eduValEl = document.getElementById("edu-val");
  const carValEl = document.getElementById("car-val");
  const entValEl = document.getElementById("ent-val");
  const eduBarEl = document.getElementById("edu-bar");
  const carBarEl = document.getElementById("car-bar");
  const entBarEl = document.getElementById("ent-bar");
  const alignmentReasonEl = document.getElementById("alignment-reason");
  const intentInputEl = document.getElementById("intent-input");
  const setIntentBtn = document.getElementById("set-intent-btn");
  const activeIntentText = document.getElementById("active-intent-text");
  const totalWatchText = document.getElementById("total-watch-text");
  const budgetMetersEl = document.getElementById("budget-meters");
  const openSidepanelBtn = document.getElementById("open-sidepanel-btn");
  const openDashboardBtn = document.getElementById("open-dashboard-btn");

  // Load last cached video classification
  const { lastClassification } = await chrome.storage.local.get("lastClassification");

  if (lastClassification) {
    const score = Math.round(lastClassification.personalized_score || lastClassification.base_value_score || 50);
    videoCategoryEl.textContent = lastClassification.content_type || "Other";
    scorePillEl.textContent = `${score}/100`;

    if (score >= 70) {
      scorePillEl.style.backgroundColor = "rgba(16, 185, 129, 0.2)";
      scorePillEl.style.color = "#10B981";
    } else if (score < 40) {
      scorePillEl.style.backgroundColor = "rgba(239, 68, 68, 0.2)";
      scorePillEl.style.color = "#EF4444";
    } else {
      scorePillEl.style.backgroundColor = "rgba(245, 158, 11, 0.2)";
      scorePillEl.style.color = "#F59E0B";
    }

    videoTitleEl.textContent = lastClassification.title || "YouTube Video";
    videoChannelEl.textContent = lastClassification.channel || "Creator";

    const breakdown = lastClassification.score_breakdown || {};
    const edu = Math.round(breakdown.educational_value || 50);
    const car = Math.round(breakdown.career_relevance || 50);
    const ent = Math.round(breakdown.entertainment_value || 50);

    eduValEl.textContent = `${edu}%`;
    carValEl.textContent = `${car}%`;
    entValEl.textContent = `${ent}%`;
    eduBarEl.style.width = `${edu}%`;
    carBarEl.style.width = `${car}%`;
    entBarEl.style.width = `${ent}%`;
    breakdownGridEl.style.display = "flex";

    if (lastClassification.goal_alignment_reasoning) {
      alignmentReasonEl.textContent = lastClassification.goal_alignment_reasoning;
      alignmentReasonEl.style.display = "block";
    }
  }

  // Fetch active session status
  chrome.runtime.sendMessage({ type: "GET_ACTIVE_SESSION" }, (response) => {
    if (response?.success && response.data) {
      const data = response.data;
      totalWatchText.textContent = `${data.today_total_minutes.toFixed(0)}m watched today`;

      if (data.current_intent) {
        activeIntentText.textContent = data.current_intent;
      }

      // Render category meters
      budgetMetersEl.innerHTML = "";
      const primaryCategories = ["Education", "Career", "Technology", "Entertainment", "Gaming"];
      
      primaryCategories.forEach((cat) => {
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
        meter.className = "meter-row";
        meter.innerHTML = `
          <div class="meter-header">
            <span>${cat}</span>
            <span style="color: ${pct >= 100 ? '#EF4444' : '#94A3B8'}">${used.toFixed(0)} / ${limit}m (${pct}%)</span>
          </div>
          <div class="progress-track">
            <div class="progress-bar" style="width: ${pct}%; background-color: ${barColor};"></div>
          </div>
        `;
        budgetMetersEl.appendChild(meter);
      });
    }
  });

  // Intent submission
  setIntentBtn.addEventListener("click", () => {
    const text = intentInputEl.value.trim();
    if (!text) return;

    chrome.runtime.sendMessage({
      type: "LOG_INTENT",
      data: { intent_text: text }
    }, (res) => {
      if (res?.success) {
        activeIntentText.textContent = text;
        intentInputEl.value = "";
        setIntentBtn.textContent = "Saved!";
        setTimeout(() => { setIntentBtn.textContent = "Set"; }, 1500);
      }
    });
  });

  // Open side panel
  openSidepanelBtn.addEventListener("click", async () => {
    chrome.runtime.sendMessage({ type: "OPEN_SIDEPANEL" });
    window.close();
  });

  // Open full dashboard
  openDashboardBtn.addEventListener("click", () => {
    chrome.tabs.create({ url: "http://localhost:5173" });
  });
});
