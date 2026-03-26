import { useState, useRef, useCallback } from "react";
import { useParams, useNavigate, useSearchParams } from "react-router-dom";
import { api } from "../api/client";
import { UniversitySelector } from "../components/UniversitySelector";
import { CUHKProgramSelector } from "../components/CUHKProgramSelector";
import { InterviewFormatBriefing } from "../components/InterviewFormatBriefing";
import { QuestionCard } from "../components/QuestionCard";
import { VoiceRecorder } from "../components/VoiceRecorder";
import { FeedbackPanel } from "../components/FeedbackPanel";
import { ScoreBoard } from "../components/ScoreBoard";
import { InterviewTimer } from "../components/InterviewTimer";
import { AnswerComparisonPanel } from "../components/AnswerComparisonPanel";

export function InterviewPage() {
  const { userId } = useParams();
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();

  const [university, setUniversity] = useState(searchParams.get("university") || "");
  const [program, setProgram] = useState(searchParams.get("program") || "");
  const [mode, setMode] = useState(searchParams.get("mode") || "practice");
  const [difficulty, setDifficulty] = useState("medium");
  const [sessionId, setSessionId] = useState(null);
  const [currentQuestion, setCurrentQuestion] = useState(null);
  const [maxQuestions, setMaxQuestions] = useState(5);
  const [feedback, setFeedback] = useState(null);
  const [currentExchangeId, setCurrentExchangeId] = useState(null);
  const [currentAnswerText, setCurrentAnswerText] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // Simulation mode state
  const [timerActive, setTimerActive] = useState(false);
  const questionStartRef = useRef(null);

  // Session complete state
  const [complete, setComplete] = useState(false);
  const [overallScore, setOverallScore] = useState(null);
  const [summaryFeedback, setSummaryFeedback] = useState(null);
  const [exchanges, setExchanges] = useState([]);

  const readyFromBriefing = searchParams.get("ready") === "1";

  const startInterview = async () => {
    if (!university) return;
    setLoading(true);
    setError(null);
    try {
      const res = await api.startInterview(parseInt(userId), university, program || null, mode, difficulty);
      setSessionId(res.session_id);
      setCurrentQuestion(res);
      setMaxQuestions(res.max_questions || 5);
      setFeedback(null);
      questionStartRef.current = Date.now();
      if (mode === "simulation") setTimerActive(true);
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  };

  const handleAnswer = async (answerText) => {
    if (!sessionId) return;
    setTimerActive(false);
    const responseTime = questionStartRef.current
      ? (Date.now() - questionStartRef.current) / 1000
      : null;

    setLoading(true);
    setError(null);
    setCurrentAnswerText(answerText);
    try {
      const res = await api.submitAnswer(sessionId, answerText, responseTime);
      setFeedback(res.feedback);

      // Track exchange ID for the improve button
      const session = await api.getSession(parseInt(userId), sessionId);
      const answered = session.exchanges?.filter((e) => e.answer_text);
      if (answered?.length > 0) {
        setCurrentExchangeId(answered[answered.length - 1].id);
      }

      if (res.session_complete) {
        setComplete(true);
        setOverallScore(res.overall_score);
        setSummaryFeedback(res.summary_feedback);
        setExchanges(session.exchanges || []);
      } else if (res.next_question) {
        setCurrentQuestion(res.next_question);
        if (res.next_question.max_questions) {
          setMaxQuestions(res.next_question.max_questions);
        }
      }
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  };

  const handleTimeUp = useCallback((elapsed) => {
    // In simulation mode, auto-submit with what we have
    setTimerActive(false);
  }, []);

  const handleNextQuestion = () => {
    setFeedback(null);
    setCurrentExchangeId(null);
    setCurrentAnswerText(null);
    questionStartRef.current = Date.now();
    if (mode === "simulation") setTimerActive(true);
  };

  const endEarly = async () => {
    if (!sessionId) return;
    await api.endInterview(sessionId);
    navigate(`/history/${userId}`);
  };

  const goToBriefing = () => {
    navigate(
      `/briefing/${userId}?university=${encodeURIComponent(university)}&program=${encodeURIComponent(program)}&mode=${mode}`
    );
  };

  // Interview complete view
  if (complete) {
    return (
      <div className="page interview-page">
        <ScoreBoard
          overallScore={overallScore}
          summaryFeedback={summaryFeedback}
          exchanges={exchanges}
          sessionId={sessionId}
        />
        <div className="actions">
          <button className="btn btn-primary" onClick={() => navigate(`/replay/${userId}/${sessionId}`)}>
            Replay & Improve Answers
          </button>
          <button className="btn btn-secondary" onClick={() => { setComplete(false); setSessionId(null); }}>
            Try Again
          </button>
          <button className="btn btn-secondary" onClick={() => navigate(`/analytics/${userId}`)}>
            View Analytics
          </button>
          <button className="btn btn-back" onClick={() => navigate("/")}>Home</button>
        </div>
      </div>
    );
  }

  // Pre-interview: select university, program, mode
  if (!sessionId) {
    return (
      <div className="page interview-page">
        <div className="page-header">
          <button className="btn btn-back" onClick={() => navigate(`/profile/${userId}`)}>← Back</button>
          <h1>Start Interview</h1>
        </div>

        <div className="card">
          <UniversitySelector value={university} onChange={setUniversity} />
          <CUHKProgramSelector
            university={university}
            program={program}
            onProgramChange={setProgram}
          />

          {/* Mode Selector */}
          <div className="mode-selector">
            <label>Interview Mode</label>
            <div className="mode-options">
              <button
                className={`mode-option ${mode === "practice" ? "active" : ""}`}
                onClick={() => setMode("practice")}
              >
                <strong>Practice</strong>
                <span>Relaxed pace, detailed feedback after each answer</span>
              </button>
              <button
                className={`mode-option ${mode === "simulation" ? "active" : ""}`}
                onClick={() => setMode("simulation")}
              >
                <strong>Simulation</strong>
                <span>2-min timer, auto-read questions, real interview pressure</span>
              </button>
            </div>
          </div>

          {/* Difficulty Selector */}
          <div className="mode-selector">
            <label>Difficulty</label>
            <div className="mode-options three-col">
              {[
                { key: "easy", title: "Easy", desc: "Encouraging questions, simple vocabulary" },
                { key: "medium", title: "Medium", desc: "Balanced depth, fair challenge" },
                { key: "hard", title: "Hard", desc: "Devil's advocate, multi-layered, tough" },
              ].map((d) => (
                <button
                  key={d.key}
                  className={`mode-option ${difficulty === d.key ? "active" : ""}`}
                  onClick={() => setDifficulty(d.key)}
                >
                  <strong>{d.title}</strong>
                  <span>{d.desc}</span>
                </button>
              ))}
            </div>
          </div>

          {university && <InterviewFormatBriefing university={university} program={program} />}

          <div className="actions">
            {university && (
              <button className="btn btn-secondary" onClick={goToBriefing}>
                Get Strategy Briefing First
              </button>
            )}
            <button
              className="btn btn-primary"
              onClick={startInterview}
              disabled={!university || loading}
            >
              {loading ? "Starting..." : readyFromBriefing ? "Begin Interview" : "Start Interview"}
            </button>
          </div>
          {error && <div className="error-text">{error}</div>}
        </div>
      </div>
    );
  }

  // Active interview
  return (
    <div className="page interview-page">
      <div className="page-header">
        <h1>
          {university} {program ? `— ${program}` : ""}
          {mode === "simulation" && <span className="mode-badge simulation">SIMULATION</span>}
        </h1>
        <button className="btn btn-danger" onClick={endEarly}>End Early</button>
      </div>

      {/* Timer for simulation mode */}
      {mode === "simulation" && (
        <InterviewTimer
          duration={120}
          active={timerActive}
          onTimeUp={handleTimeUp}
        />
      )}

      {currentQuestion && (
        <QuestionCard
          questionNumber={currentQuestion.question_number}
          totalQuestions={maxQuestions}
          questionText={currentQuestion.question_text}
          questionType={currentQuestion.question_type}
          autoSpeak={mode === "simulation"}
        />
      )}

      {feedback && !loading ? (
        <div>
          <FeedbackPanel feedback={feedback} mode={mode} />

          {/* Answer improvement coach */}
          {currentExchangeId && currentAnswerText && (
            <AnswerComparisonPanel
              sessionId={sessionId}
              exchangeId={currentExchangeId}
              originalAnswer={currentAnswerText}
            />
          )}

          <button className="btn btn-primary" onClick={handleNextQuestion}>
            Next Question
          </button>
        </div>
      ) : (
        <div className="card">
          <h3>Your Answer</h3>
          <VoiceRecorder
            onTranscript={handleAnswer}
            userId={parseInt(userId)}
            context={currentQuestion ? `Interview question: ${currentQuestion.question_text}` : ""}
            placeholder="Tap the microphone and speak your answer..."
          />
          {loading && <div className="loading">Analyzing your response...</div>}
        </div>
      )}

      {error && <div className="error-text">{error}</div>}
    </div>
  );
}
