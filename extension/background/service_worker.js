// YouTubeWise Background Service Worker (Manifest V3)
const API_BASE = "http://localhost:8000/api";

// Initialize default storage on install
chrome.runtime.onInstalled.addListener(async () => {
  console.log("[YouTubeWise] Extension installed.");
  await chrome.storage.local.set({
    userId: "default_user",
    apiUrl: API_BASE,
    activeVideoId: null,
    activeVideoCategory: "Other",
    lastNotificationTime: {}
  });
});

// Update extension action badge based on score
async function updateBadge(score, category) {
  try {
    if (score !== null && score !== undefined) {
      const scoreInt = Math.round(score);
      await chrome.action.setBadgeText({ text: String(scoreInt) });
      
      let color = "#10B981"; // Emerald green (Useful)
      if (scoreInt < 35) {
        color = "#EF4444"; // Red (Low)
      } else if (scoreInt < 65) {
        color = "#F59E0B"; // Amber (Moderate)
      }
      await chrome.action.setBadgeBackgroundColor({ color });
    } else {
      await chrome.action.setBadgeText({ text: "" });
    }
  } catch (err) {
    console.error("[YouTubeWise] Badge update error:", err);
  }
}

// Show threshold notification
async function triggerThresholdNotification(category, message, isExceeded = false) {
  try {
    const { lastNotificationTime = {} } = await chrome.storage.local.get("lastNotificationTime");
    const now = Date.now();
    const lastTime = lastNotificationTime[category] || 0;
    
    // Throttle notifications to at most once every 3 minutes per category
    if (now - lastTime < 180000 && !isExceeded) {
      return;
    }
    
    lastNotificationTime[category] = now;
    await chrome.storage.local.set({ lastNotificationTime });

    await chrome.notifications.create(`limit_warning_${category}_${now}`, {
      type: "basic",
      iconUrl: chrome.runtime.getURL("icons/icon-128.png"),
      title: isExceeded ? `⚠️ ${category} Limit Exceeded` : `⏱️ ${category} Time Alert`,
      message: message,
      priority: 2
    });
  } catch (err) {
    console.error("[YouTubeWise] Notification error:", err);
  }
}

// Handle messages from content script, popup, and sidepanel
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  (async () => {
    try {
      const { apiUrl = API_BASE, userId = "default_user" } = await chrome.storage.local.get(["apiUrl", "userId"]);

      if (message.type === "CLASSIFY_VIDEO") {
        const payload = {
          ...message.data,
          user_id: userId
        };

        const res = await fetch(`${apiUrl}/classify`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(payload)
        });

        if (!res.ok) {
          throw new Error(`Classification failed: ${res.statusText}`);
        }

        const data = await res.json();
        await chrome.storage.local.set({
          activeVideoId: data.video_id,
          activeVideoCategory: data.content_type,
          lastClassification: data
        });

        await updateBadge(data.personalized_score, data.content_type);
        sendResponse({ success: true, data });
      }

      else if (message.type === "WATCH_TICK") {
        const payload = {
          ...message.data,
          user_id: userId
        };

        const res = await fetch(`${apiUrl}/session/watch`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(payload)
        });

        if (!res.ok) {
          throw new Error(`Watch tick failed: ${res.statusText}`);
        }

        const data = await res.json();

        // Check for warnings & send notifications
        if (data.warnings && data.warnings.length > 0) {
          const warningMsg = data.warnings[0];
          await triggerThresholdNotification(payload.category, warningMsg, data.is_any_limit_exceeded);
        }

        sendResponse({ success: true, data });
      }

      else if (message.type === "LOG_INTENT") {
        const payload = {
          ...message.data,
          user_id: userId
        };

        const res = await fetch(`${apiUrl}/session/intent`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(payload)
        });

        if (!res.ok) throw new Error("Intent logging failed");
        const data = await res.json();
        await chrome.storage.local.set({ currentIntent: data.intent_text });
        sendResponse({ success: true, data });
      }

      else if (message.type === "ASK_CHATBOT") {
        const payload = {
          ...message.data,
          user_id: userId
        };

        const res = await fetch(`${apiUrl}/chat`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(payload)
        });

        if (!res.ok) throw new Error("Chat request failed");
        const data = await res.json();
        sendResponse({ success: true, data });
      }

      else if (message.type === "GET_ACTIVE_SESSION") {
        const res = await fetch(`${apiUrl}/session/active?user_id=${userId}`);
        if (!res.ok) throw new Error("Failed to get session");
        const data = await res.json();
        sendResponse({ success: true, data });
      }

      else if (message.type === "GET_PROFILE") {
        const res = await fetch(`${apiUrl}/profile?user_id=${userId}`);
        if (!res.ok) throw new Error("Failed to get profile");
        const data = await res.json();
        sendResponse({ success: true, data });
      }

      else if (message.type === "OPEN_SIDEPANEL") {
        let windowId = sender?.tab?.windowId;
        if (!windowId) {
          const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
          windowId = tab?.windowId;
        }
        if (windowId) {
          await chrome.sidePanel.open({ windowId });
          sendResponse({ success: true });
        }
      }

      else {
        sendResponse({ success: false, error: "Unknown message type" });
      }
    } catch (err) {
      console.error(`[YouTubeWise] Error handling ${message.type}:`, err);
      sendResponse({ success: false, error: err.message });
    }
  })();

  return true; // Keep message channel open for async response
});
