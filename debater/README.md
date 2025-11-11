# 🎭 AI Debate System

An AI-powered debate system where different LLM models debate each other on any proposition, followed by AI adjudication of the results.

## 🌟 Features

- **Multi-Model Support**: Claude (Anthropic), GPT (OpenAI), and Gemini (Google)
- **Structured Debates**: 5 turns per side with alternating arguments
- **AI Adjudication**: Automated scoring and reasoning by a judge model
- **Gradio Frontend**: Clean, intuitive web interface
- **FastAPI Backend**: Robust REST API with CORS support
- **Microservices Architecture**: Separately deployable frontend and backend
- **Cloud-Ready**: Configured for Google Cloud Run deployment

## 📁 Project Structure

```
debater/
├── backend/                 # FastAPI backend service
│   ├── app/
│   │   ├── routes/         # API routes
│   │   │   ├── debate.py   # Debate endpoints
│   │   │   ├── rag.py      # RAG endpoints (scaffold)
│   │   │   └── mcp.py      # MCP endpoints (scaffold)
│   │   ├── models/         # Pydantic models
│   │   ├── services/       # Business logic
│   │   │   ├── llm_service.py      # LLM integrations
│   │   │   └── debate_service.py   # Debate orchestration
│   │   └── storage/        # Data storage
│   │       └── memory_store.py     # In-memory storage
│   ├── requirements.txt
│   └── .env.example
│
├── frontend/               # Gradio frontend application
│   ├── app.py             # Main Gradio application
│   ├── requirements.txt
│   └── .env.example
│
└── README.md
```

## 🚀 Local Development Setup

### Prerequisites

- Python 3.11 or higher
- API keys for at least one LLM provider:
  - Anthropic API key (for Claude models)
  - OpenAI API key (for GPT models)
  - Google API key (for Gemini models)

### Backend Setup

1. **Navigate to backend directory:**
   ```bash
   cd debater/backend
   ```

2. **Create virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment (optional):**
   ```bash
   cp .env.example .env
   # Edit .env if you want to configure defaults
   ```

5. **Run the backend:**
   ```bash
   python -m uvicorn app.main:app --host 0.0.0.0 --port 9000 --reload
   ```

   The backend will be available at `http://localhost:9000`
   - API documentation: `http://localhost:9000/docs`
   - Alternative docs: `http://localhost:9000/redoc`

### Frontend Setup

1. **Open a new terminal and navigate to frontend directory:**
   ```bash
   cd debater/frontend
   ```

2. **Create virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure backend URL (if needed):**
   ```bash
   cp .env.example .env
   # Edit .env to update BACKEND_URL if backend is not on localhost:9000
   ```

5. **Run the frontend:**
   ```bash
   python app.py
   ```

   The frontend will be available at `http://localhost:8000`

## 📖 How to Use

1. **Start both services** (backend on port 9000, frontend on port 8000)

2. **Open the Gradio interface** at `http://localhost:8000`

3. **Enter API Keys**: Provide keys for the model providers you want to use

4. **Create a Debate**:
   - Enter a proposition (debate topic)
   - Select a model to argue FOR the motion
   - Select a model to argue AGAINST the motion
   - Click "Create Debate"

5. **Start the Debate**:
   - Click "Start Debate" to run the full 5-turn debate
   - Watch as both models present their arguments

6. **Adjudicate**:
   - Select a judge model from the dropdown
   - Click "Adjudicate Debate"
   - Review the scores and reasoning

## 🔌 API Endpoints

### Debate Routes (`/debate`)

- `POST /debate/create` - Create a new debate
- `GET /debate/{debate_id}` - Get debate status
- `POST /debate/{debate_id}/start` - Start/continue debate
- `POST /debate/{debate_id}/adjudicate` - Adjudicate completed debate
- `GET /debate/` - List all debates
- `GET /debate/models/available` - Get available models

### RAG Routes (`/rag`) - Scaffold

- `GET /rag/` - RAG root (placeholder)
- `GET /rag/health` - Health check

### MCP Routes (`/mcp`) - Scaffold

- `GET /mcp/` - MCP root (placeholder)
- `GET /mcp/health` - Health check

## 🛠️ Extending the Project

### Adding New LLM Providers

1. **Update `backend/app/services/llm_service.py`**:
   - Add model names to class constants
   - Implement a new `_call_<provider>` method
   - Update `_get_provider` method

2. **Update frontend model list** in `frontend/app.py`:
   - Add new models to `AVAILABLE_MODELS`

### Adding RAG Functionality

1. **Implement in `backend/app/routes/rag.py`**:
   - Add vector database integration
   - Create document ingestion endpoints
   - Add retrieval endpoints

2. **Add services** in `backend/app/services/`:
   - Create `rag_service.py` for RAG logic
   - Integrate with debate system if needed

### Adding MCP Support

1. **Implement in `backend/app/routes/mcp.py`**:
   - Define MCP protocol handlers
   - Add context management endpoints

2. **Create MCP service** in `backend/app/services/mcp_service.py`

