export function FeedbackPanel({ feedback }) {
  if (!feedback) return null;

  const avgScore = (
    (feedback.content_score + feedback.relevance_score + feedback.clarity_score) / 3
  ).toFixed(1);

  return (
    <div className="feedback-panel">
      <h4>Feedback</h4>
      <div className="scores">
        <div className="score-item">
          <label>Content</label>
          <span className="score">{feedback.content_score}/10</span>
        </div>
        <div className="score-item">
          <label>Relevance</label>
          <span className="score">{feedback.relevance_score}/10</span>
        </div>
        <div className="score-item">
          <label>Clarity</label>
          <span className="score">{feedback.clarity_score}/10</span>
        </div>
        <div className="score-item avg">
          <label>Average</label>
          <span className="score">{avgScore}/10</span>
        </div>
      </div>
      <p className="feedback-text">{feedback.feedback}</p>
    </div>
  );
}
