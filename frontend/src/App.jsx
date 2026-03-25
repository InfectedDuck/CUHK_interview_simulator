import { BrowserRouter, Routes, Route } from "react-router-dom";
import { HomePage } from "./pages/HomePage";
import { ProfilePage } from "./pages/ProfilePage";
import { InterviewPage } from "./pages/InterviewPage";
import { HistoryPage } from "./pages/HistoryPage";
import { ResultsPage } from "./pages/ResultsPage";

function App() {
  return (
    <BrowserRouter>
      <div className="app">
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/profile/:userId" element={<ProfilePage />} />
          <Route path="/interview/:userId" element={<InterviewPage />} />
          <Route path="/history/:userId" element={<HistoryPage />} />
          <Route path="/results/:userId/:sessionId" element={<ResultsPage />} />
        </Routes>
      </div>
    </BrowserRouter>
  );
}

export default App;
