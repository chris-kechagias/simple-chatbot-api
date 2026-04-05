# Simple Chatbot API

![Python](https://img.shields.io/badge/Python-3.11%2B-blue?style=flat-square&logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-0.129%2B-009688?style=flat-square&logo=fastapi)
![SQLModel](https://img.shields.io/badge/SQLModel-ORM-red?style=flat-square)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-336791?style=flat-square&logo=postgresql)
![OpenAI](https://img.shields.io/badge/OpenAI-API-412991?style=flat-square&logo=openai)
![Docker](https://img.shields.io/badge/Docker-ready-2496ED?style=flat-square&logo=docker)
![uv](https://img.shields.io/badge/uv-package%20manager-blueviolet?style=flat-square)

## Status

![Version](https://img.shields.io/badge/version-0.0.0-blue?style=flat-square)
![Last Commit](https://img.shields.io/github/last-commit/chris-kechagias/simple-chatbot-api?style=flat-square)
![Commits](https://img.shields.io/github/commit-activity/m/chris-kechagias/simple-chatbot-api?style=flat-square&label=Activity)
![License](https://img.shields.io/github/license/chris-kechagias/simple-chatbot-api?style=flat-square)
![In Progress](https://img.shields.io/badge/status-in%20progress-orange?style=flat-square)

---

## About

A FastAPI-powered conversational AI service using OpenAI, with full conversation management, streaming responses, token-based context trimming, rolling summarization, and a composable prompt system. Part of a larger portfolio project — built incrementally, PR by PR.

**Phases:**
- ~~Phase 1 — Core chat API with conversation memory (PostgreSQL)~~ ✅
- ~~Phase 2 — Full CRUD, context window, auto-title, streaming & composable prompt system~~ ✅
- Phase 3 — RAG over retail inventory data

---

## Project Structure

```
simple-chatbot-api/
├── main.py                  # App launcher
├── Dockerfile               # Container image definition
├── docker-compose.yml       # Multi-service orchestration (API + PostgreSQL)
├── app/
│   ├── core/                # Infrastructure (config, database, logging, errors)
│   ├── routers/             # HTTP layer — thin, no business logic
│   ├── controllers/         # Business logic & orchestration
│   ├── services/            # OpenAI client, summarizer, prompt loader
│   ├── utils/               # Shared utilities (token counting, etc.)
│   └── models/              # Pydantic & SQLModel schemas
├── prompts/                 # Composable prompt library
│   ├── prompts.yaml         # Control layer — defines prompt compositions
│   ├── base/                # Base prompt templates
│   ├── core/                # Identity and persona
│   ├── styles/              # Tone styles (casual, formal, sarcastic)
│   ├── rules/               # Behavioral rules (communication, factuality, etc.)
│   └── intensity/           # Intensity calibration (low, medium, high)
└── tests/                   # Test suite
```

---

## Installation

### Option A — Docker (recommended)

1. Clone the repo:
```bash
git clone https://github.com/chris-kechagias/simple-chatbot-api.git
cd simple-chatbot-api
```

2. Copy the example env file and fill in your values:
```bash
cp .env.example .env
```

3. Build and start:
```bash
task build       # build image and start containers (detached)
task start       # start without rebuilding
task stop        # stop containers
task restart     # stop and restart
task logs        # follow container logs
```

Or using Docker directly:
```bash
docker compose up --build -d
```

The API will be available at `http://localhost:8000`.

---

### Option B — Local

**Prerequisites:** Python 3.11+, PostgreSQL, an OpenAI API key

1. Clone the repo and install dependencies:
```bash
git clone https://github.com/chris-kechagias/simple-chatbot-api.git
cd simple-chatbot-api
uv sync
```

2. Copy the example env file and fill in your values:
```bash
cp .env.example .env
```

3. Run the API locally:
```bash
task dev
```

---

### First Request

This API has no authentication yet. Every request requires a `user_id` UUID that you generate yourself — think of it as your user identifier until auth is added.

Generate one:
```bash
python -c "import uuid; print(uuid.uuid4())"
```

Use that UUID as `user_id` in all your requests. For new conversations, set `conversation_id` to `null` or omit it entirely.

---

## Author

**Chris Kechagias**

[![Medium Badge](https://img.shields.io/badge/@ck.chris.kechagias-black?style=flat&logo=medium&logoColor=white&link=https://medium.com/@ck.chris.kechagias)](https://medium.com/@ck.chris.kechagias)<br>
[![GitHub](https://skillicons.dev/icons?i=github)](https://github.com/chris-kechagias)<br>
[![LinkedIn](https://skillicons.dev/icons?i=linkedin)](https://www.linkedin.com/in/chkechagias)<br>
[![dev.to](https://skillicons.dev/icons?i=devto)](https://dev.to/kris_k)<br>

*Transitioning from retail operations to AI engineering.*

**⭐ If you find this project helpful, consider giving it a star!**
