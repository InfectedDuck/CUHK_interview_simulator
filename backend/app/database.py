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
    status              TEXT NOT NULL DEFAULT 'in_progress',
    overall_score       REAL,
    summary_feedback    TEXT,
    started_at          TEXT NOT NULL DEFAULT (datetime('now')),
    completed_at        TEXT,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE TABLE IF NOT EXISTS exchanges (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id      INTEGER NOT NULL,
    question_number INTEGER NOT NULL,
    question_text   TEXT NOT NULL,
    answer_text     TEXT,
    content_score   REAL,
    relevance_score REAL,
    clarity_score   REAL,
    feedback        TEXT,
    created_at      TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (session_id) REFERENCES sessions(id)
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
