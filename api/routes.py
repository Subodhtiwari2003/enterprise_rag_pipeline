from fastapi import APIRouter, HTTPException
from api.schemas import (
    QueryRequest, QueryResponse,
    RetrieveRequest, RetrieveResponse, RetrievedChunk,
    MCPToolCall, MCPToolResponse,
    GuardrailCheckRequest, GuardrailCheckResponse,
)
from core.rag_pipeline import run_rag_pipeline
from core.vector_store import VectorStoreManager
from core.mcp_tools import MCP_TOOLS, execute_mcp_tool
from core.guardrails import run_input_guardrails
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


# ─────────────────────────────────────────────
# RAG Query Endpoint
# ─────────────────────────────────────────────

@router.post("/query", response_model=QueryResponse, tags=["RAG"])
def query_rag(request: QueryRequest):
    """
    Ask a question against the HR or Finance knowledge base.
    Includes guardrail checks, vector retrieval, and Gemini-powered generation.
    """
    try:
        result = run_rag_pipeline(
            query=request.query,
            domain=request.domain.lower(),
        )
        return QueryResponse(**result)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"RAG pipeline error: {e}")
        raise HTTPException(status_code=500, detail="Internal pipeline error")


# ─────────────────────────────────────────────
# Raw Document Retrieval Endpoint
# ─────────────────────────────────────────────

@router.post("/retrieve", response_model=RetrieveResponse, tags=["RAG"])
def retrieve_documents(request: RetrieveRequest):
    """
    Retrieve raw document chunks from the vector store without LLM generation.
    Useful for debugging retrieval quality.
    """
    try:
        results = VectorStoreManager.query(
            domain=request.domain.lower(),
            query_text=request.query,
            top_k=request.top_k,
        )
        return RetrieveResponse(
            results=[RetrievedChunk(**r) for r in results],
            count=len(results),
            domain=request.domain,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Retrieval error: {e}")
        raise HTTPException(status_code=500, detail="Retrieval failed")


# ─────────────────────────────────────────────
# MCP Tool Endpoints
# ─────────────────────────────────────────────

@router.get("/mcp/tools", tags=["MCP"])
def list_mcp_tools():
    """List all available MCP tool definitions."""
    return {"tools": MCP_TOOLS, "count": len(MCP_TOOLS)}


@router.post("/mcp/call", response_model=MCPToolResponse, tags=["MCP"])
def call_mcp_tool(request: MCPToolCall):
    """
    Execute an MCP tool by name with provided parameters.
    Enables agent-based orchestration of the RAG pipeline.
    """
    try:
        result = execute_mcp_tool(request.tool_name, request.parameters)
        return MCPToolResponse(
            tool_name=request.tool_name,
            result=result,
            success=True,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"MCP tool error [{request.tool_name}]: {e}")
        return MCPToolResponse(
            tool_name=request.tool_name,
            result=None,
            success=False,
            error=str(e),
        )


# ─────────────────────────────────────────────
# Guardrail Check Endpoint
# ─────────────────────────────────────────────

@router.post("/guardrail/check", response_model=GuardrailCheckResponse, tags=["Safety"])
def check_guardrails(request: GuardrailCheckRequest):
    """
    Run safety guardrail checks on a query before it enters the pipeline.
    Checks for PII, prompt injection, blocked topics, and domain validity.
    """
    result = run_input_guardrails(request.query, request.domain)
    return GuardrailCheckResponse(passed=result.passed, reason=result.reason)


# ─────────────────────────────────────────────
# Domain Info
# ─────────────────────────────────────────────

@router.get("/domains", tags=["Info"])
def list_domains():
    """List supported knowledge domains."""
    return {
        "domains": [
            {"name": "hr", "description": "Human Resources: leave, performance, onboarding, conduct"},
            {"name": "finance", "description": "Finance: expenses, budget, accounts payable, audit"},
        ]
    }