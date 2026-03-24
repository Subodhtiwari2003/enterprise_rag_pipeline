# rag_chain.py
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.chains import RetrievalQA
from ingestion import load_and_chunk
from vector_store import get_vector_store
import os
from langsmith.tracing import traceable

@traceable(name="RAG HR/Finance QA")
def build_qa_chain():
    chunks = load_and_chunk("data/hr_docs/hr_policy.pdf")
    vector_store = get_vector_store(chunks)

    retriever = vector_store.as_retriever(search_kwargs={"k": 3})
    llm = ChatGoogleGenerativeAI(
        model="gemini-pro",
        google_api_key=os.getenv("GOOGLE_API_KEY"),
        temperature=0.2
    )

    chain = RetrievalQA.from_chain_type(
        llm=llm,
        retriever=retriever,
        return_source_documents=True,
        chain_type="stuff",
        verbose=True
    )
    return chain