# Interview Tester

**An AI-powered university admission interview preparation platform built specifically for Hong Kong's top universities, with deep intelligence for CUHK.**

Students upload their CV, speak their introduction, and practice realistic admission interviews with an AI interviewer that adapts to their answers, probes deeper on weak responses, asks about their specific projects, and provides professional-grade coaching feedback — all running locally with zero cloud dependencies.

---

## Why This Project Exists

University admission interviews are high-stakes and unpredictable. Students often prepare by memorizing answers, which interviewers easily detect. Professional interview coaches charge HK$1,500+/hour and are inaccessible to most students.

This platform replicates what a top-tier interview coach does:
- Builds a deep understanding of the student from their CV, essays, and voice introduction
- Conducts a natural conversation (not a quiz) that adapts in real-time
- Provides specific, actionable feedback — not just "be more specific" but a rewritten version of your actual answer showing you exactly what better looks like
- Tracks progress across sessions and identifies recurring patterns

---

## Architecture Overview

```
+------------------+         +------------------+         +------------------+
|                  |  Audio  |                  |  HTTP   |                  |
|   React Frontend |-------->|  FastAPI Backend  |-------->|   Ollama (LLM)   |
|   (Vite + JSX)   |<--------|  (Python 3.14)   |<--------|   Mistral 7B     |
|                  |  JSON   |                  |         |                  |
+------------------+         +--------+---------+         +------------------+
                                      |
                              +-------+-------+
                              |               |
                        +-----+-----+   +-----+-----+
                        |  SQLite   |   |  Whisper   |
                        |  Database |   |  STT (CPU) |
                        +-----------+   +-----------+
```

| Layer | Technology | Purpose |
|-------|-----------|---------|
| Frontend | React 19 + Vite | Interactive web UI with voice recording |
| Backend | FastAPI + Python 3.14 | API server, AI orchestration, document parsing |
| LLM | Ollama (local) or OpenRouter (cloud) | Question generation, answer analysis, coaching |
| Speech-to-Text | faster-whisper (base) | Local audio transcription with AI correction |
| Database | SQLite + aiosqlite | Session history, profiles, analytics |
| Document Parser | pdfplumber + python-docx | CV/essay text extraction |

**Dual mode:** Runs fully local with Ollama (no API keys, no data leaves the machine), or deploys to the cloud with OpenRouter using free models.

---

## Core Features

### 1. Intelligent Profile Building

Students can build their profile through multiple channels — the system merges everything intelligently:

| Input Method | What It Extracts |
|-------------|-----------------|
| Voice Introduction | Education, skills, goals, target universities |
| CV/Resume Upload (PDF/DOCX) | Projects, experience, achievements, technologies |
| Personal Statement | Personality traits, interests, motivations |
| Essay Upload | Writing style, intellectual interests, values |

The AI extracts structured data from unstructured input:

```
Uploaded CV  ──>  AI Profile Extraction  ──>  Structured Profile
                                               ├── Education (level, institution, major, GPA)
                                               ├── Skills ["Python", "React", "Data Analysis"]
                                               ├── Experience [{title, org, description}]
                                               ├── Projects [{name, description, technologies,
                                               │              role, outcome}]
                                               ├── Goals
                                               ├── Achievements
                                               ├── Interests
                                               └── Personality Traits
```

Each upload enriches the existing profile — uploading a CV then a personal statement combines information from both without losing anything.

---

### 2. Conversational Interview Engine

This is not a quiz with 5 random questions. The AI conducts a real conversation:

