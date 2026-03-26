import { useState, useEffect } from "react";
import { api } from "../api/client";

export function CUHKProgramSelector({ university, program, onProgramChange }) {
  const [programs, setPrograms] = useState([]);

  useEffect(() => {
    if (university?.toUpperCase().includes("CUHK")) {
      api.getPrograms().then((data) => setPrograms(data.programs)).catch(() => {});
    }
  }, [university]);

  if (!university?.toUpperCase().includes("CUHK")) return null;

  return (
    <div className="program-selector">
      <label htmlFor="program">Target Program / Faculty</label>
      <select
        id="program"
        value={program || ""}
        onChange={(e) => onProgramChange(e.target.value)}
      >
        <option value="">Select a program...</option>
        {programs.map((p) => (
          <option key={p} value={p}>{p}</option>
        ))}
      </select>
    </div>
  );
}
