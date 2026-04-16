# BookIQ — Document Intelligence Platform

> AI-powered book discovery and Q&A with RAG pipeline

## Screenshots
[Add 4 screenshots after running the app - label them clearly]

## Architecture
books.toscrape.com → Selenium scraper → SQLite
↓
sentence-transformers
↓
ChromaDB (vectors)
↑
User question → embed → similarity search → Claude/LM Studio → answer + citations

## Tech Stack
| Layer | Technology |
|-------|-----------|
| Backend | Django + Django REST Framework |
| Database | SQLite (dev) + ChromaDB |
| AI | Anthropic Claude API or LM Studio (local) |
| Embeddings | sentence-transformers all-MiniLM-L6-v2 |
| Scraping | Selenium + BeautifulSoup |
| Frontend | Next.js 14 (App Router) + Tailwind CSS |

## Setup

### Backend
```bash
cd backend
pip install -r ../requirements.txt
cp .env.example .env   # add your ANTHROPIC_API_KEY
python manage.py migrate
python manage.py runserver
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

Open http://localhost:3000

## Environment Variables (.env)
ANTHROPIC_API_KEY=your_key_here
LLM_PROVIDER=claude          # or 'lmstudio'
LLM_BASE_URL=http://localhost:1234/v1   # only for lmstudio

## API Documentation
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /api/ | List all books |
| GET | /api/books/{id}/ | Book detail |
| GET | /api/books/{id}/related/ | Related books |
| GET | /api/books/{id}/insights/ | AI insights |
| GET | /api/qa/history/ | Q&A history |
| POST | /api/seed/ | Load sample books |
| POST | /api/scrape/ | Scrape books from web |
| POST | /api/books/{id}/insights/ | Generate AI insights |
| POST | /api/books/{id}/embeddings/ | Generate embeddings |
| POST | /api/qa/ask/ | Ask a question (RAG) |

## Sample Q&A
**Q: What is The Great Gatsby about?**
A: The Great Gatsby follows narrator Nick Carraway in 1920s New York... [Source 1]

**Q: Which fantasy books are available?**
A: Based on the library, The Hobbit by Tolkien and Harry Potter... [Source 1][Source 2]

**Q: What is the highest rated book?**
A: Harry Potter and the Sorcerer's Stone holds a 4.9 rating... [Source 1]

**Q: Recommend a book similar to 1984**
A: If you enjoyed 1984's dystopian themes, you might enjoy... [Source 1]

**Q: What are the main themes in Pride and Prejudice?**
A: Pride and Prejudice explores social class, marriage, and personal growth... [Source 1]

## Caching
AI responses are cached using Django's file-based cache (24hr TTL).
Cache keys: llm_{md5(prompt)} — prevents redundant API calls.

## Bonus Features Implemented
- Persistent file-based caching of all LLM responses
- Cross-book global RAG search (no book selection needed)
- Overlapping chunk windows (chunk_size=500, overlap=50)
- Dual LLM support: Claude API + LM Studio (toggle via env var)
- Session-based Q&A history
- Genre filter pills on Dashboard
- Sentiment score (0.0-1.0) in AI Insights