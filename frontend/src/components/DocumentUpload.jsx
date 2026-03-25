import { useState, useRef } from "react";

const DOC_TYPES = [
  { value: "CV/Resume", label: "CV / Resume" },
  { value: "Personal Statement", label: "Personal Statement" },
  { value: "Essay", label: "Essay" },
  { value: "Cover Letter", label: "Cover Letter" },
  { value: "document", label: "Other Document" },
];

const ALLOWED_EXTENSIONS = [".pdf", ".docx", ".doc", ".txt", ".md"];

export function DocumentUpload({ userId, onProfileUpdate, disabled }) {
  const [docType, setDocType] = useState("CV/Resume");
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState(null);
  const [fileName, setFileName] = useState(null);
  const fileRef = useRef(null);

  const handleFileChange = (e) => {
    const file = e.target.files[0];
    if (!file) return;

    const ext = "." + file.name.split(".").pop().toLowerCase();
    if (!ALLOWED_EXTENSIONS.includes(ext)) {
      setError(`Unsupported file type. Allowed: ${ALLOWED_EXTENSIONS.join(", ")}`);
      setFileName(null);
      return;
    }
    setError(null);
    setFileName(file.name);
  };

  const handleUpload = async () => {
    const file = fileRef.current?.files[0];
    if (!file) return;

    setUploading(true);
    setError(null);

    const formData = new FormData();
    formData.append("file", file);
    formData.append("user_id", userId);
    formData.append("doc_type", docType);

    try {
      const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";
      const res = await fetch(`${API_URL}/api/profile/upload`, {
        method: "POST",
        body: formData,
      });
      if (!res.ok) {
        const err = await res.json().catch(() => ({ detail: res.statusText }));
        throw new Error(err.detail || "Upload failed");
      }
      const profile = await res.json();
      onProfileUpdate?.(profile);
      setFileName(null);
      if (fileRef.current) fileRef.current.value = "";
    } catch (e) {
      setError(e.message);
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="document-upload">
      <div className="upload-row">
        <select
          value={docType}
          onChange={(e) => setDocType(e.target.value)}
          className="doc-type-select"
        >
          {DOC_TYPES.map((t) => (
            <option key={t.value} value={t.value}>{t.label}</option>
          ))}
        </select>
        <label className="file-input-label">
          {fileName || "Choose file..."}
          <input
            ref={fileRef}
            type="file"
            accept=".pdf,.docx,.doc,.txt,.md"
            onChange={handleFileChange}
            hidden
          />
        </label>
        <button
          className="btn btn-primary"
          onClick={handleUpload}
          disabled={!fileName || uploading || disabled}
        >
          {uploading ? "Analyzing..." : "Upload & Analyze"}
        </button>
      </div>
      <p className="upload-hint">Supported: PDF, DOCX, TXT. Your profile will be enriched with each upload.</p>
      {error && <div className="error-text">{error}</div>}
    </div>
  );
}
