# Research Public

This repository contains various research projects and experiments.

## Projects

### 🎭 AI Debate System (`debater/`)

An AI-powered debate system where different LLM models (Claude, GPT, Gemini) debate each other on any proposition, followed by AI adjudication.

**Quick Start:**
- Backend (FastAPI): `cd debater/backend && pip install -r requirements.txt && python -m uvicorn app.main:app --port 9000`
- Frontend (Gradio): `cd debater/frontend && pip install -r requirements.txt && python app.py`

**Full Documentation:** See [debater/README.md](./debater/README.md) for complete setup, development, and deployment instructions.

**Features:**
- Multi-model support (Claude, GPT, Gemini)
- Structured 5-turn debates with AI adjudication
- Separate FastAPI backend and Gradio frontend
- Google Cloud Run deployment ready
