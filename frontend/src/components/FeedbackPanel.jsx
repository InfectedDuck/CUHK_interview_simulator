export function FeedbackPanel({ feedback, mode }) {
  if (!feedback) return null;

  const coreScores = [
    { label: "Content", score: feedback.content_score },
    { label: "Relevance", score: feedback.relevance_score },
    { label: "Clarity", score: feedback.clarity_score },
  ];

  const extraScores = [
    feedback.values_alignment_score != null && { label: "CUHK Values", score: feedback.values_alignment_score },
    feedback.self_awareness_score != null && { label: "Self-Awareness", score: feedback.self_awareness_score },
    mode === "simulation" && feedback.time_management_score != null && { label: "Time Mgmt", score: feedback.time_management_score },
  ].filter(Boolean);

  const allScores = [...coreScores, ...extraScores];
  const avgScore = (
    allScores.reduce((sum, s) => sum + s.score, 0) / allScores.length
  ).toFixed(1);

  return (
    <div className="feedback-panel">
      <h4>Feedback</h4>
      <div className={`scores scores-${allScores.length > 4 ? "wide" : "normal"}`}>
        {allScores.map((s, i) => (
          <div key={i} className={`score-item ${s.score >= 7 ? "high" : s.score < 5 ? "low" : ""}`}>
            <label>{s.label}</label>
            <span className="score">{s.score}/10</span>
          </div>
        ))}
        <div className="score-item avg">
          <label>Average</label>
          <span className="score">{avgScore}/10</span>
        </div>
      </div>
      <p className="feedback-text">{feedback.feedback}</p>
    </div>
  );
}
