

const API_BASE = process.env.NEXT_PUBLIC_API_BASE || "http://127.0.0.1:8000";

console.log("API_BASE =", API_BASE);


export async function login(username, password) {
  const body = new URLSearchParams();
  body.append("username", username);
  body.append("password", password);

  const r = await fetch(`${API_BASE}/auth/login`, {
    method: "POST",
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
    body,
  });

  if (!r.ok) throw new Error("Login failed");
  return r.json(); // { access_token, token_type }
}

export async function createJob(token, input_text) {
  const r = await fetch(`${API_BASE}/jobs`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "Authorization": `Bearer ${token}`
    },
    body: JSON.stringify({ input_text })
  });
  if (!r.ok) throw new Error("Create job failed");
  return r.json();
}

export async function listJobs(token) {
  const r = await fetch(`${API_BASE}/jobs`, {
    headers: { "Authorization": `Bearer ${token}` }
  });
  if (!r.ok) throw new Error("List jobs failed");
  return r.json();
}

export async function getJob(token, jobId) {
  const r = await fetch(`${API_BASE}/jobs/${jobId}`, {
    headers: { "Authorization": `Bearer ${token}` }
  });
  if (!r.ok) throw new Error("Get job failed");
  return r.json();
}

export async function getResult(token, jobId) {
  const r = await fetch(`${API_BASE}/jobs/${jobId}/result`, {
    headers: { "Authorization": `Bearer ${token}` }
  });
  if (!r.ok) throw new Error("Result not ready");
  return r.json();
}

export async function getAnalytics(token) {
  const r = await fetch(`${API_BASE}/analytics/summary`, {
    headers: { "Authorization": `Bearer ${token}` }
  });
  if (!r.ok) throw new Error("Analytics failed");
  return r.json();
}
