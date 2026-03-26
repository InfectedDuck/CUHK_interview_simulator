import aiosqlite
from .config import settings

DATABASE_PATH = settings.database_path

SCHEMA = """
CREATE TABLE IF NOT EXISTS users (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    name        TEXT NOT NULL,
    created_at  TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS profiles (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id             INTEGER NOT NULL UNIQUE,
    raw_transcript      TEXT NOT NULL,
    education           TEXT,
    skills              TEXT,
    experience          TEXT,
    projects            TEXT,
    goals               TEXT,
    target_programs     TEXT,
    target_universities TEXT,
    achievements        TEXT,
    interests           TEXT,
    personality_traits   TEXT,
    updated_at          TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE TABLE IF NOT EXISTS sessions (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id             INTEGER NOT NULL,
    target_university   TEXT NOT NULL,
    target_program      TEXT,
    mode                TEXT NOT NULL DEFAULT 'practice',
    difficulty          TEXT NOT NULL DEFAULT 'medium',
    max_questions       INTEGER NOT NULL DEFAULT 5,
    status              TEXT NOT NULL DEFAULT 'in_progress',
    overall_score       REAL,
    summary_feedback    TEXT,
    started_at          TEXT NOT NULL DEFAULT (datetime('now')),
    completed_at        TEXT,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE TABLE IF NOT EXISTS exchanges (
    id                      INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id              INTEGER NOT NULL,
    question_number         INTEGER NOT NULL,
    question_text           TEXT NOT NULL,
    question_type           TEXT,
    answer_text             TEXT,
    content_score           REAL,
    relevance_score         REAL,
    clarity_score           REAL,
    values_alignment_score  REAL,
    self_awareness_score    REAL,
    time_management_score   REAL,
    feedback                TEXT,
    improved_answer         TEXT,
    star_breakdown          TEXT,
    key_changes             TEXT,
    response_time_seconds   REAL,
    started_at              TEXT,
    created_at              TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (session_id) REFERENCES sessions(id)
);

CREATE TABLE IF NOT EXISTS exchange_retries (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    exchange_id     INTEGER NOT NULL,
    attempt_number  INTEGER NOT NULL DEFAULT 1,
    answer_text     TEXT NOT NULL,
    content_score   REAL,
    relevance_score REAL,
    clarity_score   REAL,
    feedback        TEXT,
    created_at      TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (exchange_id) REFERENCES exchanges(id)
);

CREATE TABLE IF NOT EXISTS analytics_cache (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id         INTEGER NOT NULL,
    analysis_type   TEXT NOT NULL,
    data            TEXT NOT NULL,
    computed_at     TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE TABLE IF NOT EXISTS briefings (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id     INTEGER NOT NULL,
    university  TEXT NOT NULL,
    program     TEXT,
    content     TEXT NOT NULL,
    created_at  TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (user_id) REFERENCES users(id)
);
"""


async def get_db() -> aiosqlite.Connection:
    db = await aiosqlite.connect(DATABASE_PATH)
    db.row_factory = aiosqlite.Row
    return db


MIGRATIONS = [
    "ALTER TABLE profiles ADD COLUMN achievements TEXT",
    "ALTER TABLE profiles ADD COLUMN interests TEXT",
    "ALTER TABLE profiles ADD COLUMN personality_traits TEXT",
    "ALTER TABLE profiles ADD COLUMN projects TEXT",
    # Sessions additions
    "ALTER TABLE sessions ADD COLUMN target_program TEXT",
    "ALTER TABLE sessions ADD COLUMN mode TEXT DEFAULT 'practice'",
    "ALTER TABLE sessions ADD COLUMN max_questions INTEGER DEFAULT 5",
    # Exchanges additions
    "ALTER TABLE exchanges ADD COLUMN question_type TEXT",
    "ALTER TABLE exchanges ADD COLUMN improved_answer TEXT",
    "ALTER TABLE exchanges ADD COLUMN star_breakdown TEXT",
    "ALTER TABLE exchanges ADD COLUMN key_changes TEXT",
    "ALTER TABLE exchanges ADD COLUMN response_time_seconds REAL",
    "ALTER TABLE exchanges ADD COLUMN started_at TEXT",
    "ALTER TABLE exchanges ADD COLUMN values_alignment_score REAL",
    "ALTER TABLE exchanges ADD COLUMN self_awareness_score REAL",
    "ALTER TABLE exchanges ADD COLUMN time_management_score REAL",
    "ALTER TABLE sessions ADD COLUMN difficulty TEXT DEFAULT 'medium'",
]


async def init_db():
    db = await aiosqlite.connect(DATABASE_PATH)
    await db.executescript(SCHEMA)
    # Run migrations for existing databases
    for sql in MIGRATIONS:
        try:
            await db.execute(sql)
        except Exception:
            pass  # Column already exists
    await db.commit()
    await db.close()
