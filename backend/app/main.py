import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import settings
from .database import create_tables
from .routers import chunk, history, presets, techniques, upload

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("chunking_playground")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan event handler to auto-create database tables on startup."""
    logger.info("Initializing Chunking Playground API...")
    try:
        await create_tables()
        logger.info("Database tables initialized successfully.")
    except Exception as e:
        logger.warning(f"Could not connect to database on startup: {e}. DB dependent endpoints may fail.")
    yield
    logger.info("Shutting down Chunking Playground API...")


app = FastAPI(
    title="Chunking Strategies Playground API",
    description="Interactive API for 21 text chunking techniques and document parsing for RAG systems.",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list + ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API routers
app.include_router(techniques.router)
app.include_router(chunk.router)
app.include_router(presets.router)
app.include_router(history.router)
app.include_router(upload.router)


@app.get("/api/health")
async def health_check():
    return {"status": "ok", "app": "Chunking Playground API", "version": "0.1.0"}
