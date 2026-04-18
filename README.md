# 🏢 Enterprise RAG Pipeline

> A production-ready, end-to-end Retrieval-Augmented Generation (RAG) system for enterprise HR and Finance domains — built with FastAPI, LangChain, Google Gemini, ChromaDB, LangSmith, and deployed via Docker on Render.

![Python](https://img.shields.io/badge/Python-3.11-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115-green)
![LangChain](https://img.shields.io/badge/LangChain-0.3-orange)
![Docker](https://img.shields.io/badge/Docker-ready-blue)
![Render](https://img.shields.io/badge/Deployed-Render-purple)
![License](https://img.shields.io/badge/License-MIT-lightgrey)

---

## 📌 Overview

This project implements a fully functional, enterprise-grade RAG pipeline designed to answer domain-specific questions grounded in internal knowledge bases — with built-in safety guardrails, observability via LangSmith, and MCP (Model Context Protocol) tool-calling support.

**Supported Domains:**
- 🧑‍💼 **HR** — Leave policies, performance reviews, onboarding, code of conduct
- 💰 **Finance** — Expense reimbursement, budget planning, accounts payable, audit & compliance

---

## 🏗️ Architecture

```
User Query
    │
    ▼
┌─────────────────────────────┐
│     FastAPI REST API        │  ← /api/v1/query, /retrieve, /mcp/call
└────────────┬────────────────┘
             │
    ┌────────▼────────┐
    │  Input Guardrail │  ← PII check, injection detection, domain validation
    └────────┬─────────┘
             │
    ┌────────▼──────────────┐
    │  ChromaDB Retrieval   │  ← Google Embedding API → cosine similarity search
    │  (HR / Finance)       │
    └────────┬──────────────┘
             │
    ┌────────▼───────────────┐
    │  Gemini 1.5 Flash LLM  │  ← Domain-specific prompt templates
    └────────┬───────────────┘
             │
    ┌────────▼────────┐
    │ Output Guardrail │  ← PII leakage check on LLM response
    └────────┬─────────┘
             │
    ┌────────▼──────────┐
    │  LangSmith Trace   │  ← Full pipeline observability
    └────────┬───────────┘
             │
          Response
```

---

## ⚙️ Tech Stack

| Component | Technology | Why |
|---|---|---|
| **API Framework** | FastAPI | Async, fast, auto-docs |
| **LLM** | Google Gemini 1.5 Flash | Free tier, fast, capable |
| **Embeddings** | Google Embedding API | No local model = zero RAM overhead |
| **Vector DB** | ChromaDB | Free, lightweight, no external service needed |
| **Orchestration** | LangChain | Chain composition, prompt templates |
| **Observability** | LangSmith | Full trace monitoring for every LLM call |
| **Safety** | Custom Guardrails | PII detection, prompt injection, topic blocking |
| **Tool Calling** | MCP (Model Context Protocol) | Agent-compatible tool definitions |
| **Deployment** | Docker + Render | Free-tier deployable, <400MB image |

---

## 🗂️ Project Structure

```
enterprise_rag_pipeline/

├── main.py                  # FastAPI app entry point, lifespan startup
├── api/
│   ├── routes.py            # All API endpoints
│   └── schemas.py           # Pydantic request/response models
└── core/
│   ├── config.py            # Environment config & LangSmith setup
│   ├── vector_store.py      # ChromaDB manager (init, add, query)
│   ├── ingestion.py         # Domain document chunking & ingestion
│   ├── rag_pipeline.py      # Full RAG chain with LangSmith tracing
│   ├── guardrails.py        # Input/output safety checks
│   └── mcp_tools.py         # MCP tool registry & executor
├── Dockerfile               # Multi-stage, optimized for 512MB RAM
├── render.yaml              # Render deployment config
├── requirements.txt         # Lean dependencies (~380MB total)
├── .env.example             # Environment variable reference
├── .gitignore
└── README.md
```

---

## 🚀 Quick Start (Local)

### 1. Clone & Setup

```bash
git clone https://github.com/Subodhtiwari2003/enterprise_rag_pipeline.git
cd enterprise_rag_pipeline
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
cp .env.example .env
# Edit .env and add your GOOGLE_API_KEY (required)
# Optionally add LANGCHAIN_API_KEY for LangSmith tracing
```

### 3. Run

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

Open **http://localhost:8000/docs** for the interactive Swagger UI.

---

## 🐳 Docker (Local)

```bash
# Build
docker build -t enterprise-rag .

# Run
docker run -p 8000:8000 \
  -e GOOGLE_API_KEY=your_key_here \
  -e LANGCHAIN_API_KEY=your_langsmith_key \
  enterprise-rag
```

---

## ☁️ Deploy on Render

### Step-by-step:

1. **Push this repo to GitHub**

2. **Go to [render.com](https://render.com)** → New → Web Service

3. **Connect your GitHub repo**

4. **Settings:**
   - Runtime: `Docker`
   - Dockerfile Path: `./Dockerfile`
   - Plan: `Free`

5. **Add Environment Variables** (under Environment tab):
   | Key | Value |
   |-----|-------|
   | `GOOGLE_API_KEY` | your Google AI Studio key |
   | `LANGCHAIN_API_KEY` | your LangSmith key (optional) |
   | `LANGCHAIN_PROJECT` | `enterprise-rag-pipeline` |
   | `LANGCHAIN_TRACING_V2` | `true` |

6. **Click Deploy** — Render auto-detects `render.yaml`

> 💡 The free tier sleeps after 15 minutes of inactivity. First request after sleep takes ~30s.

---

## 📡 API Endpoints

### `POST /api/v1/query`
Ask a question against the HR or Finance knowledge base.

```json
// Request
{
  "query": "How many days of annual leave do I get?",
  "domain": "hr",
  "top_k": 4
}

// Response
{
  "answer": "As per the Leave Policy, all full-time employees are entitled to 24 days of paid annual leave per year...",
  "sources": [
    { "title": "Leave Policy", "domain": "hr", "score": 0.91 }
  ],
  "domain": "hr",
  "blocked": false
}
```

### `POST /api/v1/retrieve`
Get raw document chunks without LLM generation.

```json
{ "query": "invoice processing steps", "domain": "finance", "top_k": 3 }
```

### `GET /api/v1/mcp/tools`
List all available MCP tool definitions for agent integration.

### `POST /api/v1/mcp/call`
Execute an MCP tool directly.

```json
{
  "tool_name": "query_finance_policy",
  "parameters": { "query": "What are the payment terms for vendors?" }
}
```

### `POST /api/v1/guardrail/check`
Test the guardrail layer against any query.

```json
{ "query": "My Aadhaar is 1234 5678 9012", "domain": "hr" }
// → { "passed": false, "reason": "PII detected: aadhaar" }
```

---

## 🛡️ Guardrail System

The custom guardrail layer runs **zero-dependency** pattern matching — no heavy `guardrails-ai` package required.

| Check | What it catches |
|---|---|
| **PII Detection** | Aadhaar, PAN, credit card, email, phone, SSN |
| **Prompt Injection** | "ignore previous instructions", "act as", "jailbreak", etc. |
| **Blocked Topics** | Specific salary of named individuals, passwords, personal data requests |
| **Domain Validation** | Rejects queries for unknown domains |
| **Query Length** | Rejects empty or excessively long queries |
| **Output PII Check** | Scans LLM response before returning to user |

---

## 📊 LangSmith Observability

When `LANGCHAIN_API_KEY` is set, every RAG query is traced in LangSmith with:
- Full input/output for each chain step
- Retrieval results and scores
- LLM token usage and latency
- Guardrail pass/fail events

View traces at: **https://smith.langchain.com**

---

## 🔧 MCP Tool Integration

The pipeline exposes 4 MCP-compatible tools for agent orchestration:

| Tool | Description |
|---|---|
| `query_hr_policy` | Full RAG query against HR domain |
| `query_finance_policy` | Full RAG query against Finance domain |
| `retrieve_documents` | Raw vector search (no LLM) |
| `check_query_safety` | Run guardrail checks only |

These follow the MCP spec and can be plugged into any agent framework (LangChain agents, AutoGen, custom orchestrators).

---

## 📦 Why This Stack Fits Render Free Tier

| Library Removed | Replaced With | RAM Saved |
|---|---|---|
| `sentence-transformers` | Google Embedding API | ~800MB |
| `faiss-cpu` | ChromaDB | ~200MB |
| `pinecone-client` | ChromaDB (free, in-process) | N/A |
| `guardrails-ai` | Custom regex guardrails | ~150MB |
| **Total estimated footprint** | | **~350–380MB** ✅ |

---

## 🧑‍💻 Resume Description

> **Enterprise RAG Pipeline** | Python · FastAPI · LangChain · Google Gemini · ChromaDB · LangSmith · Docker · Render
>
> - Built end-to-end RAG API for HR and Finance domains with domain-isolated vector retrieval using ChromaDB and Google Embedding API (no local models, fits Render 512MB free tier)
> - Implemented layered safety guardrails for PII detection (Aadhaar, PAN, credit card), prompt injection blocking, and output sanitization — zero heavy dependencies
> - Integrated LangSmith tracing for full observability of every LLM call, retrieval step, and guardrail event
> - Exposed MCP (Model Context Protocol) tool definitions enabling agent-based orchestration
> - Containerized with multi-stage Docker build and deployed on Render with health checks and auto-restart

---

## 📄 License

MIT © Subodh Tiwari