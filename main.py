from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import logging
import os

from api.routes import router
from core.config import settings
from core.vector_store import VectorStoreManager
from core.ingestion import ingest_all_documents

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting Enterprise RAG Pipeline...")
    try:
        logger.info("Initializing vector store...")
        VectorStoreManager.initialize()
        logger.info("Ingesting domain documents...")
        ingest_all_documents()
        logger.info("Pipeline ready.")
    except Exception as e:
        logger.error(f"Startup error: {e}")
    yield
    logger.info("Shutting down...")


app = FastAPI(
    title="Enterprise RAG Pipeline",
    description="End-to-end RAG API for HR and Finance domains with LangSmith tracing and Guardrails",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/api/v1")


@app.get("/")
def root():
    return {
        "message": "Enterprise RAG Pipeline is running",
        "docs": "/docs",
        "health": "/health",
    }


@app.get("/health")
def health():
    return {"status": "healthy", "version": "1.0.0"}