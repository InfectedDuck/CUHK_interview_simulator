import { useState, useEffect, useRef, useCallback } from "react";

export function InterviewTimer({ duration = 120, onTimeUp, active }) {
  const [remaining, setRemaining] = useState(duration);
  const intervalRef = useRef(null);
  const startTimeRef = useRef(null);

  const getElapsed = useCallback(() => {
    if (!startTimeRef.current) return 0;
    return (Date.now() - startTimeRef.current) / 1000;
  }, []);

  useEffect(() => {
    if (active) {
      startTimeRef.current = Date.now();
      setRemaining(duration);
      intervalRef.current = setInterval(() => {
        const elapsed = (Date.now() - startTimeRef.current) / 1000;
        const left = Math.max(0, duration - elapsed);
        setRemaining(left);
        if (left <= 0) {
          clearInterval(intervalRef.current);
          onTimeUp?.(elapsed);
        }
      }, 250);
    } else {
      clearInterval(intervalRef.current);
    }
    return () => clearInterval(intervalRef.current);
  }, [active, duration, onTimeUp]);

  const minutes = Math.floor(remaining / 60);
  const seconds = Math.floor(remaining % 60);
  const progress = remaining / duration;

  let urgency = "green";
  if (progress < 0.25) urgency = "red";
  else if (progress < 0.5) urgency = "yellow";

  return (
    <div className={`interview-timer ${urgency} ${active ? "active" : ""}`}>
      <div className="timer-display">
        {minutes}:{seconds.toString().padStart(2, "0")}
      </div>
      <div className="timer-bar">
        <div className="timer-fill" style={{ width: `${progress * 100}%` }} />
      </div>
    </div>
  );
}
