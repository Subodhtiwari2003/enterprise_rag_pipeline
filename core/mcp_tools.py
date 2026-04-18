"""
MCP (Model Context Protocol) Tool Layer.

Exposes structured tool definitions that can be called by LLM agents
or external orchestrators. Each tool wraps a core RAG or utility function.
"""

from typing import Any
from core.vector_store import VectorStoreManager
from core.rag_pipeline import run_rag_pipeline
from core.guardrails import run_input_guardrails

# ── Tool Registry ─────────────────────────────────────────────────────────────

MCP_TOOLS = [
    {
        "name": "query_hr_policy",
        "description": "Query the HR knowledge base for policies on leave, performance, onboarding, code of conduct, etc.",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "The HR-related question to answer"}
            },
            "required": ["query"],
        },
    },
    {
        "name": "query_finance_policy",
        "description": "Query the Finance knowledge base for policies on expenses, budgets, accounts payable, audit, etc.",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "The Finance-related question to answer"}
            },
            "required": ["query"],
        },
    },
    {
        "name": "retrieve_documents",
        "description": "Retrieve raw relevant document chunks from a domain without generating an LLM answer.",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Search query"},
                "domain": {"type": "string", "enum": ["hr", "finance"], "description": "Knowledge domain"},
                "top_k": {"type": "integer", "description": "Number of results (1–10)", "default": 4},
            },
            "required": ["query", "domain"],
        },
    },
    {
        "name": "check_query_safety",
        "description": "Run guardrail checks on a query before processing. Returns pass/fail with reason.",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Query to check"},
                "domain": {"type": "string", "enum": ["hr", "finance"]},
            },
            "required": ["query", "domain"],
        },
    },
]


def execute_mcp_tool(tool_name: str, parameters: dict) -> Any:
    """Execute a registered MCP tool by name with given parameters."""
    if tool_name == "query_hr_policy":
        return run_rag_pipeline(query=parameters["query"], domain="hr")

    elif tool_name == "query_finance_policy":
        return run_rag_pipeline(query=parameters["query"], domain="finance")

    elif tool_name == "retrieve_documents":
        top_k = min(max(parameters.get("top_k", 4), 1), 10)
        results = VectorStoreManager.query(
            domain=parameters["domain"],
            query_text=parameters["query"],
            top_k=top_k,
        )
        return {"results": results, "count": len(results)}

    elif tool_name == "check_query_safety":
        result = run_input_guardrails(parameters["query"], parameters["domain"])
        return {"passed": result.passed, "reason": result.reason}

    else:
        raise ValueError(f"Unknown tool: '{tool_name}'. Available: {[t['name'] for t in MCP_TOOLS]}")