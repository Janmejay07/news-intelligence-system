# News Intelligence System

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Endee Vector DB](https://img.shields.io/badge/Vector%20DB-Endee-green.svg)](https://github.com/endee-io/endee)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**A modern AI-powered News Intelligence System** that combines free news APIs, semantic search via [Endee](https://github.com/endee-io/endee) vector database, RAG (Retrieval Augmented Generation), personalized recommendations, and agentic AI workflows.

---

## 📋 Project Overview

### Problem Statement

Staying informed in the digital age is challenging: news is scattered across sources, search is keyword-based, and synthesizing insights requires manual effort. Users need:

- **Semantic understanding** — find news by meaning, not just keywords
- **Intelligent Q&A** — get answers grounded in real news
- **Personalized discovery** — recommendations aligned with interests
- **Automated workflows** — agentic pipelines for search, summarize, recommend

### Solution

This system addresses these needs by:

1. **Ingesting** news from free APIs (no API key required)
2. **Storing** with weekly/monthly buckets and auto-deletion
3. **Indexing** in Endee for high-performance vector search
4. **Answering** via RAG with local LLM (Ollama)
5. **Recommending** based on semantic similarity
6. **Orchestrating** through agentic workflows

---

## 🏗️ System Design & Technical Approach

```
┌─────────────────────────────────────────────────────────────────────────┐
│                     News Intelligence System Architecture                  │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────────────────┐   │
│  │ Free News    │───▶│ News Storage │───▶│ Endee Vector Database     │   │
│  │ API (Saurav) │    │ Weekly/Monthly│    │ (Semantic Search)         │   │
│  │ No API key   │    │ Auto-delete  │    │ https://github.com/endee-io│   │
│  └──────────────┘    └──────────────┘    └────────────┬───────────────┘   │
│                                                       │                   │
│  ┌───────────────────────────────────────────────────┼─────────────────┐ │
│  │                    Application Layer               │                 │ │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐ │                 │ │
│  │  │ Semantic    │  │ RAG         │  │ Recommend   │ │                 │ │
│  │  │ Search      │  │ (Ollama)    │  │ Engine      │ │                 │ │
│  │  └─────────────┘  └─────────────┘  └─────────────┘ │                 │ │
│  │  ┌───────────────────────────────────────────────┐ │                 │ │
│  │  │           Agentic AI Workflows                │◀┘                 │ │
│  │  └──────────────────────────────────────────────┘                    │ │
│  └──────────────────────────────────────────────────────────────────────┘ │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

### Components

| Component | Technology | Purpose |
|-----------|------------|---------|
| **News Source** | [Saurav's NewsAPI](https://saurav.tech/NewsAPI/) | Free news, no API key |
| **Storage** | JSON files (weekly/monthly) | Retention with auto-deletion |
| **Vector DB** | [Endee](https://github.com/endee-io/endee) | Semantic search, HNSW indexing |
| **Embeddings** | sentence-transformers | all-MiniLM-L6-v2 (384-dim) |
| **LLM** | Ollama (local) | RAG generation, no API cost |
| **API** | FastAPI | REST endpoints |

---

## 🔧 How Endee Is Used

[Endee](https://github.com/endee-io/endee) is a high-performance vector database (up to 1B vectors on a single node). We use it as follows:

### 1. Index Creation

- **Index name**: `news_vectors`
- **Dimension**: 384 (all-MiniLM-L6-v2)
- **Space type**: cosine similarity
- **Precision**: INT8 (memory-efficient)

### 2. Vector Upsert

Each news article is embedded and stored with metadata:

```python
{
    "id": "article_hash",
    "vector": [0.1, -0.2, ...],  # 384-dim embedding
    "meta": {
        "title": "...",
        "description": "...",
        "url": "...",
        "category": "technology",
        "country": "us"
    }
}
```

### 3. Semantic Search

Queries are embedded and searched via Endee's HNSW index:

```python
results = index.query(vector=query_embedding, top_k=10, filter=[...])
```

### 4. Use Cases Enabled

- **Semantic Search** — "AI regulation in Europe" finds relevant articles
- **RAG** — Retrieved articles provide context for LLM answers
- **Recommendations** — Similarity to user interest vectors

---

## Forked Endee Repository

This project is built using a forked version of the Endee vector database.

Forked repository:
https://github.com/Janmejay07/endee

The forked Endee repository serves as the base vector database implementation for semantic search, RAG retrieval, and recommendation workflows in this project.

The system currently runs using the official Endee Docker image for stability, while the forked repository is maintained for customization and extension.

---

## 🚀 Setup & Execution

### Prerequisites

- Python 3.10+
- [Docker](https://www.docker.com/) (for Endee)
- [Ollama](https://ollama.ai/) (for local LLM)

### 1. Fork Endee (Required)

Fork [endee-io/endee](https://github.com/endee-io/endee) to your account:

```
https://github.com/Janmejay07/endee
```

This project uses the official Endee Docker image; you can swap to your fork if needed.

### 2. Clone This Repository

```bash
git clone https://github.com/Janmejay07/news-intelligence-system.git
cd news-intelligence-system
```

### 3. Create Virtual Environment

```bash
python -m venv .venv
.venv\Scripts\activate   # Windows
# source .venv/bin/activate  # Linux/macOS
```

### 4. Install Dependencies

```bash
pip install -r requirements.txt
```

### 5. Start Endee (Docker)

```bash
docker compose up -d
```

Endee runs on `http://localhost:8080`.

### 6. Install Ollama & Pull Model

```bash
# Install from https://ollama.ai/
ollama pull llama3.2
```

### 7. Configure Environment

```bash
copy .env.example .env   # Windows
# cp .env.example .env   # Linux/macOS
```

Edit `.env` if needed (defaults work for local dev).

### 8. Ingest News

```bash
python scripts/ingest.py
```

### 9. Run the API

```bash
python main.py
# or: uvicorn src.api.main:app --reload --port 8000
```

API: **http://localhost:8000** | Docs: **http://localhost:8000/docs**

---

## 📡 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | API info |
| GET | `/health` | Health check |
| POST | `/ingest` | Fetch & index news |
| POST | `/search` | Semantic search |
| POST | `/ask` | RAG Q&A |
| POST | `/recommend` | Personalized recommendations |
| POST | `/workflow?task=search\|ask\|recommend\|summarize` | Agentic workflow |

### Example: Semantic Search

```bash
curl -X POST http://localhost:8000/search \
  -H "Content-Type: application/json" \
  -d '{"query": "artificial intelligence regulation", "top_k": 5}'
```

### Example: RAG Ask

```bash
curl -X POST http://localhost:8000/ask \
  -H "Content-Type: application/json" \
  -d '{"query": "What are the latest developments in AI policy?"}'
```

### Example: Recommendations

```bash
curl -X POST http://localhost:8000/recommend \
  -H "Content-Type: application/json" \
  -d '{"interests": ["machine learning", "climate tech"], "top_k": 10}'
```

---

## 📁 Project Structure

```
news-intelligence-system/
├── config/
│   └── settings.py          # Configuration
├── src/
│   ├── news_ingestion/      # Fetch & storage
│   ├── embeddings/          # Sentence transformers
│   ├── vector_db/           # Endee client
│   ├── rag/                 # RAG pipeline
│   ├── recommendations/     # Recommendation engine
│   ├── agents/              # Agentic workflows
│   └── api/                 # FastAPI app
├── scripts/
│   └── ingest.py            # Ingestion script
├── docker-compose.yml       # Endee service
├── requirements.txt
├── main.py
└── README.md
```

---

## 🔄 Retention & Auto-Deletion

- **Weekly buckets**: `data/news/weekly/YYYY-Www/`
- **Monthly buckets**: `data/news/monthly/YYYY-MM/`
- **Retention**: 4 weeks (weekly), 3 months (monthly) — configurable
- **Auto-deletion**: Runs on each ingest; removes buckets beyond retention

---

## 📜 License

MIT License. See [LICENSE](LICENSE) for details.

---

## 🙏 Acknowledgments

- [Endee](https://github.com/endee-io/endee) — Vector database
- [Saurav's NewsAPI](https://saurav.tech/NewsAPI/) — Free news API
- [Ollama](https://ollama.ai/) — Local LLM
- [sentence-transformers](https://www.sbert.net/) — Embeddings
