import { Component } from "react";
import { BrowserRouter, Routes, Route, Link } from "react-router-dom";
import { HomePage } from "./pages/HomePage";
import { ProfilePage } from "./pages/ProfilePage";
import { InterviewPage } from "./pages/InterviewPage";
import { HistoryPage } from "./pages/HistoryPage";
import { ResultsPage } from "./pages/ResultsPage";
import { BriefingPage } from "./pages/BriefingPage";
import { AnalyticsPage } from "./pages/AnalyticsPage";
import { ReplayPage } from "./pages/ReplayPage";
import { ThemeToggle } from "./components/ThemeToggle";

class ErrorBoundary extends Component {
  state = { hasError: false, error: null };

  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="error-page">
          <h1>Something went wrong</h1>
          <p>{this.state.error?.message || "An unexpected error occurred."}</p>
          <button className="btn btn-primary" onClick={() => window.location.assign("/")}>
            Go Home
          </button>
        </div>
      );
    }
    return this.props.children;
  }
}

function NotFound() {
  return (
    <div className="error-page">
      <h1>404</h1>
      <p>Page not found.</p>
      <Link to="/" className="btn btn-primary">Go Home</Link>
    </div>
  );
}

function App() {
  return (
    <ErrorBoundary>
      <BrowserRouter>
        <div className="app">
          <header className="app-header no-print">
            <Link to="/" className="app-logo">Interview Tester</Link>
            <ThemeToggle />
          </header>
          <main>
            <Routes>
              <Route path="/" element={<HomePage />} />
              <Route path="/profile/:userId" element={<ProfilePage />} />
              <Route path="/interview/:userId" element={<InterviewPage />} />
              <Route path="/briefing/:userId" element={<BriefingPage />} />
              <Route path="/history/:userId" element={<HistoryPage />} />
              <Route path="/results/:userId/:sessionId" element={<ResultsPage />} />
              <Route path="/replay/:userId/:sessionId" element={<ReplayPage />} />
              <Route path="/analytics/:userId" element={<AnalyticsPage />} />
              <Route path="*" element={<NotFound />} />
            </Routes>
          </main>
        </div>
      </BrowserRouter>
    </ErrorBoundary>
  );
}

export default App;
