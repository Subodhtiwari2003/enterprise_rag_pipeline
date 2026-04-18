import logging
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langsmith import traceable
from core.config import settings
from core.vector_store import VectorStoreManager
from core.guardrails import run_input_guardrails, run_output_guardrails

logger = logging.getLogger(__name__)

# ── Prompt Templates ──────────────────────────────────

HR_PROMPT = PromptTemplate(
    input_variables=["context", "question"],
    template="""You are an expert HR assistant for an enterprise organization.
Use ONLY the context below to answer the employee's question accurately and professionally.
If the answer is not in the context, say: "I don't have information on that in our HR policies."

Context:
{context}

Question: {question}

Answer (be concise, professional, and cite the policy section where relevant):""",
)

FINANCE_PROMPT = PromptTemplate(
    input_variables=["context", "question"],
    template="""You are an expert Finance assistant for an enterprise organization.
Use ONLY the context below to answer the question accurately. 
If the answer is not in the context, say: "I don't have information on that in our Finance policies."

Context:
{context}

Question: {question}

Answer (be concise, accurate, and reference the relevant policy or process):""",
)

DOMAIN_PROMPTS = {"hr": HR_PROMPT, "finance": FINANCE_PROMPT}


def get_llm() -> ChatGoogleGenerativeAI:
    return ChatGoogleGenerativeAI(
        model=settings.GEMINI_MODEL,
        google_api_key=settings.GOOGLE_API_KEY,
        temperature=0.2,
        convert_system_message_to_human=True,
    )


def format_context(retrieved_docs: list[dict]) -> str:
    parts = []
    for i, doc in enumerate(retrieved_docs, 1):
        title = doc["metadata"].get("title", "Document")
        parts.append(f"[{i}] {title}:\n{doc['content']}")
    return "\n\n".join(parts)


@traceable(name="enterprise_rag_query", run_type="chain")
def run_rag_pipeline(query: str, domain: str) -> dict:
    """
    Full RAG pipeline:
    1. Input guardrails
    2. Retrieve relevant chunks from ChromaDB
    3. Generate answer with Gemini
    4. Output guardrails
    """
    # Step 1: Input guardrails
    guard_result = run_input_guardrails(query, domain)
    if not guard_result.passed:
        return {
            "answer": f"Query blocked: {guard_result.reason}",
            "sources": [],
            "domain": domain,
            "blocked": True,
            "block_reason": guard_result.reason,
        }

    # Step 2: Retrieve
    retrieved = VectorStoreManager.query(domain, query, top_k=settings.TOP_K)
    if not retrieved:
        return {
            "answer": "No relevant documents found for your query.",
            "sources": [],
            "domain": domain,
            "blocked": False,
        }

    context = format_context(retrieved)
    prompt_template = DOMAIN_PROMPTS.get(domain, HR_PROMPT)

    # Step 3: Generate
    llm = get_llm()
    chain = prompt_template | llm | StrOutputParser()
    answer = chain.invoke({"context": context, "question": query})

    # Step 4: Output guardrails
    out_guard = run_output_guardrails(answer)
    if not out_guard.passed:
        return {
            "answer": "Response blocked due to safety policy.",
            "sources": [],
            "domain": domain,
            "blocked": True,
            "block_reason": out_guard.reason,
        }

    sources = [
        {
            "title": doc["metadata"].get("title"),
            "domain": doc["metadata"].get("domain"),
            "score": doc["score"],
        }
        for doc in retrieved
    ]

    return {
        "answer": answer.strip(),
        "sources": sources,
        "domain": domain,
        "blocked": False,
    }