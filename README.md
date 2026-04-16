# BookMind - Document Intelligence Platform

A full-stack web application with AI/RAG integration that processes book data and enables intelligent querying.

## Features

- **Book Management**: Upload, store, and manage book data
- **AI Insights**: Automatic summary generation, genre classification, sentiment analysis, and recommendations
- **RAG Pipeline**: Question-answering over book content with source citations
- **Web Scraping**: Automated book data collection from the web
- **REST API**: Full backend API with Django REST Framework
- **Modern UI**: Responsive frontend with Next.js and Tailwind CSS

## Tech Stack

- **Backend**: Django REST Framework (Python)
- **Database**: SQLite (metadata), ChromaDB (vectors)
- **Frontend**: Next.js with Tailwind CSS
- **AI Integration**: LM Studio (local LLM) or OpenAI API
- **Embeddings**: Sentence Transformers
- **Web Scraping**: Selenium + BeautifulSoup

## Setup Instructions

### Prerequisites

- Python 3.8+
- Node.js 18+
- LM Studio (optional, for local LLM)

### Backend Setup

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run migrations
python manage.py migrate

# Start development server
python manage.py runserver
```

The API will be available at `http://localhost:8000/api/`

### Frontend Setup

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

The frontend will be available at `http://localhost:3000`

### LM Studio Setup (Optional)

1. Download LM Studio from https://lmstudio.ai/
2. Open LM Studio and download a model (e.g., Llama 3, Mistral)
3. Start the local server on port 1234

## API Documentation

### GET Endpoints

| Endpoint | Description |
|----------|-------------|
| `GET /api/` | List all books |
| `GET /api/books/{id}/` | Get book details |
| `GET /api/books/{id}/insights/` | Get AI insights |
| `GET /api/books/{id}/related/` | Get related books |
| `GET /api/books/{id}/chunks/` | Get book chunks |
| `GET /api/qa/history/` | Get Q&A history |

### POST Endpoints

| Endpoint | Description |
|----------|-------------|
| `POST /api/seed/` | Load sample books |
| `POST /api/scrape/` | Scrape books from web |
| `POST /api/books/{id}/insights/` | Generate AI insights |
| `POST /api/qa/ask/` | Ask a question (RAG query) |

## Sample Q&A

### Example Questions and Answers

**Question**: "What is The Great Gatsby about?"
> **Answer**: The Great Gatsby is a novel set in the Jazz Age on Long Island, near New York City. The story follows the mysterious millionaire Jay Gatsby and explores themes of decadence, idealism, resistance to change, social upheaval, and excess. It's a story about the American Dream and the hollowness of wealth.

**Question**: "Who is the main character in 1984?"
> **Answer**: The main character is Winston Smith, who works at the Ministry of Truth in a dystopian totalitarian society. The novel depicts his growing rebellion against the Party's control over truth and facts.

**Question**: "What genre is Pride and Prejudice?"
> **Answer**: Pride and Prejudice is a Romance novel that charts the emotional development of Elizabeth Bennet. It explores themes of love, reputation, and class in Regency-era England.

## Screenshots

### Dashboard
- Hero section with search bar
- Book grid with cards showing title, author, rating, and cover
- Buttons to load sample books or scrape from web

### Book Detail Page
- Book cover image
- Title, author, rating, genre
- Description
- Ask Question interface
- AI Insights cards (summary, genre, sentiment, recommendations)

### Q&A Page
- Book selection dropdown
- Question input with submit
- Answer display with source citations
- Recent questions history

## Configuration

### Environment Variables

For the frontend, create a `.env.local` file:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000/api
```

### Settings

In `backend/backend/settings.py`, you can configure:

- `EMBEDDING_MODEL`: Sentence transformer model (default: `sentence-transformers/all-MiniLM-L6-v2`)
- `CHUNK_SIZE`: Text chunk size for RAG (default: 500)
- `CHUNK_OVERLAP`: Overlap between chunks (default: 50)
- `LLM_BASE_URL`: LLM API endpoint (default: `http://localhost:1234/v1`)
- `LLM_MODEL`: Model name for LLM

## Project Structure

```
├── backend/
│   ├── backend/          # Django project settings
│   ├── books/             # Main app with models, views, serializers
│   │   ├── models.py      # Database models
│   │   ├── views.py       # API views
│   │   ├── serializers.py # DRF serializers
│   │   ├── vector_store.py # ChromaDB integration
│   │   ├── llm_integration.py # LLM integration
│   │   ├── scraper.py     # Web scraping
│   │   └── urls.py        # URL routing
│   └── manage.py
├── frontend/
│   ├── app/               # Next.js pages
│   ├── components/        # React components
│   └── lib/               # API utilities
├── requirements.txt       # Python dependencies
└── README.md
```

## License

MIT License
