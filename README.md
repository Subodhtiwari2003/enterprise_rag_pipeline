# Enterprise RAG Pipeline

An intelligent Retrieval-Augmented Generation (RAG) system designed for enterprise applications with advanced routing, guardrails, and observability features.

## Features

- **Smart Routing** - Intelligent query routing to HR, Finance, or RAG pipeline
- **Input/Output Guardrails** - Validation and safety checks for queries and responses
- **LangSmith Integration** - Full tracing and monitoring of pipeline execution
- **MCP Support** - Model Context Protocol integration for external data sources
- **FastAPI Backend** - Modern, async-ready HTTP API
- **Multi-Source RAG** - Support for FAISS, Pinecone, and other vector stores
- **Google Generative AI** - Integration with Google's latest LLM models
- **Docker Ready** - Production-ready containerization with multi-stage builds

## Architecture

```
User Query
    ↓
Input Guardrails (Validation)
    ↓
Router (HR/Finance/RAG)
    ↓
    ├→ HR Route → MCP Client → HR Data
    ├→ Finance Route → MCP Client → Finance Data
    └→ General Query → RAG Pipeline
            ↓
        Retriever (Vector Store)
            ↓
        Generator (LLM)
    ↓
Output Guardrails (Validation)
    ↓
User Response
```

## Project Structure

```
enterprise_rag_pipeline/
├── app/                          # Main application
│   ├── main.py                  # FastAPI application & entry point
│   ├── config.py                # Configuration management
│   └── __init__.py
├── rag/                         # RAG components
│   ├── pipeline.py              # RAG orchestration
│   ├── retriever.py             # Vector store retrieval
│   └── generator.py             # LLM response generation
├── agents/                      # Routing agents
│   └── router.py                # Query routing logic
├── guardrails/                  # Safety & validation
│   ├── input_guard.py           # Input validation
│   └── output_guard.py          # Output validation
├── observability/               # Monitoring & tracing
│   └── langsmith.py             # LangSmith integration
├── mcp/                         # External integrations
│   ├── client.py                # MCP client
│   └── server.py                # MCP server
├── data/                        # Sample data
│   ├── hr_data.txt
│   └── finance_data.txt
├── requirements.txt             # Python dependencies
├── Dockerfile                   # Container configuration
├── docker-compose.yml           # Multi-container setup
├── .dockerignore                # Docker build exclusions
└── README.md                    # This file
```

## Installation

### Local Setup

**Prerequisites:**
- Python 3.11+
- pip or conda
- Git

**Steps:**

1. Clone the repository
```bash
git clone <repository-url>
cd enterprise_rag_pipeline
```

2. Create a virtual environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies
```bash
pip install -r requirements.txt
```

4. Configure environment variables
```bash
cp .env.example .env  # Create from template if available
```

### Docker Setup

**Prerequisites:**
- Docker 20.10+
- Docker Compose 2.0+

**Quick Start:**

```bash
# Build and run with Docker Compose
docker-compose up -d

# View logs
docker-compose logs -f enterprise-rag

# Stop the service
docker-compose down
```

**Manual Docker Build:**

```bash
# Build the image
docker build -t enterprise-rag-pipeline:latest .

# Run the container
docker run -p 8000:8000 \
  -e LANGSMITH_API_KEY=your_key \
  -e GOOGLE_API_KEY=your_key \
  -v $(pwd)/data:/app/data \
  enterprise-rag-pipeline:latest
```

## Configuration

### Environment Variables

Create a `.env` file in the project root:

```env
# LangSmith Configuration
LANGSMITH_API_KEY=your_langsmith_api_key
LANGSMITH_ENDPOINT=https://api.smith.langchain.com

# Google Generative AI
GOOGLE_API_KEY=your_google_api_key

# Pinecone (optional)
PINECONE_API_KEY=your_pinecone_api_key
PINECONE_ENVIRONMENT=your_environment

# Application Settings
DEBUG=false
HOST=0.0.0.0
PORT=8000
```

### Configuration File

Edit `app/config.py` for advanced settings:
- Model selection
- Vector store provider
- Guardrail thresholds
- Tracing settings

