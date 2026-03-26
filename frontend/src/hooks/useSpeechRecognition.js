import { useState, useRef, useCallback, useEffect } from "react";

const SpeechRecognition =
  window.SpeechRecognition || window.webkitSpeechRecognition;

export function useSpeechRecognition({ lang = "en-US", continuous = true } = {}) {
  const [transcript, setTranscript] = useState("");
  const [isListening, setIsListening] = useState(false);
  const [error, setError] = useState(null);
  const [isSupported] = useState(!!SpeechRecognition);
  const recognitionRef = useRef(null);
  const finalTranscriptRef = useRef("");
  const retryCountRef = useRef(0);
  const intentionalStopRef = useRef(false);
  const maxRetries = 3;

  useEffect(() => {
    return () => {
      intentionalStopRef.current = true;
      if (recognitionRef.current) {
        recognitionRef.current.abort();
      }
    };
  }, []);

  const createRecognition = useCallback(() => {
    const recognition = new SpeechRecognition();
    recognition.lang = lang;
    recognition.continuous = continuous;
    recognition.interimResults = true;
    recognition.maxAlternatives = 1;
    return recognition;
  }, [lang, continuous]);

  const startRecognition = useCallback((recognition) => {
    recognition.onstart = () => {
      setIsListening(true);
      setError(null);
      retryCountRef.current = 0; // Reset retries on successful start
    };

    recognition.onresult = (event) => {
      let interim = "";
      let finalText = "";
      for (let i = 0; i < event.results.length; i++) {
        const result = event.results[i];
        if (result.isFinal) {
          finalText += result[0].transcript + " ";
        } else {
          interim += result[0].transcript;
        }
      }
      finalTranscriptRef.current = finalText;
      setTranscript(finalText + interim);
    };

    recognition.onerror = (event) => {
      if (event.error === "aborted" || intentionalStopRef.current) {
        return;
      }

      // Auto-retry on "network" error — Chrome bug where the service
      // connection drops even with good internet
      if (event.error === "network" && retryCountRef.current < maxRetries) {
        retryCountRef.current++;
        setError(`Connecting to speech service... (attempt ${retryCountRef.current + 1})`);
        // Small delay then retry with a fresh instance
        setTimeout(() => {
          if (intentionalStopRef.current) return;
          try {
            const newRecognition = createRecognition();
            recognitionRef.current = newRecognition;
            startRecognition(newRecognition);
            newRecognition.start();
          } catch {
            setError("Speech recognition failed. Use the 'Type Instead' button.");
            setIsListening(false);
          }
        }, 500 * retryCountRef.current); // Increasing delay: 500ms, 1000ms, 1500ms
        return;
      }

      // "not-allowed" means mic permission denied
      if (event.error === "not-allowed") {
        setError("Microphone access denied. Please allow microphone in browser settings.");
      } else if (event.error === "network") {
        setError("Speech service unreachable after retries. Use the 'Type Instead' button.");
      } else {
        setError(`Speech recognition error: ${event.error}`);
      }
      setIsListening(false);
    };

    recognition.onend = () => {
      if (intentionalStopRef.current) {
        setIsListening(false);
        setTranscript(finalTranscriptRef.current.trim());
        return;
      }
      // In continuous mode, auto-restart if it stops unexpectedly
      // (Chrome sometimes stops after ~60s of silence)
      if (continuous && !intentionalStopRef.current && retryCountRef.current === 0) {
        try {
          recognition.start();
          return;
        } catch {
          // Falls through to stop
        }
      }
      setIsListening(false);
      setTranscript(finalTranscriptRef.current.trim());
    };
  }, [continuous, createRecognition]);

  const start = useCallback(() => {
    if (!SpeechRecognition) {
      setError("Speech recognition is not supported in this browser. Please use Chrome.");
      return;
    }

    // Request microphone permission first to avoid the "network" error
    // that sometimes happens when permissions aren't pre-granted
    navigator.mediaDevices?.getUserMedia({ audio: true })
      .then((stream) => {
        // Got permission — stop the stream immediately (we don't need it,
        // SpeechRecognition manages its own audio)
        stream.getTracks().forEach((t) => t.stop());

        setError(null);
        finalTranscriptRef.current = "";
        setTranscript("");
        intentionalStopRef.current = false;
        retryCountRef.current = 0;

        const recognition = createRecognition();
        recognitionRef.current = recognition;
        startRecognition(recognition);
        recognition.start();
      })
      .catch(() => {
        setError("Microphone access denied. Please allow microphone in browser settings, then try again.");
      });
  }, [createRecognition, startRecognition]);

  const stop = useCallback(() => {
    intentionalStopRef.current = true;
    if (recognitionRef.current) {
      recognitionRef.current.stop();
    }
  }, []);

  const reset = useCallback(() => {
    finalTranscriptRef.current = "";
    setTranscript("");
    setError(null);
  }, []);

  return { transcript, isListening, error, isSupported, start, stop, reset };
}
