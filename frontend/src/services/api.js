const API_BASE = "http://localhost:8000/api";

export async function fetchDailyAnalytics(userId = "default_user") {
  const res = await fetch(`${API_BASE}/analytics/daily?user_id=${userId}`);
  if (!res.ok) throw new Error("Failed to fetch daily analytics");
  return res.json();
}

export async function fetchWeeklyAnalytics(userId = "default_user") {
  const res = await fetch(`${API_BASE}/analytics/weekly?user_id=${userId}`);
  if (!res.ok) throw new Error("Failed to fetch weekly analytics");
  return res.json();
}

export async function fetchProfile(userId = "default_user") {
  const res = await fetch(`${API_BASE}/profile?user_id=${userId}`);
  if (!res.ok) throw new Error("Failed to fetch profile");
  return res.json();
}

export async function updateProfile(userId = "default_user", data) {
  const res = await fetch(`${API_BASE}/profile?user_id=${userId}`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
  if (!res.ok) throw new Error("Failed to update profile");
  return res.json();
}

export async function logIntent(userId = "default_user", intentText) {
  const res = await fetch(`${API_BASE}/session/intent`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ user_id: userId, intent_text: intentText }),
  });
  if (!res.ok) throw new Error("Failed to log intent");
  return res.json();
}

export async function seedDemoData(userId = "default_user") {
  const res = await fetch(`${API_BASE}/analytics/seed-demo?user_id=${userId}`, {
    method: "POST",
  });
  if (!res.ok) throw new Error("Failed to seed demo data");
  return res.json();
}
