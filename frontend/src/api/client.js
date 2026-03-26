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
  startInterview: (userId, targetUniversity, targetProgram, mode, difficulty) =>
    request("/api/interview/start", {
      method: "POST",
      body: JSON.stringify({
        user_id: userId,
        target_university: targetUniversity,
        target_program: targetProgram,
        mode: mode || "practice",
        difficulty: difficulty || "medium",
      }),
    }),
  submitAnswer: (sessionId, answerText, responseTimeSeconds) =>
    request(`/api/interview/${sessionId}/answer`, {
      method: "POST",
      body: JSON.stringify({
        answer_text: answerText,
        response_time_seconds: responseTimeSeconds,
      }),
    }),
  endInterview: (sessionId) =>
    request(`/api/interview/${sessionId}/end`, { method: "POST" }),

  // Answer improvement
  improveAnswer: (sessionId, exchangeId) =>
    request(`/api/interview/${sessionId}/exchange/${exchangeId}/improve`, {
      method: "POST",
    }),

  // Replay
  replayAnswer: (sessionId, exchangeId, answerText) =>
    request(`/api/interview/${sessionId}/replay/${exchangeId}`, {
      method: "POST",
      body: JSON.stringify({ answer_text: answerText }),
    }),

  // Sessions
  listSessions: (userId) => request(`/api/sessions/${userId}`),
  getSession: (userId, sessionId) =>
    request(`/api/sessions/${userId}/${sessionId}`),

  // Analytics
  getAnalytics: (userId) => request(`/api/analytics/${userId}`),

  // Briefing
  generateBriefing: (userId, university, program) =>
    request(`/api/briefing/${userId}`, {
      method: "POST",
      body: JSON.stringify({ university, program }),
    }),
  getInterviewFormat: (university, program) =>
    request(`/api/briefing/format?university=${encodeURIComponent(university)}&program=${encodeURIComponent(program || "")}`),
  getPrograms: () => request("/api/briefing/programs"),

  // Whisper transcription with AI context correction
  transcribe: async (audioBlob, { userId, context, language } = {}) => {
    const formData = new FormData();
    formData.append("file", audioBlob, "recording.webm");
    if (userId) formData.append("user_id", userId);
    if (context) formData.append("context", context);
    if (language) formData.append("language", language);
    const res = await fetch(
      `${API_URL}/api/transcribe`,
      { method: "POST", body: formData }
    );
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: res.statusText }));
      throw new Error(err.detail || "Transcription failed");
    }
    return res.json();
  },
};
