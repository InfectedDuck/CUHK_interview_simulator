import { useState } from "react";
import { api } from "../api/client";

export function AnswerComparisonPanel({ sessionId, exchangeId, originalAnswer }) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleImprove = async () => {
    setLoading(true);
    setError(null);
    try {
      const result = await api.improveAnswer(sessionId, exchangeId);
      setData(result);
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  };

  if (!data) {
    return (
      <div className="answer-comparison">
        <button
          className="btn btn-coach"
          onClick={handleImprove}
          disabled={loading}
        >
          {loading ? "Generating improved answer..." : "Show Me a Better Answer"}
        </button>
        {error && <div className="error-text">{error}</div>}
      </div>
    );
  }

  return (
    <div className="answer-comparison">
      <h4>Answer Comparison</h4>
      <div className="comparison-grid">
        <div className="comparison-col original">
          <h5>Your Answer</h5>
          <p>{originalAnswer}</p>
        </div>
        <div className="comparison-col improved">
          <h5>Improved Version</h5>
          <p>{data.improved_answer}</p>
        </div>
      </div>

      {data.key_changes?.length > 0 && (
        <div className="key-changes">
          <h5>Key Improvements</h5>
          <ul>
            {data.key_changes.map((change, i) => (
              <li key={i}>{change}</li>
            ))}
          </ul>
        </div>
      )}

      {data.star_breakdown && (
        <div className="star-breakdown">
          <h5>STAR Method Breakdown</h5>
          <div className="star-grid">
            {["situation", "task", "action", "result"].map((key) => (
              <div key={key} className="star-item">
                <span className="star-label">{key.charAt(0).toUpperCase() + key.slice(1)}</span>
                <p>{data.star_breakdown[key] || "Not identified"}</p>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