```
Question Strategy Flow:

  Q1 [WARMUP]     "Tell me about yourself and what brings you to CUHK."
       │
       ▼ Student answers well (score: 8.2/10)
       │
  Q2 [CHALLENGE]   "You mentioned your event management system project.
       │            What was the most difficult technical decision you made,
       │            and would you make the same choice today?"
       │
       ▼ Student gives vague answer (score: 4.5/10)
       │
  Q3 [FOLLOW-UP]   "I'd love to hear more specifics — can you walk me through
       │            one concrete example of a trade-off you faced in that project?"
       │
       ▼ Student elaborates well (score: 7.8/10)
       │
  Q4 [CHALLENGE]   "How do you think the skills you developed in that project
       │            connect to CUHK's emphasis on social responsibility?"
       │
       ▼ ...continues adapting...
       │
  Q5 [CLOSING]     "If you could contribute one thing to the CUHK community,
                    what would it be?"
```

**How it adapts:**

| Previous Score | Strategy | Behavior |
|---------------|----------|----------|
| < 5.0 | Follow-up | Gives the student another chance to elaborate, references their specific answer |
| 5.0 - 7.0 | Probe | Asks for a concrete example or deeper reflection |
| > 7.0 | Challenge | Advances to a harder topic, tests critical thinking |
| Final question | Closing | Forward-looking, memorable, gives student a strong finish |

**Dynamic session length:** If a student struggles badly (avg < 4.5), the system automatically adds follow-up questions (up to 8 total) to give them a fair chance.

---

### 3. CUHK Deep Knowledge System

The platform contains a structured knowledge base covering 9 CUHK programs with insider-level intelligence:

```
CUHK Knowledge Base
├── Core Values
│   ├── Whole Person Development (博文約禮)
│   ├── Bilingualism (Chinese + English)
│   ├── Social Responsibility
│   └── Tradition & Innovation
│
├── 9 Colleges
│   ├── Chung Chi (Christian values, service)
│   ├── New Asia (Chinese heritage, philosophy)
│   ├── United (Social engagement)
│   ├── Shaw (Innovation, entrepreneurship)
│   └── ... 5 more
│
└── 9 Programs with Deep Insight
    ├── Medicine
    │   ├── Format: MMI (6-8 stations, 8 min each)
    │   ├── Competencies: empathy, ethical reasoning, teamwork...
    │   ├── Red Flags: memorized answers, lack of self-awareness
    │   └── Insider Tips: "Think aloud — they want your reasoning
    │                      process, not just your conclusion"
    ├── Business Administration
    │   ├── Format: Individual interview + group discussion
    │   └── ...
    ├── Law
    ├── Engineering
    ├── Science
    ├── Social Science
    ├── Arts
    ├── Education
    └── General / Undecided
```

This knowledge is injected into:
- **Question generation** — questions match the program's interview style
- **Response scoring** — answers are evaluated against program-specific rubrics
- **Strategy briefings** — advice is tailored to what each faculty actually looks for

---

### 4. Multi-Dimensional Scoring

Every answer is scored across up to 6 dimensions:

```
                    Core Scores              CUHK-Specific         Simulation
                ┌───────────────────┐   ┌──────────────────┐   ┌──────────────┐
                │  Content    8/10  │   │  Values      7/10│   │  Time    9/10│
                │  Relevance  7/10  │   │  Alignment       │   │  Management  │
                │  Clarity    9/10  │   │                  │   │              │
                │                   │   │  Self-       6/10│   │              │
                │                   │   │  Awareness       │   │              │
                └───────────────────┘   └──────────────────┘   └──────────────┘
                   Always scored           When CUHK +            Simulation
                                           program selected       mode only
```

---

### 5. Answer Improvement Coach

After each answer, students can click **"Show Me a Better Answer"** to see their answer professionally rewritten:

```
┌─────────────────────────────┐  ┌─────────────────────────────┐
│      YOUR ANSWER            │  │    IMPROVED VERSION          │
│                             │  │                              │
│ "I did a project about      │  │ "I built an event management │
│  events. It was hard but    │  │  system that handles 500+    │
│  I learned a lot."          │  │  concurrent users. The       │
│                             │  │  biggest challenge was       │
│                             │  │  designing the real-time     │
│                             │  │  notification system — I     │
│                             │  │  chose WebSockets over       │
│                             │  │  polling after benchmarking  │
│                             │  │  both approaches..."         │
└─────────────────────────────┘  └─────────────────────────────┘

Key Improvements:
  1. Added specific numbers (500+ users)
  2. Named the technical challenge
  3. Showed decision-making process
  4. Connected to concrete outcome

STAR Breakdown:
  Situation: Building event management for university
  Task:      Handle real-time updates at scale
  Action:    Benchmarked WebSockets vs polling, chose WS
  Result:    System handles 500+ concurrent users
```

