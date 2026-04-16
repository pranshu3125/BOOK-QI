# BOOK-QI - Document Intelligence Platform

> AI-powered book discovery, analysis, and Q&A with RAG pipeline

## Overview

BOOK-QI is a full-stack web application that demonstrates document intelligence by processing book data from the web, generating AI-powered insights, and enabling intelligent question-answering over books using Retrieval-Augmented Generation (RAG).

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                      FRONTEND (Next.js + Tailwind)              │
│  Dashboard  │  Book Detail  │  Q&A Interface                │
└──────────────────────┬──────────────────────────────────┘
                       │ HTTP API
┌──────────────────────▼──────────────────────────────────┐
│                 BACKEND (Django REST Framework)            │
│  Views → Services → Models                             │
│     │         │        │                                │
│     ▼         ▼        ▼                                │
│  Scraper  RAG Engine  Insights                         │
│     │         │        │                                │
│     ▼         ▼        ▼                                │
│  ┌────────┐ ┌────────┐ ┌─────────┐                   │
│  │Selenium │ │ChromaDB │ │Django   │                   │
│  │Scraping │ │Vectors │ │MySQL    │                   │
│  └────────┘ └────────┘ └─────────┘                   │
└───────────────────────────────────────────────────────┘
                       │
                       ▼
┌───────────────────────────────────────────────────────┐
│              AI Services (LLM Provider)                  │
│  OpenAI API / Claude API / LM Studio (local)          │
└───────────────────────────────────────────────────────┘
```

## Tech Stack

| Layer | Technology |
|-------|------------|
| Frontend | Next.js 14 (App Router) + Tailwind CSS |
| Backend | Django + Django REST Framework |
| Database | MySQL (metadata) + ChromaDB (vectors) |
| AI | OpenAI / Claude / LM Studio |
| Embeddings | sentence-transformers (all-MiniLM-L6-v2) |
| Scraping | Selenium + BeautifulSoup |

## Features

### Core Features
- **Book Management**: Upload, store, and manage book data
- **Web Scraping**: Automated data collection from multiple sources
- **AI Insights**: Summary, genre classification, sentiment, recommendations
- **RAG Pipeline**: Question answering with source citations
- **REST API**: Full Django REST Framework API

### Implemented Insights
- Summary generation from book descriptions
- Genre classification
- Sentiment analysis with score (0.0-1.0)
- Book recommendations based on genre/author

### RAG Pipeline
1. User asks a question
2. Question is embedded using sentence-transformers
3. Similar chunks retrieved from ChromaDB vector store
4. Context built from retrieved chunks
5. LLM generates contextual answer
6. Answer returned with source citations

## Quick Setup

### Prerequisites
- Python 3.8+
- Node.js 18+
- MySQL 8.0+ (optional, SQLite fallback available)
- Chrome browser (for Selenium)

### 1. Clone and Install Backend

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r ../requirements.txt

# Copy environment file
cp .env.example .env
# Edit .env with your settings
```

### 2. Configure Database (MySQL)

Create MySQL database:
```sql
CREATE DATABASE bookqi_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

Or use SQLite fallback:
```bash
# In .env or environment:
USE_SQLITE=true
```

### 3. Run Migrations

```bash
python manage.py migrate
python manage.py runserver
```

### 4. Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

### 5. Access the Application

- Frontend: http://localhost:3000
- Backend API: http://localhost:8000/api/
- Admin: http://localhost:8000/admin/

## Environment Variables

### Backend (.env)
```bash
# Database (MySQL)
MYSQL_DATABASE=bookqi_db
MYSQL_USER=root
MYSQL_PASSWORD=your_password
MYSQL_HOST=localhost
MYSQL_PORT=3306

# Or use SQLite
USE_SQLITE=true

# LLM Settings
LLM_PROVIDER=lmstudio  # or 'claude', 'openai'
LLM_BASE_URL=http://localhost:1234/v1
LLM_MODEL=local-model

# OpenAI (if using OpenAI)
OPENAI_API_KEY=sk-...

# Claude (if using Claude)
ANTHROPIC_API_KEY=sk-ant-...

# Security
DJANGO_SECRET_KEY=your-secret-key
```

### Frontend (.env.local)
```bash
NEXT_PUBLIC_API_URL=http://localhost:8000/api
```

## API Documentation

### Book Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/` | List all books |
| GET | `/api/books/{id}/` | Get book details |
| GET | `/api/books/{id}/related/` | Get related books |
| POST | `/api/seed/` | Load 8 sample books |
| POST | `/api/scrape/` | Scrape books from web |

