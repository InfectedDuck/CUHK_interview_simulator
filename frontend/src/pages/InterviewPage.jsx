import { useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { api } from "../api/client";
import { UniversitySelector } from "../components/UniversitySelector";
import { QuestionCard } from "../components/QuestionCard";
import { VoiceRecorder } from "../components/VoiceRecorder";
import { FeedbackPanel } from "../components/FeedbackPanel";
import { ScoreBoard } from "../components/ScoreBoard";

const MAX_QUESTIONS = 5;

export function InterviewPage() {
  const { userId } = useParams();
  const navigate = useNavigate();

  const [university, setUniversity] = useState("");
  const [sessionId, setSessionId] = useState(null);
  const [currentQuestion, setCurrentQuestion] = useState(null);
  const [feedback, setFeedback] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // Session complete state
  const [complete, setComplete] = useState(false);
  const [overallScore, setOverallScore] = useState(null);
  const [summaryFeedback, setSummaryFeedback] = useState(null);
  const [exchanges, setExchanges] = useState([]);

  const startInterview = async () => {
    if (!university) return;
    setLoading(true);
    setError(null);
    try {
      const res = await api.startInterview(parseInt(userId), university);
      setSessionId(res.session_id);
      setCurrentQuestion(res);
      setFeedback(null);
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  };

  const handleAnswer = async (answerText) => {
    if (!sessionId) return;
    setLoading(true);
    setError(null);
    try {
      const res = await api.submitAnswer(sessionId, answerText);
      setFeedback(res.feedback);

      if (res.session_complete) {
        setComplete(true);
        setOverallScore(res.overall_score);
        setSummaryFeedback(res.summary_feedback);
        // Load full session for breakdown
        const session = await api.getSession(parseInt(userId), sessionId);
        setExchanges(session.exchanges || []);
      } else if (res.next_question) {
        setCurrentQuestion(res.next_question);
      }
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  };

  const handleNextQuestion = () => {
    setFeedback(null);
  };

  const endEarly = async () => {
    if (!sessionId) return;
    await api.endInterview(sessionId);
    navigate(`/history/${userId}`);
  };

  // Interview complete view
  if (complete) {
    return (
      <div className="page interview-page">
        <ScoreBoard
          overallScore={overallScore}
          summaryFeedback={summaryFeedback}
          exchanges={exchanges}
        />
        <div className="actions">
          <button className="btn btn-primary" onClick={() => navigate(`/interview/${userId}`)}>
            Try Again
          </button>
          <button className="btn btn-secondary" onClick={() => navigate(`/history/${userId}`)}>
            View History
          </button>
          <button className="btn btn-back" onClick={() => navigate("/")}>
            Home
          </button>
        </div>
      </div>
    );
  }

  // Pre-interview: select university
  if (!sessionId) {
    return (
      <div className="page interview-page">
        <div className="page-header">
          <button className="btn btn-back" onClick={() => navigate(`/profile/${userId}`)}>
            ← Back
          </button>
          <h1>Start Interview</h1>
        </div>
        <div className="card">
          <UniversitySelector value={university} onChange={setUniversity} />
          <button
            className="btn btn-primary"
            onClick={startInterview}
            disabled={!university || loading}
          >
            {loading ? "Starting..." : "Begin Interview"}
          </button>
          {error && <div className="error-text">{error}</div>}
        </div>
      </div>
    );
  }

  // Active interview
  return (
    <div className="page interview-page">
      <div className="page-header">
        <h1>Interview — {university}</h1>
        <button className="btn btn-danger" onClick={endEarly}>
          End Early
        </button>
      </div>

      {currentQuestion && (
        <QuestionCard
          questionNumber={currentQuestion.question_number}
          totalQuestions={MAX_QUESTIONS}
          questionText={currentQuestion.question_text}
        />
      )}

      {feedback && !loading ? (
        <div>
          <FeedbackPanel feedback={feedback} />
          <button className="btn btn-primary" onClick={handleNextQuestion}>
            Next Question
          </button>
        </div>
      ) : (
        <div className="card">
          <h3>Your Answer</h3>
          <VoiceRecorder
            onTranscript={handleAnswer}
            placeholder="Tap the microphone and speak your answer..."
          />
          {loading && <div className="loading">Analyzing your response...</div>}
        </div>
      )}

      {error && <div className="error-text">{error}</div>}
    </div>
  );
}