The coach keeps the student's authentic stories but restructures for impact and adds specificity from their profile data.

---

### 6. Two Interview Modes

| Feature | Practice Mode | Simulation Mode |
|---------|:------------:|:--------------:|
| Timer | None | 2-minute countdown |
| Feedback | After each answer | After each answer |
| Question reading | Manual button | Auto-read via TTS |
| Time pressure scoring | No | Yes |
| Visual timer | No | Green -> Yellow -> Red |
| Auto-submit on timeout | No | Yes |

---

### 7. Pre-Interview Strategy Briefing

Before starting an interview, students can generate a personalized coaching report:

```
Strategy Briefing for: CUHK Medicine

Likely Questions:
  1. "Why medicine and not another helping profession?"
     Why they ask: Tests genuine motivation vs. parental pressure
     Your angle: Reference your hospital volunteering from your CV

  2. "Describe an ethical dilemma you've encountered"
     Why they ask: MMI stations test ethical reasoning
     Your angle: Use your community service experience as a framework

Key Talking Points:
  - Your event management project → demonstrates problem-solving under pressure
  - Hospital volunteering → shows genuine compassion through ACTION
  - DSE results → evidence of academic rigor

Do:                              Don't:
  + Use specific examples          - Memorize scripted answers
  + Show your reasoning process    - Claim to have all the answers
  + Reference CUHK's values        - Focus only on prestige
  + Acknowledge complexity          - Be dismissive of other perspectives

Opening Strategy: Start with a warm greeting. Mention something specific
about CUHK Medicine that excites you (e.g., the Problem-Based Learning
curriculum or the rural health outreach program).
```

---

### 8. Cross-Session Analytics

After completing multiple sessions, students access a performance dashboard:

```
Sessions: 5          Avg Content: 7.2     Avg Relevance: 6.8     Avg Clarity: 7.5

Improvement Velocity:
  Content:    +18.3%    ████████████████████   (strong improvement)
  Relevance:  +12.1%    █████████████          (improving)
  Clarity:    +24.7%    ████████████████████████████ (excellent growth)

Score Trends:                          Skill Breakdown:
  10│         ╱─────                        Content
   8│    ╱───╱                             ╱      ╲
   6│───╱                          Clarity ╱────────╲ Relevance
   4│                                      ╲        ╱
   2│                                       ╲──────╱
    └──────────────
     S1  S2  S3  S4  S5

Strengths:                             Areas for Growth:
  + Clear communication style            - Lacks specific examples when
  + Strong project narratives              discussing extracurriculars
  + Good self-awareness                  - Tends to give short answers
                                           under time pressure
```

---

### 9. Answer Replay & Delta Scoring

Students can revisit any past question, re-record their answer, and see exactly how they improved:

```
Original Score:  Content 5  →  New Score: Content 8  (+3.0)
                 Relevance 4              Relevance 7  (+3.0)
                 Clarity 6                Clarity 8    (+2.0)
```

This creates a deliberate practice loop: perform -> get feedback -> understand what better looks like -> retry -> measure improvement.

---

### 10. Context-Aware Speech Recognition

Standard speech-to-text makes errors like "producer" instead of "produced" or mangles proper nouns. Our system adds an AI correction layer:

```
Audio Input
    │
    ▼
Whisper STT ──> Raw: "I producer a building event management system using reacts"
    │
    ▼
AI Correction ──> Context: Student's profile has project "Building Event
    │              Management System" using ["React", "Node.js"]
    │
    ▼
Corrected: "I produced a building event management system using React"
```

