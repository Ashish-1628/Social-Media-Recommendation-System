import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Import all models so SQLAlchemy's Base.metadata knows every table
import app.models  # noqa: F401

from app.api.router import api_router
from app.core.config import get_settings
from app.database import Base, engine
from app.middleware.logging import LoggingMiddleware

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)

settings = get_settings()

app = FastAPI(
    title="GraphConnect API",
    description="""
Backend API for the **GraphConnect** Social Network Recommendation System.

## Features
- 🔐 **JWT Authentication** — register, login, protected endpoints
- 👥 **Social Graph** — follow / unfollow users
- 📝 **Posts** — create, edit, delete, like, comment
- 🤖 **Recommendations**
  - *Friend-of-Friend* (BFS graph traversal)
  - *Collaborative Filtering* (Jaccard similarity)
  - *Content-Based* (tag matching)
  - *Trending* (time-decayed engagement)
  - *Hybrid* (weighted merge of the above)
""",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# ── Startup: auto-create all tables (SQLite zero-config) ──────────────────────
@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)
    logging.getLogger("graphconnect").info("Database tables ensured.")


# ── Middleware ────────────────────────────────────────────────────────────────
origins = [
    "http://localhost:5173",  # Vite dev server
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(LoggingMiddleware)

# ── Routes ────────────────────────────────────────────────────────────────────
app.include_router(api_router)


@app.get("/health", tags=["Health"])
def health_check():
    return {"status": "ok", "message": "GraphConnect API is running.", "version": "1.0.0"}
