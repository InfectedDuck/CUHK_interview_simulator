import { useEffect } from "react";
import { useSpeechSynthesis } from "../hooks/useSpeechSynthesis";

const TYPE_LABELS = {
  warmup: "Warm-up",
  probe: "Deep Dive",
  follow_up: "Follow-up",
  challenge: "Challenge",
  closing: "Final Question",
};

export function QuestionCard({ questionNumber, totalQuestions, questionText, questionType, autoSpeak }) {
  const { speak, cancel, isSpeaking } = useSpeechSynthesis();

  useEffect(() => {
    if (autoSpeak && questionText) {
      speak(questionText);
    }
    return () => cancel();
  }, [questionText, autoSpeak]);

  return (
    <div className="question-card">
      <div className="question-header">
        <span className="question-number">
          Question {questionNumber}{totalQuestions ? ` of ${totalQuestions}` : ""}
        </span>
        <div className="question-header-right">
          {questionType && TYPE_LABELS[questionType] && (
            <span className={`question-type-badge ${questionType}`}>
              {TYPE_LABELS[questionType]}
            </span>
          )}
          <button
            className="btn btn-small"
            onClick={() => (isSpeaking ? cancel() : speak(questionText))}
          >
            {isSpeaking ? "Stop" : "Read Aloud"}
          </button>
        </div>
      </div>
      <p className="question-text">{questionText}</p>
    </div>
  );
}
