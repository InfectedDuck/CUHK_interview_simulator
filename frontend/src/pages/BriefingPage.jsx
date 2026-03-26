import { useState, useEffect } from "react";
import { useParams, useNavigate, useSearchParams } from "react-router-dom";
import { api } from "../api/client";

export function BriefingPage() {
  const { userId } = useParams();
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const university = searchParams.get("university") || "CUHK";
  const program = searchParams.get("program") || "";
  const mode = searchParams.get("mode") || "practice";

  const [briefing, setBriefing] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    api
      .generateBriefing(parseInt(userId), university, program)
      .then(setBriefing)
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
  }, [userId, university, program]);

  const startInterview = () => {
    navigate(
      `/interview/${userId}?university=${encodeURIComponent(university)}&program=${encodeURIComponent(program)}&mode=${mode}&ready=1`
    );
  };

  if (loading) {
    return (
      <div className="page briefing-page">
        <div className="loading">Generating your personalized strategy briefing...</div>
      </div>
    );
  }

  return (
    <div className="page briefing-page">
      <div className="page-header">
        <button className="btn btn-back" onClick={() => navigate(`/interview/${userId}`)}>
          ← Back
        </button>
        <h1>Strategy Briefing</h1>
      </div>

      {error && <div className="banner warning">{error}</div>}

      {briefing && (
        <>
          {/* Likely Questions */}
          {briefing.likely_questions?.length > 0 && (
            <div className="card briefing-section">
              <h2>Likely Questions</h2>
              {briefing.likely_questions.map((q, i) => (
                <div key={i} className="briefing-item">
                  <div className="briefing-question">"{q.question}"</div>
                  <div className="briefing-why"><strong>Why they ask:</strong> {q.why_they_ask}</div>
                  <div className="briefing-angle"><strong>Your angle:</strong> {q.your_angle}</div>
                </div>
              ))}
            </div>
          )}

          {/* Key Talking Points */}
          {briefing.key_talking_points?.length > 0 && (
            <div className="card briefing-section">
              <h2>Your Key Talking Points</h2>
              {briefing.key_talking_points.map((tp, i) => (
                <div key={i} className="briefing-item">
                  <strong>{tp.topic}</strong>
                  <p><em>Your story:</em> {tp.your_story}</p>
                  <p><em>CUHK connection:</em> {tp.connection_to_cuhk}</p>
                </div>
              ))}
            </div>
          )}

          {/* Areas to Practice */}
          {briefing.areas_to_practice?.length > 0 && (
            <div className="card briefing-section">
              <h2>Areas to Practice</h2>
              {briefing.areas_to_practice.map((a, i) => (
                <div key={i} className="briefing-item">
                  <strong>{a.weakness}</strong>
                  <p>{a.exercise}</p>
                </div>
              ))}
            </div>
          )}

          {/* Do's and Don'ts */}
          <div className="card briefing-section dos-donts">
            <div className="dos">
              <h3>Do</h3>
              <ul>{briefing.dos?.map((d, i) => <li key={i}>{d}</li>)}</ul>
            </div>
            <div className="donts">
              <h3>Don't</h3>
              <ul>{briefing.donts?.map((d, i) => <li key={i}>{d}</li>)}</ul>
            </div>
          </div>

          {/* Strategies */}
          {(briefing.opening_strategy || briefing.closing_strategy) && (
            <div className="card briefing-section">
              <h2>Interview Strategy</h2>
              {briefing.opening_strategy && (
                <div className="briefing-item">
                  <strong>Opening:</strong> {briefing.opening_strategy}
                </div>
              )}
              {briefing.closing_strategy && (
                <div className="briefing-item">
                  <strong>Closing:</strong> {briefing.closing_strategy}
                </div>
              )}
            </div>
          )}
        </>
      )}

      <div className="actions">
        <button className="btn btn-primary btn-large" onClick={startInterview}>
          I'm Ready — Start Interview
        </button>
      </div>
    </div>
  );
}