The AI uses the student's profile (name, projects, skills, technologies) as context to fix mishearings.

---

## Project Structure

```
interview_tester/
├── backend/
│   ├── app/
│   │   ├── main.py                          # FastAPI app + CORS + health check
│   │   ├── config.py                        # Environment-based settings
│   │   ├── database.py                      # SQLite schema (7 tables) + migrations
│   │   ├── models/
│   │   │   ├── user.py                      # User + Profile models
│   │   │   ├── interview.py                 # Interview request/response models
│   │   │   └── session.py                   # Session + Exchange models
│   │   ├── routers/
│   │   │   ├── users.py                     # User CRUD
│   │   │   ├── profile.py                   # Profile extraction + transcription
│   │   │   ├── interview.py                 # Interview flow + coaching + replay
│   │   │   ├── sessions.py                  # Session history queries
│   │   │   ├── briefing.py                  # Strategy briefing generation
│   │   │   └── analytics.py                 # Performance analytics
│   │   └── services/
│   │       ├── ollama.py                    # LLM interface (Ollama chat API)
│   │       ├── whisper_stt.py               # Speech-to-text + AI correction
│   │       ├── conversation_engine.py       # Adaptive question generation
│   │       ├── response_analyzer.py         # Multi-dimensional scoring
│   │       ├── answer_coach.py              # Answer improvement with STAR
│   │       ├── profile_extractor.py         # AI profile parsing + merging
│   │       ├── strategy_briefing.py         # Pre-interview coaching reports
│   │       ├── analytics.py                 # Progress tracking + pattern detection
│   │       ├── cuhk_knowledge.py            # CUHK intelligence (9 programs)
│   │       └── document_parser.py           # PDF/DOCX/TXT parsing
│   ├── requirements.txt
│   └── run.py
│
└── frontend/
    ├── src/
    │   ├── App.jsx                          # Router (8 routes)
    │   ├── api/client.js                    # Backend API wrapper
    │   ├── hooks/
    │   │   ├── useAudioRecorder.js          # MediaRecorder API wrapper
    │   │   └── useSpeechSynthesis.js        # Browser TTS wrapper
    │   ├── pages/
    │   │   ├── HomePage.jsx                 # User selection + health status
    │   │   ├── ProfilePage.jsx              # Voice + document profile building
    │   │   ├── InterviewPage.jsx            # Full interview flow (practice + sim)
    │   │   ├── BriefingPage.jsx             # Pre-interview strategy report
    │   │   ├── HistoryPage.jsx              # Session history list
    │   │   ├── ResultsPage.jsx              # Session results + breakdown
    │   │   ├── AnalyticsPage.jsx            # Charts + trends + patterns
    │   │   └── ReplayPage.jsx               # Re-answer with delta scoring
    │   └── components/
    │       ├── VoiceRecorder.jsx             # Audio recording + Whisper + text fallback
    │       ├── QuestionCard.jsx              # Question display + type badges + TTS
    │       ├── FeedbackPanel.jsx             # Score visualization (up to 6 dimensions)
    │       ├── ScoreBoard.jsx                # Session completion summary
    │       ├── AnswerComparisonPanel.jsx      # Side-by-side answer improvement
    │       ├── InterviewTimer.jsx            # Countdown timer (simulation mode)
    │       ├── InterviewFormatBriefing.jsx    # Interview format info card
    │       ├── UniversitySelector.jsx         # HK university dropdown
    │       ├── CUHKProgramSelector.jsx        # CUHK program/faculty dropdown
    │       ├── DocumentUpload.jsx             # File upload for CV/essays
    │       ├── ProfileCard.jsx               # Structured profile display
    │       ├── InterviewReport.jsx           # Print-optimized PDF report layout
    │       └── ThemeToggle.jsx               # Dark/light mode toggle
    ├── index.html
    ├── vite.config.js
    └── package.json
```

---

## API Endpoints