### Insights Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/books/{id}/insights/` | Get AI insights |
| POST | `/api/books/{id}/insights/` | Generate insights |

### Q&A Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/qa/ask/` | Ask a RAG question |
| GET | `/api/qa/history/` | Get Q&A history |

### Example API Calls

```bash
# List books
curl http://localhost:8000/api/

# Load sample books
curl -X POST http://localhost:8000/api/seed/

# Scrape books (use specific source)
curl -X POST http://localhost:8000/api/scrape/ \
  -H "Content-Type: application/json" \
  -d '{"source": "toscrape", "count": 10, "num_pages": 2}'

# Get book insights
curl http://localhost:8000/api/books/1/insights/

# Ask a question (RAG)
curl -X POST http://localhost:8000/api/qa/ask/ \
  -H "Content-Type: application/json" \
  -d '{"question": "What is this book about?", "book_id": 1}'

# Ask without book (cross-book search)
curl -X POST http://localhost:8000/api/qa/ask/ \
  -H "Content-Type: application/json" \
  -d '{"question": "What are the main themes in these books?"}'
```

## Project Structure

```
BOOK-QI/
├── backend/
│   ├── backend/
│   │   ├── settings.py      # Django settings
│   │   ├── urls.py         # URL routing
│   │   └── wsgi.py
│   ├── books/
│   │   ├── models.py       # Database models
│   │   ├── views.py       # API views
│   │   ├── serializers.py
│   │   ├── urls.py
│   │   ├── vector_store.py     # ChromaDB integration
│   │   ├── llm_integration.py # LLM calls
│   │   ├── scraper.py          # Legacy scraper
│   │   └── migrations/
│   │   └── services/
│   │       ├── __init__.py
│   │       ├── scraper.py   # Multi-source scraper
│   │       ├── chunker.py  # Text chunking
│   │       ├── embeddings.py
│   │       ├── rag.py      # RAG pipeline
│   │       ├── insights.py
│   │       └── cache.py   # Response caching
│   ├── manage.py
│   └── .env.example
├── frontend/
│   ├── app/
│   │   ├── page.tsx       # Dashboard
│   │   ├── layout.tsx
│   │   ├── book/[id]/
│   │   └── qa/
│   ├── components/
│   ├── lib/
│   │   └── api.ts
│   ├── package.json
│   └── tailwind.config.js
├── requirements.txt
├── README.md
└── SPEC.md
```

## Sample Questions & Answers

**Q: What is The Great Gatsby about?**
> A: The Great Gatsby is a novel set in the Jazz Age on Long Island, near New York City. It depicts first-person narrator Nick Carraway's interactions with mysterious millionaire Jay Gatsby and explores themes of decadence, idealism, resistance to change, social upheaval, and excess. [Source 1: The Great Gatsby]

**Q: Which books are fantasy genre?**
> A: Based on our library, the fantasy books include The Hobbit (4.8 rating) by J.R.R. Tolkien and Harry Potter and the Sorcerer's Stone (4.9 rating) by J.K. Rowling. [Source 1], [Source 2]

**Q: What are the main themes in these books?**
> A: The books explore various themes including: the American Dream and social class (The Great Gatsby), totalitarianism and truth (1984), coming of age and identity (The Catcher in the Rye), romance and reputation (Pride and Prejudice). [Source 1-8]

## How It Works

### Scraping Pipeline
1. Source is validated (toscrape, openlibrary, gutenberg)
2. Selenium navigates to source pages
3. BeautifulSoup parses HTML
4. Book metadata extracted
5. Saves to database with chunks

### RAG Pipeline
1. User question embedded using sentence-transformers
2. ChromaDB similarity search retrieves top-k chunks
3. Context built from retrieved chunks with citations
4. LLM generates answer using context
5. Response includes source citations

### Caching
- Responses cached using Django file-based cache
- Cache key includes provider + model to avoid conflicts
- Default TTL: 24 hours

## Screenshots

[Add screenshots here after running the app:
1. Dashboard with book grid
2. Book detail page with insights
3. Q&A interface with citations
4. API browsable interface]

## Known Issues & Limitations

- Selenium requires Chrome browser installed
- LM Studio must be running for local LLM
- MySQL on Windows may need Visual Studio build tools
- OpenLibrary/Gutenberg scrapers planned but not implemented

## Future Improvements

- Add OpenLibrary scraper
- Add Celery for async tasks
- Add semantic chunking
- Improve error handling
- Add tests

## License

MIT License

## Credits

Built as a learning project for internship submission.