import os
from dataclasses import dataclass

@dataclass
class Config:
    # LLM Config
    MODEL_NAME: str = os.getenv("MODEL_NAME", "gemini-pro")
    TEMPERATURE: float = 0.3

    # Vector DB
    VECTOR_DB_PATH: str = os.getenv("VECTOR_DB_PATH", "./vectorstore")

    # Retrieval
    TOP_K: int = 3

    # Embeddings
    EMBEDDING_MODEL: str = "sentence-transformers/all-MiniLM-L6-v2"

config = Config()