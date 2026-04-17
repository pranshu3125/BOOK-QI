# BOOK-QI - Document Intelligence Platform

> A full-stack web application for AI-powered book discovery, analysis, and intelligent question-answering

## Project Overview

BOOK-QI is a document intelligence platform that demonstrates end-to-end implementation of:
- Web scraping for automated data collection
- Vector-based similarity search for Retrieval-Augmented Generation (RAG)
- AI-powered insights generation
- RESTful API design with Django
- Responsive frontend with modern web technologies

This project was built as a demonstration of full-stack development skills with AI/RAG integration, suitable for technical evaluation and learning purposes.

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                      FRONTEND                          │
│  Next.js 14 (App Router) + Tailwind CSS              │
│  Dashboard │ Book Detail │ Q&A Interface              │
└──────────────────────┬──────────────────────────────────┘
                       │ HTTP/REST API
┌──────────────────────▼──────────────────────────────────┐
│                 BACKEND                               │
│  Django REST Framework + Python                     │
│                                                   │
│  ┌──────────────────────────────────────────────┐  │
│  │           Service Layer (Modular Design)          │  │
│  │  scraper │ chunker │ embeddings │ rag │ insights│  │
│  └──────────────────────────────────────────────┘  │
└──────────────────────┬──────────────────────────────────┘
                       │
        ┌──────────────┼──────────────┐
        ▼              ▼              ▼
   ┌─────────┐   ┌─────────┐   ┌──────────┐
   │ SQLite  │   │ChromaDB │   │   LLM   │
   │ (data)  │   │(vector) │   │(AI API) │
   └─────────┘   └─────────┘   └──────────┘
```

## Tech Stack & Rationale

| Technology | Why Used |
|------------|---------|
| **Django + DRF** | Robust Python web framework with built-in REST API support, excellent for learning and production |
| **SQLite** | Zero-configuration database for development; switches to MySQL for production scale |
| **ChromaDB** | Open-source vector database optimized similarity search; ideal for RAG implementation |
| **sentence-transformers** | Pre-trained embeddings (all-MiniLM-L6-v2); efficient and accurate for text similarity |
| **Selenium + BeautifulSoup** | Industry-standard web scraping; handles dynamic content well |
| **Next.js 14** | Modern React framework with App Router; excellent developer experience |
| **Tailwind CSS** | Utility-first CSS for rapid, responsive UI development |
| **LM Studio** (optional) | Local LLM hosting for development without API costs |

## Features Implemented

### 1. Book Management
- Database storage of book metadata (title, author, description, rating, genre, cover URL)
- Search and genre-based filtering
- Related book recommendations based on genre and author

### 2. Web Scraping Pipeline
- Automated data collection using Selenium WebDriver
- Multi-source architecture (easily extensible)
- Currently implements: books.toscrape.com (legal practice site)
- Safe parsing with error handling
- Bulk page scraping support

### 3. Document Processing
- Text chunking with overlapping windows (chunk_size=500, overlap=50)
- Metadata tracking per chunk (book_id, title, chunk_index, source)
- Embedding generation using sentence-transformers

### 4. RAG Pipeline
Complete implementation of Retrieval-Augmented Generation:

```
User Question → Embed → ChromaDB Search → Context Build → LLM → Answer + Citations
```

Features:
- Per-book and cross-book search
- Structured source citations with metadata
- Contextual answers with references

### 5. AI Insights
Four insight types implemented:

| Insight | Description |
|---------|-------------|
| **Summary** | Generated from book description |
| **Genre Classification** | Predicted genre (Fiction, Sci-Fi, Fantasy, etc.) |
| **Sentiment Analysis** | Label + score (0.0-1.0) |
| **Recommendations** | Similar books based on genre/author |

### 6. Caching
- Django file-based cache for AI responses
- Cache keys include provider + model to avoid conflicts
- 24-hour TTL to reduce redundant API calls

### 7. REST API
Clean, consistent API design:

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/` | GET | List all books |
| `/api/books/{id}/` | GET | Book details |
| `/api/books/{id}/related/` | GET | Related books |
| `/api/books/{id}/insights/` | GET/POST | AI insights |
| `/api/seed/` | POST | Load sample books |
| `/api/scrape/` | POST | Scrape from web |
| `/api/qa/ask/` | POST | RAG question |
| `/api/qa/history/` | GET | Q&A history |

## Setup Instructions

### Prerequisites
- Python 3.8+
- Node.js 18+
- Chrome browser (for Selenium)

### Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
venv\Scripts\activate  # Windows

# Install dependencies
pip install -r ../requirements.txt

# Run migrations
python manage.py migrate

