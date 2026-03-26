import { useState, useEffect } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { api } from "../api/client";
import { ScoreBoard } from "../components/ScoreBoard";
import { InterviewReport } from "../components/InterviewReport";

export function ResultsPage() {
  const { userId, sessionId } = useParams();
  const navigate = useNavigate();
  const [session, setSession] = useState(null);
  const [loading, setLoading] = useState(true);
  const [showReport, setShowReport] = useState(false);

  useEffect(() => {
    api
      .getSession(parseInt(userId), parseInt(sessionId))
      .then(setSession)
      .finally(() => setLoading(false));
  }, [userId, sessionId]);

  if (loading) return <div className="loading-skeleton"><div className="skeleton-text" /><div className="skeleton-text short" /><div className="skeleton-text" /></div>;
  if (!session) return <div className="error-text">Session not found</div>;

  if (showReport) {
    return (
      <div className="page">
        <button className="btn btn-back no-print" onClick={() => setShowReport(false)}>← Back to Results</button>
        <InterviewReport session={session} />
      </div>
    );
  }

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
        sessionId={parseInt(sessionId)}
      />

      <div className="actions">
        <button className="btn btn-primary" onClick={() => navigate(`/replay/${userId}/${sessionId}`)}>
          Replay & Improve Answers
        </button>
        <button className="btn btn-secondary" onClick={() => setShowReport(true)}>
          Export as PDF
        </button>
        <button className="btn btn-secondary" onClick={() => navigate(`/interview/${userId}`)}>
          Practice Again
        </button>
        <button className="btn btn-secondary" onClick={() => navigate(`/analytics/${userId}`)}>
          View Analytics
        </button>
        <button className="btn btn-back" onClick={() => navigate("/")}>Home</button>
      </div>
    </div>
  );
}
