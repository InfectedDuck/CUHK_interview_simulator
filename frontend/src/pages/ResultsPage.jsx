import { useState, useEffect } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { api } from "../api/client";
import { ScoreBoard } from "../components/ScoreBoard";

export function ResultsPage() {
  const { userId, sessionId } = useParams();
  const navigate = useNavigate();
  const [session, setSession] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api
      .getSession(parseInt(userId), parseInt(sessionId))
      .then(setSession)
      .finally(() => setLoading(false));
  }, [userId, sessionId]);

  if (loading) return <div className="loading">Loading...</div>;
  if (!session) return <div className="error-text">Session not found</div>;

  return (
    <div className="page results-page">
      <div className="page-header">
        <button className="btn btn-back" onClick={() => navigate(`/history/${userId}`)}>
          ← Back
        </button>
        <h1>Results — {session.target_university}</h1>
      </div>

      <ScoreBoard
        overallScore={session.overall_score}
        summaryFeedback={session.summary_feedback}
        exchanges={session.exchanges}
      />

      <div className="actions">
        <button
          className="btn btn-primary"
          onClick={() => navigate(`/interview/${userId}`)}
        >
          Practice Again
        </button>
        <button className="btn btn-back" onClick={() => navigate("/")}>
          Home
        </button>
      </div>
    </div>
  );
}