| Method | Endpoint | Purpose |
|--------|---------|---------|
| `GET` | `/api/health` | System health + Ollama status |
| `POST` | `/api/users` | Create user |
| `GET` | `/api/users` | List users |
| `GET` | `/api/users/{id}` | Get user details |
| `POST` | `/api/transcribe` | Audio -> text (Whisper + AI correction) |
| `POST` | `/api/profile/extract` | Voice transcript -> structured profile |
| `POST` | `/api/profile/upload` | Document upload -> profile extraction |
| `GET` | `/api/profile/{id}` | Get user's profile |
| `PUT` | `/api/profile/{id}` | Update profile fields |
| `POST` | `/api/interview/start` | Start interview session |
| `POST` | `/api/interview/{id}/answer` | Submit answer, get scores + next question |
| `POST` | `/api/interview/{id}/exchange/{eid}/improve` | Generate improved answer |
| `POST` | `/api/interview/{id}/replay/{eid}` | Re-answer with delta scoring |
| `POST` | `/api/interview/{id}/end` | End session early |
| `GET` | `/api/sessions/{uid}` | List user's sessions |
| `GET` | `/api/sessions/{uid}/{sid}` | Full session with all exchanges |
| `POST` | `/api/briefing/{uid}` | Generate strategy briefing |
| `GET` | `/api/briefing/format` | Get interview format info |
| `GET` | `/api/briefing/programs` | List CUHK programs |
| `GET` | `/api/analytics/{uid}` | Full performance analytics |

---

## Database Schema

```
users ──────────< profiles (1:1)
  │
  └──────────────< sessions ──────< exchanges ──────< exchange_retries
                      │
                      └── analytics_cache
                      └── briefings
```

**7 tables** tracking users, profiles (10+ extracted fields), interview sessions with mode/program, individual Q&A exchanges with 6 scoring dimensions, answer retries for replay mode, cached analytics, and strategy briefings.

---

## Setup & Running

### Prerequisites
- Python 3.11+
- Node.js 18+
- Ollama with Mistral model

### Installation

```bash
# 1. Pull the LLM model
ollama pull mistral:7b-instruct-q4_0

# 2. Backend
cd backend
pip install -r requirements.txt
python run.py                      # Starts on http://localhost:8000

# 3. Frontend (new terminal)
cd frontend
npm install
npm run dev                        # Starts on http://localhost:5173
```

The Whisper speech model (~150MB) downloads automatically on first voice recording.

### Configuration

All settings configurable via environment variables (prefix `INTERVIEW_`):

