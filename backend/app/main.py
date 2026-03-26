from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import settings
from .database import init_db
from .routers import users, profile, interview, sessions, analytics, briefing


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield


app = FastAPI(title="Interview Tester", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(users.router, prefix="/api")
app.include_router(profile.router, prefix="/api")
app.include_router(interview.router, prefix="/api")
app.include_router(sessions.router, prefix="/api")
app.include_router(analytics.router, prefix="/api")
app.include_router(briefing.router, prefix="/api")


@app.get("/api/health")
async def health_endpoint():
    from .services.ollama import health_check
    llm = await health_check()
    return {
        "status": "ok",
        "llm_status": llm["status"],
        "llm_provider": llm["provider"],
        "model": llm["model"],
    }