## Usage

### Local Execution

```bash
# Activate environment
source venv/bin/activate  # or: venv\Scripts\activate

# Run the application
python app/main.py
```

Interactive prompt:
```
Enter query (or 'exit'): Who is the CEO of the company?
```

### API Usage (with FastAPI)

```bash
# Start the server
python -m uvicorn app.main:app --reload --port 8000

# Visit API documentation
# Swagger UI: http://localhost:8000/docs
# ReDoc: http://localhost:8000/redoc
```

**Example API request:**
```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"query": "What is the Q3 revenue?", "user_role": "ANALYST"}'
```

### Docker Execution

```bash
# Using docker-compose (recommended for development)
docker-compose up

# Access API at http://localhost:8000
# Logs: docker-compose logs -f
```

## Development

### Running Tests

```bash
# Install test dependencies
pip install pytest pytest-cov

# Run tests
pytest tests/ -v --cov=app
```

### Code Formatting

```bash
# Install formatting tools
pip install black isort flake8

# Format code
black app/
isort app/

# Check linting
flake8 app/
```

### Adding New Data Sources

1. Create a new module in `data/`
2. Implement retriever in `rag/retriever.py`
3. Update routing logic in `agents/router.py`
4. Add guardrails in `guardrails/`

### Extending the Pipeline

**Adding a new route:**
```python
# In agents/router.py
elif route == "NEW_ROUTE":
    result = self.mcp.call("get_new_data", {...})
```

**Adding output validation:**
```python
# In guardrails/output_guard.py
def validate_output(response: str) -> str:
    # Your validation logic
    return response
```

## Observability

### LangSmith Integration

Automatically traces all pipeline operations:
- Query input/output
- Retrieval steps
- Generation process
- Guardrail checks

View traces at: `https://smith.langchain.com`

## Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| langchain | ≥0.1.0 | Core RAG framework |
| langchain-community | ≥0.0.10 | Community integrations |
| langchain-core | ≥0.1.0 | Base components |
| fastapi | ≥0.104.0 | Web framework |
| uvicorn | ≥0.24.0 | ASGI server |
| faiss-cpu | ≥1.7.4 | Vector similarity search |
| pinecone-client | ≥3.0.0 | Vector database |
| sentence-transformers | ≥2.2.0 | Embeddings |
| google-generativeai | ≥0.3.0 | Google LLMs |
| langsmith | ≥0.0.70 | Observability |

Full dependencies in [requirements.txt](requirements.txt)

## Troubleshooting

### Missing langchain-community vectorstores

```bash
# Clean reinstall
pip uninstall langchain langchain-community langchain-core -y
pip cache purge
pip install -r requirements.txt
```

### Docker build fails

```bash
# Clear build cache
docker system prune -a

# Rebuild
docker build --no-cache -t enterprise-rag-pipeline:latest .
```

### Health check failures

Ensure the FastAPI application is running:
```bash
curl http://localhost:8000/docs
```

## Performance Optimization

- **Vector Store**: Use Pinecone for production (vs FAISS for local)
- **Caching**: Implement Redis for query result caching
- **Batching**: Process multiple queries in parallel
- **Model**: Consider lighter models for latency-critical applications

## Security Considerations

- ✅ Non-root container user
- ✅ Input validation & guardrails
- ✅ API authentication (add as needed)
- ✅ Encrypted environment variables
- ⚠️ TODO: Add rate limiting
- ⚠️ TODO: Add request signing

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see [LICENSE](LICENSE) file for details.

## Support

For issues, questions, or suggestions:
- Open an issue on GitHub
- Check existing documentation
- Review [LangChain docs](https://python.langchain.com)
- Check [FastAPI docs](https://fastapi.tiangolo.com)

## Roadmap

- [ ] Add authentication & authorization
- [ ] Rate limiting & throttling
- [ ] GraphQL API support
- [ ] WebSocket support for streaming
- [ ] Advanced caching strategies
- [ ] Multi-language support
- [ ] Kubernetes deployment manifests
- [ ] Helm charts

---

**Last Updated:** March 2026
**Python Version:** 3.11+
**Status:** 🚀 Production Ready