| Variable | Default | Description |
|----------|---------|-------------|
| `INTERVIEW_LLM_PROVIDER` | `ollama` | LLM provider: `ollama` (local) or `openrouter` (cloud) |
| `INTERVIEW_OLLAMA_MODEL` | `mistral:7b-instruct-q4_0` | Ollama model name |
| `INTERVIEW_OPENROUTER_API_KEY` | *(empty)* | OpenRouter API key ([get one free](https://openrouter.ai/keys)) |
| `INTERVIEW_OPENROUTER_MODEL` | `nvidia/nemotron-nano-9b-v2:free` | OpenRouter model (free tier) |
| `INTERVIEW_WHISPER_MODEL` | `base` | Whisper model (tiny/base/small/medium) |
| `INTERVIEW_WHISPER_LANGUAGE` | `en` | Speech recognition language |
| `INTERVIEW_MAX_QUESTIONS_PER_SESSION` | `5` | Base questions per interview |
| `INTERVIEW_CORS_ORIGINS` | `["http://localhost:5173"]` | Allowed frontend origins |

---

## Cloud Deployment

The app deploys as two services: **frontend on Vercel** (free) + **backend on Render** (free).

### Step 1: Push to GitHub

```bash
git add -A && git commit -m "Prepare for deployment"
git remote add origin https://github.com/YOUR_USERNAME/interview-tester.git
git push -u origin main
```

### Step 2: Deploy Backend on Render

1. Go to [render.com](https://render.com) and sign up (free)
2. Click **New > Web Service** and connect your GitHub repo
3. Configure:
   - **Root directory:** `backend`
   - **Build command:** `pip install -r requirements.txt`
   - **Start command:** `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
4. Add environment variables:
   | Key | Value |
   |-----|-------|
   | `INTERVIEW_LLM_PROVIDER` | `openrouter` |
   | `INTERVIEW_OPENROUTER_API_KEY` | `sk-or-...` (your key from [openrouter.ai/keys](https://openrouter.ai/keys)) |
   | `INTERVIEW_OPENROUTER_MODEL` | `nvidia/nemotron-nano-9b-v2:free` |
   | `INTERVIEW_CORS_ORIGINS` | `["https://YOUR-APP.vercel.app"]` |
   | `INTERVIEW_WHISPER_MODEL` | `tiny` |
5. Click **Create Web Service** — note the URL (e.g., `https://interview-tester-api.onrender.com`)

### Step 3: Deploy Frontend on Vercel

1. Go to [vercel.com](https://vercel.com) and import your GitHub repo
2. Configure:
   - **Root directory:** `frontend`
   - **Framework preset:** Vite
3. Add environment variable:
   | Key | Value |
   |-----|-------|
   | `VITE_API_URL` | `https://interview-tester-api.onrender.com` |
4. Click **Deploy**

### Free Tier Notes

- **Render free tier** spins down after 15 min of inactivity. First request takes ~30s to wake up. This is normal for a demo.
- **OpenRouter free models** have rate limits (~10 req/min). Fine for normal use, may throttle rapid clicking.
- **SQLite on Render free tier** is ephemeral — data resets on each deploy. For persistent data, upgrade to Render paid ($7/mo) or switch to Supabase PostgreSQL.

---

## Technical Highlights

**Provider-Agnostic LLM Layer:** A single `generate(prompt, system)` function serves all 10 call sites across 9 services. Switching between Ollama (local) and OpenRouter (cloud) requires changing one environment variable — zero code changes.

**Prompt Engineering:** Every AI interaction uses carefully crafted prompts with structured output parsing, retry logic for malformed JSON, and context injection from CUHK knowledge base + student profile.

**Async Architecture:** All LLM calls, database operations, and Whisper transcription are fully async using `asyncio`, `aiosqlite`, and `httpx.AsyncClient`. Whisper runs in a thread pool executor to avoid blocking the event loop.

**Adaptive Algorithms:** The conversation engine uses a strategy classifier that considers answer scores, question position, interview progress, and remaining questions to determine the optimal next question type — implementing a state machine over the interview conversation.

**Profile Merging:** Multiple document uploads don't overwrite — the AI intelligently merges new information with existing data, combining skill lists, adding new projects, and keeping the more detailed version of each field.

**Local-First with Cloud Option:** Runs fully local with Ollama for privacy, or deploys to the cloud with OpenRouter. The same codebase supports both modes via environment configuration.

---

## Tech Stack

| Component | Technology | Version |
|-----------|-----------|---------|
| Frontend Framework | React | 19.x |
| Build Tool | Vite | 6.x |
| Routing | React Router | 7.x |
| Charts | Recharts | 2.x |
| Backend Framework | FastAPI | 0.115 |
| ASGI Server | Uvicorn | 0.30 |
| Database | SQLite via aiosqlite | 0.20 |
| HTTP Client | httpx | 0.27 |
| LLM Runtime | Ollama | latest |
| LLM Model | Mistral 7B Instruct | Q4_0 |
| Speech-to-Text | faster-whisper | latest |
| PDF Parsing | pdfplumber | 0.11 |
| DOCX Parsing | python-docx | 1.2 |
| Settings | pydantic-settings | 2.5 |

---

*Built as a full-stack AI project demonstrating prompt engineering, adaptive algorithms, multi-modal input processing, and domain-specific knowledge systems.*