### Switching to Database Storage

1. **Install database dependencies**:
   ```bash
   pip install sqlalchemy databases asyncpg  # for PostgreSQL
   # or
   pip install sqlalchemy aiosqlite  # for SQLite
   ```

2. **Create database models** in `backend/app/models/db_models.py`

3. **Replace `memory_store.py`** with database implementation

4. **Update `.env`** with database connection string

## ☁️ Google Cloud Run Deployment

### Prerequisites

- Google Cloud Platform account
- `gcloud` CLI installed and authenticated
- Docker installed (optional, Cloud Build can handle this)

### Backend Deployment

1. **Create Dockerfile** in `backend/`:
   ```dockerfile
   FROM python:3.11-slim

   WORKDIR /app

   COPY requirements.txt .
   RUN pip install --no-cache-dir -r requirements.txt

   COPY app ./app

   EXPOSE 9000

   CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "9000"]
   ```

2. **Build and deploy**:
   ```bash
   cd debater/backend

   # Build and deploy in one command
   gcloud run deploy debate-backend \
     --source . \
     --platform managed \
     --region us-central1 \
     --allow-unauthenticated \
     --port 9000

   # Note the service URL from the output
   ```

3. **Configure environment variables** (if needed):
   ```bash
   gcloud run services update debate-backend \
     --update-env-vars KEY=value
   ```

### Frontend Deployment

1. **Update backend URL** in `frontend/app.py`:
   ```python
   BACKEND_URL = "https://debate-backend-xxxxx.run.app"  # Your backend URL
   ```

2. **Create Dockerfile** in `frontend/`:
   ```dockerfile
   FROM python:3.11-slim

   WORKDIR /app

   COPY requirements.txt .
   RUN pip install --no-cache-dir -r requirements.txt

   COPY app.py .

   EXPOSE 8000

   CMD ["python", "app.py"]
   ```

3. **Build and deploy**:
   ```bash
   cd debater/frontend

   # Build and deploy
   gcloud run deploy debate-frontend \
     --source . \
     --platform managed \
     --region us-central1 \
     --allow-unauthenticated \
     --port 8000
   ```

### Post-Deployment Configuration

1. **Update CORS** in backend if needed:
   ```python
   # In backend/app/main.py
   allow_origins=["https://debate-frontend-xxxxx.run.app"]
   ```

2. **Configure custom domains** (optional):
   ```bash
   gcloud run domain-mappings create \
     --service debate-frontend \
     --domain your-domain.com
   ```

3. **Set up monitoring**:
   - Enable Cloud Logging
   - Set up error reporting
   - Configure alerts

## 🧪 Testing

### Manual Testing

1. **Test backend API**:
   ```bash
   # Health check
   curl http://localhost:9000/health

   # Get available models
   curl http://localhost:9000/debate/models/available

   # Create debate
   curl -X POST http://localhost:9000/debate/create \
     -H "Content-Type: application/json" \
     -d '{
       "proposition": "AI will benefit humanity",
       "for_model": "claude-sonnet-4-5-20250929",
       "against_model": "gpt-4o"
     }'
   ```

2. **Test frontend**: Open browser and interact with UI

### Adding Automated Tests

1. **Install testing dependencies**:
   ```bash
   pip install pytest pytest-asyncio httpx
   ```

2. **Create test files** in `backend/tests/`:
   - `test_routes.py` - Test API endpoints
   - `test_services.py` - Test business logic
   - `test_models.py` - Test data models

3. **Run tests**:
   ```bash
   pytest
   ```

## 🐛 Troubleshooting

### Backend won't start
- Check if port 9000 is already in use
- Verify Python version (3.11+)
- Ensure all dependencies are installed

### Frontend can't connect to backend
- Verify backend is running on correct port
- Check `BACKEND_URL` in frontend configuration
- Verify CORS settings in backend

### LLM API errors
- Verify API keys are correct
- Check API rate limits
- Ensure sufficient API credits

### Cloud Run deployment issues
- Check service logs: `gcloud run services logs read SERVICE_NAME`
- Verify port configuration matches Dockerfile EXPOSE
- Ensure authentication is properly configured

## 📝 Development Tips

1. **Use API documentation**: Visit `/docs` on the backend for interactive API testing

2. **Monitor logs**: Both services output useful debugging information

3. **Iterate quickly**: Use `--reload` flag with uvicorn for hot-reloading

4. **Test with different models**: Each model has unique characteristics

5. **Optimize costs**: Be mindful of API usage, especially with multiple turns

## 📄 License

This project is provided as-is for educational and development purposes.

## 🤝 Contributing

Contributions welcome! Areas for improvement:
- Database persistence
- User authentication
- Debate history and analytics
- More LLM providers
- Advanced adjudication criteria
- Streaming responses
- WebSocket support for real-time updates

## 📞 Support

For issues or questions:
1. Check the troubleshooting section
2. Review API documentation at `/docs`
3. Examine service logs
4. Open an issue in the repository

---

Built with ❤️ using FastAPI, Gradio, and cutting-edge LLMs
