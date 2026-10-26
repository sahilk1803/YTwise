// YouTubeWise Content Script
(function () {
  console.log("[YouTubeWise] Content script loaded.");

  let currentVideoId = null;
  let currentClassification = null;
  let isTracking = false;
  let watchInterval = null;
  let isCardExpanded = false;
  let isModalDismissedForVideo = false;

  // Extract video ID from URL
  function getVideoIdFromUrl() {
    const urlParams = new URLSearchParams(window.location.search);
    return urlParams.get("v");
  }

  // Extract video metadata from DOM
  function extractMetadata() {
    const videoId = getVideoIdFromUrl();
    if (!videoId) return null;

    // Resilient Title extraction
    const titleEl = document.querySelector(
      "h1.ytd-watch-metadata yt-formatted-string, ytd-watch-metadata #title h1, h1.title.style-scope.ytd-video-primary-info-renderer"
    );
    let title = titleEl ? titleEl.textContent.trim() : "";
    if (!title) {
      title = document.title.replace(" - YouTube", "").trim();
    }

    // Resilient Channel extraction
    const channelEl = document.querySelector(
      "ytd-watch-metadata #channel-name a, #owner #channel-name a, ytd-channel-name #text a"
    );
    const channel = channelEl ? channelEl.textContent.trim() : "";

    // Resilient Description extraction
    const descEl = document.querySelector(
      "#description-inline-expander, ytd-text-inline-expander #plain-snippet-text, #description yt-formatted-string"
    );
    const description = descEl ? descEl.textContent.trim() : "";

    // Subtitle / Captions text if active
    let transcriptText = "";
    const captionSegments = document.querySelectorAll(".ytp-caption-segment");
    if (captionSegments.length > 0) {
      transcriptText = Array.from(captionSegments).map(el => el.textContent).join(" ");
    }

    return {
      video_id: videoId,
      title: title || "YouTube Video",
      channel: channel || "YouTube Creator",
      description: description.substring(0, 1500),
      transcript_text: transcriptText
    };
  }

  // Inject or update in-page HUD
  function renderHud(classification) {
    let container = document.getElementById("youtubewise-hud-container");
    if (!container) {
      container = document.createElement("div");
      container.id = "youtubewise-hud-container";
      document.body.appendChild(container);
    }

    const score = Math.round(classification.personalized_score || classification.base_value_score || 50);
    const category = classification.content_type || "Other";
    const band = classification.personalized_band || "Moderate";

    let dotClass = "moderate";
    if (score >= 70) dotClass = "high";
    else if (score < 40) dotClass = "low";

    container.innerHTML = `
      ${isCardExpanded ? `
        <div class="ytw-expanded-card">
          <div class="ytw-card-header">
            <div class="ytw-card-title">
              <span>🧠 YouTubeWise Score</span>
            </div>
            <button class="ytw-card-close" id="ytw-close-card">&times;</button>
          </div>
          
          <div class="ytw-metrics-grid">
            <div class="ytw-metric-box">
              <div class="ytw-metric-label">Value Score</div>
              <div class="ytw-metric-val" style="color: ${score >= 70 ? '#10B981' : score < 40 ? '#EF4444' : '#F59E0B'}">${score}/100</div>
            </div>
            <div class="ytw-metric-box">
              <div class="ytw-metric-label">Category</div>
              <div class="ytw-metric-val">${category}</div>
            </div>
            <div class="ytw-metric-box">
              <div class="ytw-metric-label">Rating</div>
              <div class="ytw-metric-val">${band}</div>
            </div>
          </div>

          <div style="font-size: 11px; color: #94A3B8; font-style: italic;">
            ${classification.goal_alignment_reasoning || classification.summary}
          </div>

          ${classification.key_takeaways && classification.key_takeaways.length > 0 ? `
            <ul class="ytw-takeaways-list">
              ${classification.key_takeaways.slice(0, 3).map(t => `<li>${t}</li>`).join("")}
            </ul>
          ` : ""}

          <div class="ytw-btn-row">
            <button class="ytw-btn ytw-btn-primary" id="ytw-open-sidepanel">
              💬 Ask AI Advisor
            </button>
            <button class="ytw-btn ytw-btn-secondary" id="ytw-open-dashboard">
              📊 Analytics
            </button>
          </div>
        </div>
      ` : ""}

      <div class="ytw-badge-pill" id="ytw-toggle-card" title="Click for YouTubeWise Video Intelligence">
        <span class="ytw-score-dot ${dotClass}"></span>
        <span>${score}/100</span>
        <span class="ytw-category-badge">${category}</span>
        <span style="font-size: 10px; color: #94A3B8;">${isCardExpanded ? '▼' : '▲'}</span>
      </div>
    `;

    // Event listeners
    document.getElementById("ytw-toggle-card")?.addEventListener("click", () => {
      isCardExpanded = !isCardExpanded;
      renderHud(currentClassification);
    });

    document.getElementById("ytw-close-card")?.addEventListener("click", () => {
      isCardExpanded = false;
      renderHud(currentClassification);
    });

    document.getElementById("ytw-open-sidepanel")?.addEventListener("click", () => {
      chrome.runtime.sendMessage({ type: "OPEN_SIDEPANEL" });
    });

    document.getElementById("ytw-open-dashboard")?.addEventListener("click", () => {
      window.open("http://localhost:5173", "_blank");
    });
  }

  // Show Intervention Limit Modal
  function showInterventionModal(warningMessage) {
    if (isModalDismissedForVideo) return;
    if (document.getElementById("youtubewise-intervention-modal")) return;

    const modal = document.createElement("div");
    modal.id = "youtubewise-intervention-modal";
    modal.innerHTML = `
      <div class="ytw-modal-header">
        <span>⏱️ Digital Wellbeing Intervention</span>
      </div>
      <div class="ytw-modal-body">
        <strong>${warningMessage}</strong><br/>
        You've reached your daily limit for leisure content. Would you like to switch back to your study goals?
      </div>
      <div class="ytw-modal-actions">
        <button class="ytw-btn ytw-btn-secondary" id="ytw-snooze-btn">Snooze (5m)</button>
        <button class="ytw-btn ytw-btn-primary" id="ytw-redirect-learning">Go to Learning</button>
      </div>
    `;

    document.body.appendChild(modal);

    document.getElementById("ytw-snooze-btn")?.addEventListener("click", () => {
      isModalDismissedForVideo = true;
      modal.remove();
    });

    document.getElementById("ytw-redirect-learning")?.addEventListener("click", () => {
      window.location.href = "https://www.youtube.com/results?search_query=DSA+and+System+Design+tutorials";
    });
  }

  // Active watch time tracking loop
  function startWatchTracker() {
    if (watchInterval) clearInterval(watchInterval);

    watchInterval = setInterval(async () => {
      const videoEl = document.querySelector("video");
      if (!videoEl || videoEl.paused || videoEl.ended || document.hidden || !currentVideoId) {
        return;
      }

      const category = currentClassification?.content_type || "Other";
      const title = currentClassification?.title || document.title;
      const channel = currentClassification?.channel || "";

      chrome.runtime.sendMessage({
        type: "WATCH_TICK",
        data: {
          video_id: currentVideoId,
          video_title: title,
          channel: channel,
          category: category,
          duration_sec: 5
        }
      }, (response) => {
        if (response?.success && response.data?.is_any_limit_exceeded) {
          const warning = response.data.warnings?.[0] || "Daily category limit reached.";
          showInterventionModal(warning);
        }
      });
    }, 5000);
  }

  // Handle Video Change
  async function onVideoChange() {
    const videoId = getVideoIdFromUrl();
    if (!videoId) {
      const hud = document.getElementById("youtubewise-hud-container");
      if (hud) hud.remove();
      currentVideoId = null;
      if (watchInterval) clearInterval(watchInterval);
      return;
    }

    if (videoId === currentVideoId && currentClassification) {
      return;
    }

    currentVideoId = videoId;
    isModalDismissedForVideo = false;
    console.log(`[YouTubeWise] Detected video change: ${videoId}`);

    // Wait a moment for YouTube DOM to settle
    setTimeout(async () => {
      const metadata = extractMetadata();
      if (!metadata) return;

      chrome.runtime.sendMessage({
        type: "CLASSIFY_VIDEO",
        data: metadata
      }, (response) => {
        if (response?.success && response.data) {
          currentClassification = response.data;
          renderHud(currentClassification);
          startWatchTracker();
        }
      });
    }, 1200);
  }

  // SPA Navigation Event Listeners
  document.addEventListener("yt-navigate-finish", onVideoChange);
  document.addEventListener("spfdone", onVideoChange);
  window.addEventListener("popstate", onVideoChange);

  // Initial check
  if (getVideoIdFromUrl()) {
    onVideoChange();
  }
})();