# Start server
python manage.py runserver
```

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

### Access Points
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000/api/
- Admin Panel: http://localhost:8000/admin/

### Using MySQL (Optional)

The project defaults to SQLite. To use MySQL:

```bash
# Install MySQL client
pip install mysqlclient

# Set environment variables
set MYSQL_DATABASE=bookqi_db
set MYSQL_USER=root
set MYSQL_PASSWORD=your_password
set USE_SQLITE=false
```

## How to Use

### 1. Load Sample Books
Click "Load Sample Books" on the dashboard to seed 8 demo books.

### 2. Scrape Books
Use the API to scrape from web:
```bash
curl -X POST http://localhost:8000/api/scrape/ \
  -H "Content-Type: application/json" \
  -d '{"source": "toscrape", "count": 10, "num_pages": 2}'
```

### 3. View Book Details
Click any book to see full details including AI-generated insights.

### 4. Ask Questions
Use the Q&A section on book detail page or /qa for cross-book search.

Example questions:
- "What is this book about?"
- "Who is the main character?"
- "What genre does this book belong to?"
- "Suggest similar books"

## Project Structure

```
BOOK-QI/
├── backend/
│   ├── backend/
│   │   └── settings.py        # Django configuration
│   ├── books/
│   │   ├── models.py         # Database schema
│   │   ├── views.py         # API endpoints
│   ���   ��── serializers.py   # Data serialization
│   │   ├── urls.py         # URL routing
│   │   ├── vector_store.py # ChromaDB integration
│   │   ├── llm_integration.py # LLM calls
│   │   ├── scraper.py      # Legacy scraper
│   │   ├── migrations/
│   │   └── services/      # Service layer
│   │       ├── scraper.py  # Multi-source scraper
│   │       ├── chunker.py   # Text chunking
│   │       ├── embeddings.py # Vector generation
│   │       ├── rag.py      # RAG pipeline
│   │       ├── insights.py  # AI insights
│   │       └── cache.py    # Response caching
│   └── manage.py
├── frontend/
│   ├── app/               # Next.js pages
│   ├── components/         # Reusable UI components
│   └── lib/             # API utilities
├── requirements.txt
└── README.md
```

## Understanding the RAG Pipeline

The core innovation is the Retrieval-Augmented Generation pipeline:

1. **Question Embedding**: User question converted to vector using sentence-transformers
2. **Retrieval**: ChromaDB finds similar text chunks from stored book data
3. **Context Building**: Retrieved chunks formatted with source citations
4. **Generation**: LLM generates answer using retrieved context
5. **Citation**: Response includes source references for verification

This approach ensures answers are grounded in actual book content, not hallucinations.

## API Examples

```bash
# List all books
GET http://localhost:8000/api/

# Book detail
GET http://localhost:8000/api/books/1/

# Get AI insights
GET http://localhost:8000/api/books/1/insights/

# Ask a question about specific book
POST http://localhost:8000/api/qa/ask/
{"question": "What is this book about?", "book_id": 1}

# Ask across all books (no book_id)
POST http://localhost:8000/api/qa/ask/
{"question": "What are the main themes?"}
```

## Sample Q&A

**Q: What is The Great Gatsby about?**
> A: The Great Gatsby is a novel set in the Jazz Age on Long Island, near New York City. It follows Nick Carraway's interactions with mysterious millionaire Jay Gatsby, exploring themes of decadence, idealism, and the American Dream. [Source 1: The Great Gatsby - book_description]

**Q: What genre is 1984?**
> A: 1984 is classified as Science Fiction, specifically dystopian fiction. [Source 1: 1984 - genre_prediction]

**Q: Recommend a fantasy book**
> A: Based on your library, I recommend The Hobbit (4.8 rating) by J.R.R. Tolkien or Harry Potter and the Sorcerer's Stone (4.9 rating) by J.K. Rowling. [Source 1-2]

## Limitations & Future Improvements

Known limitations and planned improvements:

| Area | Current State | Future Improvement |
|------|--------------|-------------------|
| Scraping | Single source (toscrape) | Add OpenLibrary, Gutenberg |
| Background Tasks | Synchronous | Add Celery for async processing |
| Chunking | Fixed-size overlapping | Semantic chunking |
| Search | Basic similarity | Hybrid search with keywords |
| UI | Functional | Advanced visualizations |

## Learning Outcomes

This project demonstrates:

- ✅ Full-stack web development (Django + Next.js)
- ✅ RESTful API design and consumption
- ✅ Vector databases and embeddings
- ✅ RAG pipeline implementation
- ✅ Web scraping automation
- ✅ AI/ML integration
- ✅ Database design (SQL + vector)
- ✅ Code organization and modularity

## License

MIT License

---

Built for demonstration and learning purposes.