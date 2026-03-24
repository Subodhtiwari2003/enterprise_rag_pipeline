# vector_store.py
from sentence_transformers import SentenceTransformer
from langchain_community.vectorstores import FAISS
from langchain.embeddings import HuggingFaceEmbeddings

def get_vector_store(chunks):
    embed_model = HuggingFaceEmbeddings(
        model_name="all-MiniLM-L6-v2"
    )
    vector_store = FAISS.from_documents(chunks, embed_model)
    return vector_store