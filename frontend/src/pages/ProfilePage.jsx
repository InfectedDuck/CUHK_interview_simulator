import { useState, useEffect } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { api } from "../api/client";
import { VoiceRecorder } from "../components/VoiceRecorder";
import { ProfileCard } from "../components/ProfileCard";

export function ProfilePage() {
  const { userId } = useParams();
  const navigate = useNavigate();
  const [user, setUser] = useState(null);
  const [profile, setProfile] = useState(null);
  const [loading, setLoading] = useState(true);
  const [extracting, setExtracting] = useState(false);
  const [error, setError] = useState(null);

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
        <h2>
          {profile ? "Update Your Profile" : "Create Your Profile"}
        </h2>
        <p>
          Speak about yourself — your education, skills, experience, goals, and
          target universities. The AI will extract your profile automatically.
        </p>
        <VoiceRecorder
          onTranscript={handleTranscript}
          placeholder="Tap the microphone and introduce yourself..."
        />
        {extracting && (
          <div className="loading">Analyzing your introduction...</div>
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
