import logging
import chromadb
from chromadb.config import Settings as ChromaSettings
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from core.config import settings

logger = logging.getLogger(__name__)

# Supported domains
DOMAINS = ["hr", "finance"]


class VectorStoreManager:
    _client: chromadb.Client = None
    _embeddings: GoogleGenerativeAIEmbeddings = None
    _collections: dict = {}

    @classmethod
    def initialize(cls):
        """Initialize ChromaDB client and Google embeddings."""
        cls._embeddings = GoogleGenerativeAIEmbeddings(
            model=settings.EMBEDDING_MODEL,
            google_api_key=settings.GOOGLE_API_KEY,
        )
        cls._client = chromadb.Client(
            ChromaSettings(
                persist_directory=settings.CHROMA_PERSIST_DIR,
                anonymized_telemetry=False,
            )
        )
        for domain in DOMAINS:
            cls._collections[domain] = cls._client.get_or_create_collection(
                name=f"enterprise_rag_{domain}",
                metadata={"hnsw:space": "cosine"},
            )
        logger.info(f"VectorStore initialized. Collections: {list(cls._collections.keys())}")

    @classmethod
    def get_collection(cls, domain: str):
        if domain not in cls._collections:
            raise ValueError(f"Unknown domain '{domain}'. Valid: {DOMAINS}")
        return cls._collections[domain]

    @classmethod
    def get_embeddings(cls):
        return cls._embeddings

    @classmethod
    def add_documents(cls, domain: str, texts: list[str], metadatas: list[dict]):
        """Embed and add documents to a domain collection."""
        collection = cls.get_collection(domain)
        embeddings_list = cls._embeddings.embed_documents(texts)
        ids = [f"{domain}_{i}_{hash(t) % 100000}" for i, t in enumerate(texts)]
        collection.add(
            embeddings=embeddings_list,
            documents=texts,
            metadatas=metadatas,
            ids=ids,
        )
        logger.info(f"Added {len(texts)} chunks to '{domain}' collection.")

    @classmethod
    def query(cls, domain: str, query_text: str, top_k: int = None) -> list[dict]:
        """Query a domain collection and return top-k results."""
        k = top_k or settings.TOP_K
        collection = cls.get_collection(domain)
        query_embedding = cls._embeddings.embed_query(query_text)
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=k,
            include=["documents", "metadatas", "distances"],
        )
        output = []
        for doc, meta, dist in zip(
            results["documents"][0],
            results["metadatas"][0],
            results["distances"][0],
        ):
            output.append({"content": doc, "metadata": meta, "score": round(1 - dist, 4)})
        return output