import { useSpeechSynthesis } from "../hooks/useSpeechSynthesis";

export function QuestionCard({ questionNumber, totalQuestions, questionText }) {
  const { speak, cancel, isSpeaking } = useSpeechSynthesis();

  return (
    <div className="question-card">
      <div className="question-header">
        <span className="question-number">
          Question {questionNumber} of {totalQuestions}
        </span>
        <button
          className="btn btn-small"
          onClick={() => (isSpeaking ? cancel() : speak(questionText))}
        >
          {isSpeaking ? "⏹ Stop" : "🔊 Read Aloud"}
        </button>
      </div>
      <p className="question-text">{questionText}</p>
    </div>
  );
}
