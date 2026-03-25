import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { api } from "../api/client";

export function HomePage() {
  const [users, setUsers] = useState([]);
  const [newName, setNewName] = useState("");
  const [loading, setLoading] = useState(true);
  const [health, setHealth] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    Promise.all([api.listUsers(), api.health()])
      .then(([u, h]) => {
        setUsers(u);
        setHealth(h);
      })
      .catch(() => setHealth({ status: "error", ollama: "disconnected" }))
      .finally(() => setLoading(false));
  }, []);

  const handleCreate = async (e) => {
    e.preventDefault();
    if (!newName.trim()) return;
    const user = await api.createUser(newName.trim());
    setNewName("");
    navigate(`/profile/${user.id}`);
  };

  const selectUser = (userId) => {
    navigate(`/profile/${userId}`);
  };

  if (loading) return <div className="loading">Loading...</div>;

  return (
    <div className="page home-page">
      <h1>Interview Tester</h1>
      <p className="subtitle">Practice university admission interviews with AI</p>

      {health && health.ollama !== "connected" && (
        <div className="banner warning">
          ⚠ Ollama is not running. Start Ollama to enable AI features.
        </div>
      )}
      {health && health.ollama === "connected" && (
        <div className="banner success">
          ✓ Connected to Ollama (model: {health.model})
        </div>
      )}

      <div className="card">
        <h2>Get Started</h2>
        <form onSubmit={handleCreate} className="create-form">
          <input
            type="text"
            placeholder="Enter your name"
            value={newName}
            onChange={(e) => setNewName(e.target.value)}
          />
          <button className="btn btn-primary" type="submit">
            Create Profile
          </button>
        </form>
      </div>

      {users.length > 0 && (
        <div className="card">
          <h2>Existing Users</h2>
          <div className="user-list">
            {users.map((user) => (
              <button
                key={user.id}
                className="user-item"
                onClick={() => selectUser(user.id)}
              >
                <span className="user-name">{user.name}</span>
                <span className="user-date">{new Date(user.created_at).toLocaleDateString()}</span>
              </button>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
