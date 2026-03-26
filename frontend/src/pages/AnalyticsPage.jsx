import { useState, useEffect } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { api } from "../api/client";
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend,
  RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, Radar,
  ResponsiveContainer,
} from "recharts";

export function AnalyticsPage() {
  const { userId } = useParams();
  const navigate = useNavigate();
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api
      .getAnalytics(parseInt(userId))
      .then(setData)
      .finally(() => setLoading(false));
  }, [userId]);

  if (loading) return <div className="loading">Analyzing your performance...</div>;

  if (!data || data.sessions_completed === 0) {
    return (
      <div className="page analytics-page">
        <div className="page-header">
          <button className="btn btn-back" onClick={() => navigate(`/profile/${userId}`)}>← Back</button>
          <h1>Analytics</h1>
        </div>
        <div className="card">
          <p>Complete at least one interview session to see analytics.</p>
          <button className="btn btn-primary" onClick={() => navigate(`/interview/${userId}`)}>
            Start Interview
          </button>
        </div>
      </div>
    );
  }

  const radarData = [
    { metric: "Content", value: data.category_averages.content },
    { metric: "Relevance", value: data.category_averages.relevance },
    { metric: "Clarity", value: data.category_averages.clarity },
  ];

  return (
    <div className="page analytics-page">
      <div className="page-header">
        <button className="btn btn-back" onClick={() => navigate(`/profile/${userId}`)}>← Back</button>
        <h1>Performance Analytics</h1>
      </div>

      {/* Summary Stats */}
      <div className="analytics-stats">
        <div className="stat-card card">
          <div className="stat-number">{data.sessions_completed}</div>
          <div className="stat-label">Sessions</div>
        </div>
        <div className="stat-card card">
          <div className="stat-number">{data.category_averages.content}</div>
          <div className="stat-label">Avg Content</div>
        </div>
        <div className="stat-card card">
          <div className="stat-number">{data.category_averages.relevance}</div>
          <div className="stat-label">Avg Relevance</div>
        </div>
        <div className="stat-card card">
          <div className="stat-number">{data.category_averages.clarity}</div>
          <div className="stat-label">Avg Clarity</div>
        </div>
      </div>

      {/* Improvement Velocity */}
      {data.improvement_velocity && Object.keys(data.improvement_velocity).length > 0 && (
        <div className="card">
          <h2>Improvement Velocity</h2>
          <div className="velocity-grid">
            {Object.entries(data.improvement_velocity).map(([key, val]) => (
              <div key={key} className={`velocity-item ${val > 0 ? "positive" : val < 0 ? "negative" : ""}`}>
                <span className="velocity-label">{key}</span>
                <span className="velocity-value">{val > 0 ? "+" : ""}{val}%</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Score Trend Chart */}
      {data.trends?.length > 1 && (
        <div className="card">
          <h2>Score Trends</h2>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={data.trends}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="date" tickFormatter={(d) => new Date(d).toLocaleDateString()} />
              <YAxis domain={[0, 10]} />
              <Tooltip />
              <Legend />
              <Line type="monotone" dataKey="content_avg" stroke="#2563eb" name="Content" />
              <Line type="monotone" dataKey="relevance_avg" stroke="#16a34a" name="Relevance" />
              <Line type="monotone" dataKey="clarity_avg" stroke="#d97706" name="Clarity" />
            </LineChart>
          </ResponsiveContainer>
        </div>
      )}

      {/* Radar Chart */}
      <div className="card">
        <h2>Skill Breakdown</h2>
        <ResponsiveContainer width="100%" height={300}>
          <RadarChart data={radarData}>
            <PolarGrid />
            <PolarAngleAxis dataKey="metric" />
            <PolarRadiusAxis domain={[0, 10]} />
            <Radar dataKey="value" stroke="#2563eb" fill="#2563eb" fillOpacity={0.3} />
          </RadarChart>
        </ResponsiveContainer>
      </div>

      {/* Strengths */}
      {data.strengths?.length > 0 && (
        <div className="card strengths-card">
          <h2>Your Strengths</h2>
          {data.strengths.map((s, i) => (
            <div key={i} className="strength-item">
              <strong>{s.strength}</strong>
              <p>{s.description}</p>
            </div>
          ))}
        </div>
      )}

      {/* Weaknesses */}
      {data.weaknesses?.length > 0 && (
        <div className="card weaknesses-card">
          <h2>Areas for Growth</h2>
          {data.weaknesses.map((w, i) => (
            <div key={i} className="weakness-item">
              <strong>{w.pattern}</strong>
              <p>{w.description}</p>
              {w.practice_suggestion && (
                <p className="practice-suggestion"><em>Practice:</em> {w.practice_suggestion}</p>
              )}
            </div>
          ))}
        </div>
      )}

      <div className="actions">
        <button className="btn btn-primary" onClick={() => navigate(`/interview/${userId}`)}>
          Practice Now
        </button>
        <button className="btn btn-secondary" onClick={() => navigate(`/history/${userId}`)}>
          View History
        </button>
      </div>
    </div>
  );
}
