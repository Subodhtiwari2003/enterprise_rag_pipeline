from langchain_community.vectorstores import FAISS
from langchain.embeddings import HuggingFaceEmbeddings
from app.config import config

class Retriever:
    def __init__(self):
        self.embedding = HuggingFaceEmbeddings(
            model_name=config.EMBEDDING_MODEL
        )

        self.db = FAISS.load_local(
            config.VECTOR_DB_PATH,
            self.embedding,
            allow_dangerous_deserialization=True
        )

    def get_docs(self, query: str):
        docs = self.db.similarity_search(query, k=config.TOP_K)
        return docs

    def format_docs(self, docs):
        return "\n\n".join([doc.page_content for doc in docs])