from pydantic import BaseModel, Field
from typing import Optional, Any


class QueryRequest(BaseModel):
    query: str = Field(..., min_length=5, max_length=1000, description="Question to ask")
    domain: str = Field(..., description="Domain: 'hr' or 'finance'")
    top_k: Optional[int] = Field(4, ge=1, le=10, description="Number of docs to retrieve")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "query": "How many days of annual leave do I get?",
                    "domain": "hr",
                    "top_k": 4,
                }
            ]
        }
    }


class SourceDoc(BaseModel):
    title: str
    domain: str
    score: float


class QueryResponse(BaseModel):
    answer: str
    sources: list[SourceDoc]
    domain: str
    blocked: bool = False
    block_reason: Optional[str] = None


class RetrieveRequest(BaseModel):
    query: str = Field(..., min_length=3, max_length=500)
    domain: str
    top_k: Optional[int] = Field(4, ge=1, le=10)


class RetrievedChunk(BaseModel):
    content: str
    metadata: dict
    score: float


class RetrieveResponse(BaseModel):
    results: list[RetrievedChunk]
    count: int
    domain: str


class MCPToolCall(BaseModel):
    tool_name: str = Field(..., description="Name of the MCP tool to call")
    parameters: dict = Field(..., description="Tool input parameters")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "tool_name": "query_hr_policy",
                    "parameters": {"query": "What is the maternity leave policy?"},
                }
            ]
        }
    }


class MCPToolResponse(BaseModel):
    tool_name: str
    result: Any
    success: bool
    error: Optional[str] = None


class GuardrailCheckRequest(BaseModel):
    query: str
    domain: str


class GuardrailCheckResponse(BaseModel):
    passed: bool
    reason: str