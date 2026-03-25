import { useSpeechRecognition } from "../hooks/useSpeechRecognition";

export function VoiceRecorder({ onTranscript, placeholder = "Your speech will appear here..." }) {
  const { transcript, isListening, error, isSupported, start, stop, reset } =
    useSpeechRecognition();

  const handleStop = () => {
    stop();
    if (transcript.trim()) {
      onTranscript?.(transcript.trim());
    }
  };

  if (!isSupported) {
    return (
      <div className="voice-recorder unsupported">
        <p>⚠ Speech recognition not supported. Please use Chrome or Edge.</p>
        <textarea
          placeholder="Type your response here instead..."
          onChange={(e) => onTranscript?.(e.target.value)}
          rows={4}
        />
      </div>
    );
  }

  return (
    <div className="voice-recorder">
      <div className="voice-controls">
        {!isListening ? (
          <button className="btn mic-btn" onClick={start}>
            🎤 Start Speaking
          </button>
        ) : (
          <button className="btn mic-btn listening" onClick={handleStop}>
            ⏹ Stop
          </button>
        )}
        {transcript && (
          <button className="btn btn-secondary" onClick={reset}>
            Clear
          </button>
        )}
      </div>
      {isListening && <div className="listening-indicator">Listening...</div>}
      {error && <div className="error-text">{error}</div>}
      <div className="transcript-box">
        {transcript || <span className="placeholder">{placeholder}</span>}
      </div>
    </div>
  );
}
