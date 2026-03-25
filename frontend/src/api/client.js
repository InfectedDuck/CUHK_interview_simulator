const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

async function request(path, options = {}) {
  const res = await fetch(`${API_URL}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  if (!res.ok) {
    const error = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(error.detail || "Request failed");
  }
  return res.json();
}

export const api = {
  // Health
  health: () => request("/api/health"),

  // Users
  createUser: (name) =>
    request("/api/users", {
      method: "POST",
      body: JSON.stringify({ name }),
    }),
  getUser: (id) => request(`/api/users/${id}`),
  listUsers: () => request("/api/users"),

  // Profile
  extractProfile: (userId, transcript) =>
    request("/api/profile/extract", {
      method: "POST",
      body: JSON.stringify({ user_id: userId, transcript }),
    }),
  getProfile: (userId) => request(`/api/profile/${userId}`),
  updateProfile: (userId, data) =>
    request(`/api/profile/${userId}`, {
      method: "PUT",
      body: JSON.stringify(data),
    }),

  // Interview
  startInterview: (userId, targetUniversity) =>
    request("/api/interview/start", {
      method: "POST",
      body: JSON.stringify({
        user_id: userId,
        target_university: targetUniversity,
      }),
    }),
  submitAnswer: (sessionId, answerText) =>
    request(`/api/interview/${sessionId}/answer`, {
      method: "POST",
      body: JSON.stringify({ answer_text: answerText }),
    }),
  endInterview: (sessionId) =>
    request(`/api/interview/${sessionId}/end`, { method: "POST" }),

  // Sessions
  listSessions: (userId) => request(`/api/sessions/${userId}`),
  getSession: (userId, sessionId) =>
    request(`/api/sessions/${userId}/${sessionId}`),
};
