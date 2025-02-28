# LLM Domain Framework API

A FastAPI-based professional domain LLM framework API that supports multiple LLM model integration and RAG (Retrieval-Augmented Generation) functionality.

## Features

### 1. LLM Provider Support
- OpenAI (GPT series models)
- Ollama (Local open-source models)

### 2. RAG Features
- FAISS-based vector retrieval
- Automatic document vectorization
- Context-enhanced response generation
- Support for multiple document formats (.txt, .md, .json)

### 3. Core Features
- Prompt engineering (template management)
- Context management (session level)
- Intent analysis (multi-domain support)
- Adapter system (extensible)

## System Architecture

```
┌─────────────────────────────────────────┐
│           User Interface Layer          │
│    (Web UI, CLI, API, Natural Lang)     │
└───────────────┬─────────────────────────┘
                │
┌───────────────▼─────────────────────────┐
│            LLM Core Layer               │
│ (Prompt Eng, Context Mgmt, Intent)      │
└───────────────┬─────────────────────────┘
                │
┌───────────────▼─────────────────────────┐
│         Adapter Management Layer        │
│  (Connector Registry, Protocol, Route)   │
└───────────────┬─────────────────────────┘
                │
┌───────────────▼─────────────────────────┐
│         Software Connector Layer        │
│   (Software Adapters, API, Simulator)    │
└───────────────┬─────────────────────────┘
                │
┌───────────────▼─────────────────────────┐
│         Professional Software Layer     │
│   (ANDES, MATLAB, AutoCAD, SPSS etc)    │
└─────────────────────────────────────────┘
```

The system follows a layered architecture design:
1. User Interface Layer: Provides multiple interfaces for user interaction
2. LLM Core Layer: Handles core LLM functionalities and processing
3. Adapter Management Layer: Manages software connections and routing
4. Software Connector Layer: Implements specific software adapters
5. Professional Software Layer: Integrates with various professional tools

## Quick Start

### Environment Requirements
- Python 3.9+
- Poetry (dependency management)
- Ollama (optional, for local models)

### Installation

1. Install dependencies:
```bash
cd api
poetry install
```

2. Configure environment variables (create .env file):
```bash
OPENAI_API_KEY=your OpenAI API key
OLLAMA_API_URL=http://localhost:11434
DEFAULT_LLM_PROVIDER=ollama
```

3. Download embedding models:
```bash
poetry run download-models
```

4. Prepare knowledge base documents:
```bash
mkdir -p data/documents
# Place documents in the data/documents directory
```

### Start Service

```bash
poetry run python run.py
```

Service will start at http://localhost:8000

## API Endpoints

### 1. Query Interface
```bash
POST /api/v1/query
Content-Type: application/json

{
    "query": "Explain the concept of machine learning",
    "domain": "computer_science",
    "provider": "ollama",
    "model": "llama2"
}
```

### 2. Chat Interface
```bash
POST /api/v1/chat
Content-Type: application/json

{
    "messages": [
        {"role": "user", "content": "What is deep learning?"}
    ],
    "provider": "openai",
    "model": "gpt-3.5-turbo"
}
```

### 3. Task Analysis Interface
```bash
POST /api/v1/analyze
Content-Type: application/json

{
    "domain": "data_analysis",
    "task": {
        "type": "statistical",
        "data": "example.csv"
    }
}
```

### 4. Model List Interface
```bash
GET /api/v1/models/ollama
```

## Project Structure

```
api/
├── cache/              # Cache for LLM models and embeddings
├── data/              # Data storage and resources
│   └── documents/     # Knowledge base document storage
├── scripts/           # Utility and maintenance scripts
│   └── download_models.py
├── src/               # Source code directory
│   ├── api/          # API endpoints and routing
│   ├── core/         # Core system functionality
│   │   ├── rag/      # Retrieval Augmented Generation
│   │   ├── prompt/   # Prompt templates and management
│   │   └── intent/   # Intent analysis and processing
│   ├── adapter/      # Software system adapters
│   └── connectors/   # External service connectors
├── .env              # Environment configuration
├── pyproject.toml    # Project dependencies and settings
└── run.py            # Application entry point
```

## Development Guide

### Adding New LLM Provider
1. Create a new provider class in `src/core/providers`
2. Implement the `BaseLLMProvider` interface
3. Register the new provider in `LLMManager`

### Adding New Document Type Support
1. Modify the document loading logic in `src/core/rag/utils.py`
2. Add a new document processor

### Custom Prompt Template
1. Add a new template in `src/core/prompt/prompt_manager.py`

## Common Issues

### Model Download Failure
If you encounter issues with model download, you can:
1. Check network connection
2. Use a proxy:
```bash
poetry run download-models
```
3. Use a backup model:
```python
embedding_model="paraphrase-MiniLM-L3-v2"
```

### Ollama Connection Issue
1. Ensure Ollama service is running
2. Check environment variable configuration
3. Verify if the model is installed:
```bash
ollama list
```

## License

MIT 