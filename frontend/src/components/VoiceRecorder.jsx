import { useState } from "react";
import { useAudioRecorder } from "../hooks/useAudioRecorder";
import { api } from "../api/client";

const LANGUAGES = [
  { code: "en", label: "English" },
  { code: "zh", label: "Mandarin" },
  { code: "yue", label: "Cantonese" },
];

export function VoiceRecorder({ onTranscript, placeholder = "Your speech will appear here...", userId, context }) {
  const { startRecording, stopRecording, isRecording, duration, error: recError } = useAudioRecorder();
  const [transcript, setTranscript] = useState("");
  const [transcribing, setTranscribing] = useState(false);
  const [error, setError] = useState(null);
  const [useTextInput, setUseTextInput] = useState(false);
  const [textValue, setTextValue] = useState("");
  const [language, setLanguage] = useState("en");

  const handleStop = async () => {
    const blob = await stopRecording();
    if (!blob || blob.size === 0) {
      setError("No audio recorded");
      return;
    }

    setTranscribing(true);
    setError(null);
    try {
      const result = await api.transcribe(blob, { userId, context, language });
      setTranscript(result.text);
    } catch (e) {
      setError(e.message);
    } finally {
      setTranscribing(false);
    }
  };

  const handleSubmit = () => {
    if (transcript.trim()) {
      onTranscript?.(transcript.trim());
      setTranscript("");
    }
  };

  const handleTextSubmit = () => {
    if (textValue.trim()) {
      onTranscript?.(textValue.trim());
      setTextValue("");
    }
  };

  const handleClear = () => {
    setTranscript("");
    setError(null);
  };

  const formatDuration = (s) => `${Math.floor(s / 60)}:${(s % 60).toString().padStart(2, "0")}`;

  const langSelector = (
    <select
      className="lang-select"
      value={language}
      onChange={(e) => setLanguage(e.target.value)}
    >
      {LANGUAGES.map((l) => (
        <option key={l.code} value={l.code}>{l.label}</option>
      ))}
    </select>
  );

  // Text input mode
  if (useTextInput) {
    return (
      <div className="voice-recorder text-mode">
        <div className="voice-controls">
          <button className="btn btn-secondary" onClick={() => setUseTextInput(false)}>
            Switch to Voice
          </button>
        </div>
        <textarea
          className="text-input"
          placeholder="Type your response here... (Ctrl+Enter to submit)"
          value={textValue}
          onChange={(e) => setTextValue(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && e.ctrlKey && handleTextSubmit()}
          rows={4}
        />
        <button className="btn btn-primary" onClick={handleTextSubmit} disabled={!textValue.trim()}>
          Submit Answer
        </button>
      </div>
    );
  }

  // Voice input mode (Whisper)
  return (
    <div className="voice-recorder">
      <div className="voice-controls">
        {!isRecording ? (
          <button className="btn mic-btn" onClick={startRecording} disabled={transcribing}>
            Start Speaking
          </button>
        ) : (
          <button className="btn mic-btn listening" onClick={handleStop}>
            Stop ({formatDuration(duration)})
          </button>
        )}
        {transcript && !isRecording && (
          <>
            <button className="btn btn-primary" onClick={handleSubmit}>Submit</button>
            <button className="btn btn-secondary" onClick={handleClear}>Clear</button>
          </>
        )}
        {langSelector}
        <button className="btn btn-secondary" onClick={() => setUseTextInput(true)}>
          Type Instead
        </button>
      </div>

      {isRecording && (
        <div className="listening-indicator">Recording... {formatDuration(duration)}</div>
      )}

      {transcribing && (
        <div className="loading-skeleton">
          <div className="skeleton-text" />
          <div className="skeleton-text short" />
        </div>
      )}

      {(recError || error) && <div className="error-text">{recError || error}</div>}

      <div className="transcript-box">
        {transcript || <span className="placeholder">{placeholder}</span>}
      </div>
    </div>
  );
}
