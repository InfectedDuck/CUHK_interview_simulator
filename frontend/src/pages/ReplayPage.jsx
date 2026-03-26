import { useState, useEffect } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { api } from "../api/client";
import { VoiceRecorder } from "../components/VoiceRecorder";

export function ReplayPage() {
  const { userId, sessionId } = useParams();
  const navigate = useNavigate();
  const [session, setSession] = useState(null);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [replayResult, setReplayResult] = useState(null);

  useEffect(() => {
    api
      .getSession(parseInt(userId), parseInt(sessionId))
      .then(setSession)
      .finally(() => setLoading(false));
  }, [userId, sessionId]);

  const exchange = session?.exchanges?.[currentIndex];

  const handleReplayAnswer = async (answerText) => {
    if (!exchange) return;
    setSubmitting(true);
    setReplayResult(null);
    try {
      const result = await api.replayAnswer(parseInt(sessionId), exchange.id, answerText);
      setReplayResult(result);
    } catch (e) {
      setReplayResult({ error: e.message });
    } finally {
      setSubmitting(false);
    }
  };

  const nextExchange = () => {
    setReplayResult(null);
    setCurrentIndex((i) => Math.min(i + 1, (session?.exchanges?.length || 1) - 1));
  };

  const prevExchange = () => {
    setReplayResult(null);
    setCurrentIndex((i) => Math.max(i - 1, 0));
  };

  if (loading) return <div className="loading">Loading session...</div>;
  if (!session) return <div className="error-text">Session not found</div>;

  return (
    <div className="page replay-page">
      <div className="page-header">
        <button className="btn btn-back" onClick={() => navigate(`/results/${userId}/${sessionId}`)}>
          ← Back to Results
        </button>
        <h1>Replay & Improve</h1>
      </div>

      {exchange && (
        <>
          {/* Question */}
          <div className="question-card">
            <div className="question-header">
              <span className="question-number">
                Question {currentIndex + 1} of {session.exchanges.length}
              </span>
              {exchange.question_type && (
                <span className={`question-type-badge ${exchange.question_type}`}>
                  {exchange.question_type}
                </span>
              )}
            </div>
            <p className="question-text">{exchange.question_text}</p>
          </div>

          {/* Original Answer */}
          <div className="card original-answer">
            <h3>Your Original Answer</h3>
            <p className="answer-text">{exchange.answer_text || "No answer recorded"}</p>
            <div className="original-scores">
              <span>Content: {exchange.content_score}</span>
              <span>Relevance: {exchange.relevance_score}</span>
              <span>Clarity: {exchange.clarity_score}</span>
            </div>
            {exchange.feedback && <p className="original-feedback">{exchange.feedback}</p>}
          </div>

          {/* Replay Input */}
          {!replayResult && (
            <div className="card">
              <h3>Try Again — Record Your Improved Answer</h3>
              <VoiceRecorder
                onTranscript={handleReplayAnswer}
                userId={parseInt(userId)}
                context={exchange ? `Interview question: ${exchange.question_text}` : ""}
                placeholder="Speak your improved answer..."
              />
              {submitting && <div className="loading">Analyzing your new answer...</div>}
            </div>
          )}

          {/* Replay Result */}
          {replayResult && !replayResult.error && (
            <div className="card replay-result">
              <h3>Attempt #{replayResult.attempt_number} — Results</h3>
              <div className="delta-grid">
                {["content", "relevance", "clarity"].map((key) => (
                  <div key={key} className="delta-item">
                    <label>{key.charAt(0).toUpperCase() + key.slice(1)}</label>
                    <div className="delta-scores">
                      <span className="old-score">{exchange[`${key}_score`]}</span>
                      <span className="arrow">→</span>
                      <span className="new-score">{replayResult.scores[`${key}_score`]}</span>
                      <span className={`delta ${replayResult.deltas[key] > 0 ? "positive" : replayResult.deltas[key] < 0 ? "negative" : ""}`}>
                        {replayResult.deltas[key] > 0 ? "+" : ""}{replayResult.deltas[key]}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
              <p className="replay-feedback">{replayResult.feedback}</p>
              <button className="btn btn-secondary" onClick={() => setReplayResult(null)}>
                Try Again
              </button>
            </div>
          )}

          {replayResult?.error && (
            <div className="error-text">{replayResult.error}</div>
          )}

          {/* Navigation */}
          <div className="replay-nav">
            <button className="btn btn-secondary" onClick={prevExchange} disabled={currentIndex === 0}>
              ← Previous
            </button>
            <button className="btn btn-secondary" onClick={nextExchange} disabled={currentIndex >= session.exchanges.length - 1}>
              Next →
            </button>
          </div>
        </>
      )}
    </div>
  );
}
