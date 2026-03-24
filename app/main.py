# main.py
from fastapi import FastAPI
from pydantic import BaseModel
from rag_chain import build_qa_chain

qa_chain = build_qa_chain()
app = FastAPI()

class Query(BaseModel):
    question: str

@app.post("/query")
async def query_chain(query: Query):
    result = qa_chain({"query": query.question})
    return {
        "answer": result["result"],
        "sources": [doc.metadata for doc in result["source_documents"]]
    }