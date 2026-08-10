# AI Workforce Intelligence Platform - Backend (Phase 1)

Production-ready, async FastAPI backend foundation integrated with Ollama (`qwen2.5:7b`) to assist with workforce skill analysis, learning path recommendations, and decision support.

## Phase 1 Architecture
```
backend/app/
├── main.py          # Application Factory
├── config.py        # Settings Management (Pydantic)
├── dependencies.py  # Service & Client Injections
├── api/             # HTTP Controllers (health, chat)
├── llm/             # Reusable Singleton ChatOllama client
├── schemas/         # Pydantic Request/Response models
├── services/        # Business logic & System Prompt handler
└── utils/           # Logging configuration
```

## Quick Start Instructions

1. **Activate Virtual Environment & Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Ensure Ollama Daemon is Running**:
   ```bash
   ollama run qwen2.5:7b
   ```

3. **Launch Backend Service**:
   ```bash
   uvicorn app.main:app --reload
   ```

4. **Verify Endpoints**:
   - `GET http://localhost:8000/` -> Root message
   - `GET http://localhost:8000/health` -> Health check status
   - `POST http://localhost:8000/chat` -> Send workforce queries
   - Interactive Docs: `http://localhost:8000/docs`
