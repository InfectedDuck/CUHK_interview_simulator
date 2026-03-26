import { useState, useEffect } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { api } from "../api/client";
import { VoiceRecorder } from "../components/VoiceRecorder";
import { DocumentUpload } from "../components/DocumentUpload";
import { ProfileCard } from "../components/ProfileCard";

export function ProfilePage() {
  const { userId } = useParams();
  const navigate = useNavigate();
  const [user, setUser] = useState(null);
  const [profile, setProfile] = useState(null);
  const [loading, setLoading] = useState(true);
  const [extracting, setExtracting] = useState(false);
  const [error, setError] = useState(null);
  const [inputMode, setInputMode] = useState("voice"); // "voice" | "upload"

  useEffect(() => {
    const load = async () => {
      try {
        const u = await api.getUser(userId);
        setUser(u);
        try {
          const p = await api.getProfile(userId);
          setProfile(p);
        } catch {
          // No profile yet
        }
      } catch (e) {
        setError(e.message);
      } finally {
        setLoading(false);
      }
    };
    load();
  }, [userId]);

  const handleTranscript = async (transcript) => {
    setExtracting(true);
    setError(null);
    try {
      const p = await api.extractProfile(parseInt(userId), transcript);
      setProfile(p);
    } catch (e) {
      setError(e.message);
    } finally {
      setExtracting(false);
    }
  };

  if (loading) return <div className="loading">Loading...</div>;
  if (error && !user) return <div className="error-text">{error}</div>;

  return (
    <div className="page profile-page">
      <div className="page-header">
        <button className="btn btn-back" onClick={() => navigate("/")}>
          ← Back
        </button>
        <h1>Welcome, {user?.name}</h1>
      </div>

      <div className="card">
        <h2>{profile ? "Update Your Profile" : "Create Your Profile"}</h2>
        <p>
          Build your profile by speaking about yourself or uploading documents.
          Each input enriches your profile — you can use both!
        </p>

        <div className="input-mode-tabs">
          <button
            className={`tab ${inputMode === "voice" ? "active" : ""}`}
            onClick={() => setInputMode("voice")}
          >
            🎤 Voice Introduction
          </button>
          <button
            className={`tab ${inputMode === "upload" ? "active" : ""}`}
            onClick={() => setInputMode("upload")}
          >
            📄 Upload Document
          </button>
        </div>

        {inputMode === "voice" ? (
          <div className="input-section">
            <p className="input-hint">
              Speak about your education, skills, experience, goals, and target universities.
            </p>
            <VoiceRecorder
              onTranscript={handleTranscript}
              userId={parseInt(userId)}
              placeholder="Tap the microphone and introduce yourself..."
            />
            {extracting && (
              <div className="loading">Analyzing your introduction...</div>
            )}
          </div>
        ) : (
          <div className="input-section">
            <p className="input-hint">
              Upload your CV, personal statement, essay, or any relevant document.
              The AI will extract information and add it to your profile.
            </p>
            <DocumentUpload
              userId={parseInt(userId)}
              onProfileUpdate={setProfile}
              disabled={extracting}
            />
          </div>
        )}

        {error && <div className="error-text">{error}</div>}
      </div>

      {profile && (
        <>
          <ProfileCard profile={profile} />
          <div className="actions">
            <button
              className="btn btn-primary"
              onClick={() => navigate(`/interview/${userId}`)}
            >
              Start Interview Practice
            </button>
            <button
              className="btn btn-secondary"
              onClick={() => navigate(`/history/${userId}`)}
            >
              View History
            </button>
          </div>
        </>
      )}
    </div>
  );
}
