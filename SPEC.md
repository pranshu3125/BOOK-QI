# Document Intelligence Platform - Specification

## Project Overview
- **Project Name**: BookMind - Document Intelligence Platform
- **Type**: Full-stack Web Application with AI/RAG Integration
- **Core Functionality**: Process book data, generate AI insights, enable intelligent querying via RAG pipeline
- **Target Users**: Book enthusiasts, researchers, students

## Tech Stack
- **Backend**: Django REST Framework (Python)
- **Database**: MySQL (metadata), ChromaDB (vectors)
- **Frontend**: Next.js with Tailwind CSS
- **AI Integration**: LM Studio (local LLM) or OpenAI API
- **Web Scraping**: Selenium + BeautifulSoup
- **Embeddings**: Sentence Transformers

## UI/UX Specification

### Color Palette
- **Primary**: `#1E3A5F` (Deep Navy Blue)
- **Secondary**: `#4A90A4` (Soft Teal)
- **Accent**: `#F7931E` (Warm Orange)
- **Background**: `#F8FAFC` (Light Gray)
- **Surface**: `#FFFFFF` (White)
- **Text Primary**: `#1A1A2E` (Dark Blue)
- **Text Secondary**: `#64748B` (Slate Gray)
- **Success**: `#10B981` (Emerald)
- **Error**: `#EF4444` (Red)

### Typography
- **Font Family**: Inter (Google Fonts)
- **Headings**: 
  - H1: 32px, Bold
  - H2: 24px, SemiBold
  - H3: 20px, SemiBold
- **Body**: 16px, Regular
- **Small**: 14px, Regular

### Layout Structure
- **Header**: Fixed top navigation with logo, nav links
- **Sidebar**: Left sidebar for book categories (desktop only)
- **Main Content**: Responsive grid layout
- **Footer**: Simple footer with copyright

### Responsive Breakpoints
- Mobile: < 640px
- Tablet: 640px - 1024px
- Desktop: > 1024px

### Pages

#### 1. Dashboard/Book Listing Page (`/`)
- Hero section with search bar
- Book cards in responsive grid (3 columns desktop, 2 tablet, 1 mobile)
- Each card shows: cover image, title, author, rating, brief description
- Filter/sort options
- Pagination

#### 2. Book Detail Page (`/book/[id]`)
- Book cover image (left)
- Book details (right): title, author, description, rating, genre
- AI Insights section: summary, genre classification, recommendations
- Q&A section with chat interface
- Related books carousel

#### 3. Q&A Interface (`/qa`)
- Question input with voice input option
- Answer display with source citations
- Chat history sidebar
- Loading states with animations

### Components

#### BookCard
- Rounded corners (12px)
- Shadow on hover
- Hover scale effect (1.02)
- Cover image with aspect ratio 2:3
- Rating stars display

#### QuestionInput
- Rounded textarea
- Send button with icon
- Loading spinner during API call
- Character count

#### AnswerCard
- Gradient border accent
- Source citations in blockquotes
- Copy to clipboard button
- Loading skeleton animation

#### InsightCard
- Icon header
- Collapsible content
- Refresh button for regeneration

## Database Schema

### Books Table
```python
class Book(models.Model):
    title = models.CharField(max_length=500)
    author = models.CharField(max_length=300)
    description = models.TextField(blank=True)
    rating = models.FloatField(null=True)
    review_count = models.IntegerField(default=0)
    genre = models.CharField(max_length=100, blank=True)
    cover_url = models.URLField(blank=True)
    book_url = models.URLField(blank=True)
    price = models.CharField(max_length=50, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
```

### BookChunks Table (for RAG)
```python
class BookChunk(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    chunk_text = models.TextField()
    chunk_index = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
```

### QAHistory Table
```python
class QAHistory(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE, null=True)
    question = models.TextField()
    answer = models.TextField()
    sources = models.JSONField(default=list)
    created_at = models.DateTimeField(auto_now_add=True)
```

### AIInsights Table
```python
class AIInsights(models.Model):
    book = models.OneToOneField(Book, on_delete=models.CASCADE)
    summary = models.TextField(blank=True)
    genre_prediction = models.CharField(max_length=100, blank=True)
    sentiment = models.CharField(max_length=50, blank=True)
    recommendations = models.JSONField(default=list)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
```

## API Endpoints

### GET APIs
1. `GET /api/books/` - List all books with pagination
2. `GET /api/books/{id}/` - Get book details
3. `GET /api/books/{id}/chunks/` - Get book chunks for RAG
4. `GET /api/books/{id}/insights/` - Get AI insights
5. `GET /api/books/{id}/related/` - Get related books
6. `GET /api/qa/history/` - Get Q&A history

### POST APIs
1. `POST /api/books/` - Upload/create new book
2. `POST /api/books/scrape/` - Scrape books from web
3. `POST /api/books/{id}/insights/generate/` - Generate AI insights
4. `POST /api/qa/ask/` - Ask question (RAG query)
5. `POST /api/embeddings/generate/` - Generate embeddings for book

## RAG Pipeline

1. **Text Chunking**: 
   - Split book content into overlapping chunks (500 chars, 50 overlap)
   - Store chunks in ChromaDB with book metadata

2. **Embedding Generation**:
   - Use sentence-transformers/all-MiniLM-L6-v2
   - Generate embeddings on-demand or in background

3. **Question Answering**:
   - Generate embedding for user question
   - Perform similarity search in ChromaDB
   - Retrieve top-k relevant chunks
   - Construct prompt with context
   - Send to LLM (LM Studio or OpenAI)
   - Return answer with source citations

## Web Scraping

- Use Selenium to navigate book sites
- Extract: title, author, description, rating, reviews, cover image, genre
- Store scraped data in database
- Generate embeddings for scraped content
- Handle pagination for multiple pages

## Acceptance Criteria

### Functional
- [ ] All CRUD operations work for books
- [ ] RAG pipeline returns relevant answers with citations
- [ ] AI insights generate summary, genre, recommendations
- [ ] Web scraping collects book data successfully
- [ ] All API endpoints return proper responses

### UI/UX
- [ ] Responsive design works on all breakpoints
- [ ] Loading states show during API calls
- [ ] Error states display meaningful messages
- [ ] Animations are smooth and purposeful

### Performance
- [ ] Page load time < 2 seconds
- [ ] API response time < 1 second (cached)
- [ ] Embedding generation optimized with caching
