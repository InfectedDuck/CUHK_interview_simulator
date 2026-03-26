export function ScoreBoard({ overallScore, summaryFeedback, exchanges, sessionId }) {
  return (
    <div className="score-board">
      <div className="overall-score">
        <h2>Interview Complete</h2>
        {overallScore != null && (
          <div className="big-score">
            <span className="number">{overallScore.toFixed(1)}</span>
            <span className="out-of">/10</span>
          </div>
        )}
      </div>

      {summaryFeedback && (
        <div className="summary-feedback">
          <h3>Summary</h3>
          <p>{summaryFeedback}</p>
        </div>
      )}

      {exchanges?.length > 0 && (
        <div className="exchange-breakdown">
          <h3>Question Breakdown</h3>
          {exchanges.map((ex, i) => (
            <div key={i} className="exchange-item">
              <div className="exchange-question">
                <strong>Q{ex.question_number}</strong>
                {ex.question_type && (
                  <span className={`question-type-badge small ${ex.question_type}`}>
                    {ex.question_type}
                  </span>
                )}
                : {ex.question_text}
              </div>
              {ex.answer_text && (
                <div className="exchange-answer">
                  <strong>Your answer:</strong> {ex.answer_text}
                </div>
              )}
              {ex.content_score != null && (
                <div className="exchange-scores">
                  Content: {ex.content_score} | Relevance: {ex.relevance_score} | Clarity: {ex.clarity_score}
                  {ex.values_alignment_score != null && ` | Values: ${ex.values_alignment_score}`}
                  {ex.self_awareness_score != null && ` | Self-Awareness: ${ex.self_awareness_score}`}
                </div>
              )}
              {ex.feedback && <div className="exchange-feedback">{ex.feedback}</div>}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
