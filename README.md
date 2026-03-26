# Simple Chatbot API

![Python](https://img.shields.io/badge/Python-3.11%2B-blue?style=flat-square&logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-0.129%2B-009688?style=flat-square&logo=fastapi)
![SQLModel](https://img.shields.io/badge/SQLModel-ORM-red?style=flat-square)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-336791?style=flat-square&logo=postgresql)
![OpenAI](https://img.shields.io/badge/OpenAI-API-412991?style=flat-square&logo=openai)

## Status

![Version](https://img.shields.io/badge/version-0.0.0-blue?style=flat-square)
![Last Commit](https://img.shields.io/github/last-commit/chris-kechagias/simple-chatbot-api?style=flat-square)
![Commits](https://img.shields.io/github/commit-activity/m/chris-kechagias/simple-chatbot-api?style=flat-square&label=Activity)
![License](https://img.shields.io/github/license/chris-kechagias/simple-chatbot-api?style=flat-square)
![In Progress](https://img.shields.io/badge/status-in%20progress-orange?style=flat-square)

---

## About

A FastAPI-powered conversational AI service using OpenAI, with full conversation management and RAG-based retail inventory assistance. Part of a larger portfolio project — built incrementally, PR by PR.

**Phases:**
- ~~Phase 1 — Core chat API with conversation memory (PostgreSQL)~~ ✅
- Phase 2 — Full CRUD, context window, auto-title, prompt management & streaming -- in progress
- Phase 3 — RAG over retail inventory data

---

## Project Structure

```
simple-chatbot-api/
├── main.py                  # App launcher
├── app/
│   ├── core/                # Infrastructure (config, database, logging, errors)
│   ├── routers/             # HTTP layer — thin, no business logic
│   ├── controllers/         # Business logic & orchestration
│   ├── services/            # External API clients (OpenAI, etc.)
│   └── models/              # Pydantic & SQLModel schemas
└── tests/                   # Test suite
```

---

## Installation

### Prerequisites
- Python 3.11+
- PostgreSQL
- An OpenAI API key

### Setup

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
