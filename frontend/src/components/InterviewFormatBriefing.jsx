import { useState, useEffect } from "react";
import { api } from "../api/client";

export function InterviewFormatBriefing({ university, program }) {
  const [format, setFormat] = useState(null);

  useEffect(() => {
    if (university) {
      api.getInterviewFormat(university, program).then(setFormat).catch(() => {});
    }
  }, [university, program]);

  if (!format) return null;

  return (
    <div className="format-briefing card">
      <h3>Interview Format: {format.program}</h3>
      <p className="format-faculty">{format.faculty}</p>
      <div className="format-detail">
        <strong>Format:</strong> {format.format}
      </div>
      <div className="format-detail">
        <strong>What they value:</strong> {format.what_they_value}
      </div>
      <div className="format-competencies">
        <strong>Key competencies assessed:</strong>
        <div className="tags">
          {format.competencies?.map((c, i) => (
            <span key={i} className="tag">{c}</span>
          ))}
        </div>
      </div>
      <div className="format-tip">
        <strong>Tip:</strong> {format.tips}
      </div>
    </div>
  );
}
