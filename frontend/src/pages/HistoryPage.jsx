import { useState, useEffect } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { api } from "../api/client";

export function HistoryPage() {
  const { userId } = useParams();
  const navigate = useNavigate();
  const [sessions, setSessions] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api
      .listSessions(parseInt(userId))
      .then(setSessions)
      .finally(() => setLoading(false));
  }, [userId]);

  if (loading) return <div className="loading">Loading...</div>;

  return (
    <div className="page history-page">
      <div className="page-header">
        <button className="btn btn-back" onClick={() => navigate(`/profile/${userId}`)}>
          ← Back
        </button>
        <h1>Interview History</h1>
        {sessions.length > 0 && (
          <button className="btn btn-secondary" onClick={() => navigate(`/analytics/${userId}`)}>
            Analytics
          </button>
        )}
      </div>

      {sessions.length === 0 ? (
        <div className="card">
          <p>No interview sessions yet. Start your first practice!</p>
          <button
            className="btn btn-primary"
            onClick={() => navigate(`/interview/${userId}`)}
          >
            Start Interview
          </button>
        </div>
      ) : (
        <div className="session-list">
          {sessions.map((s) => (
            <div
              key={s.id}
              className="session-item card"
              onClick={() => navigate(`/results/${userId}/${s.id}`)}
            >
              <div className="session-info">
                <strong>{s.target_university}</strong>
                <span className={`status ${s.status}`}>{s.status}</span>
              </div>
              <div className="session-meta">
                <span>{new Date(s.started_at).toLocaleDateString()}</span>
                {s.overall_score != null && (
                  <span className="score">{s.overall_score.toFixed(1)}/10</span>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
