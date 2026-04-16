from rest_framework import viewsets, status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView
from django.conf import settings
from django.db.models import Q
import logging

from .models import Book, BookChunk, AIInsights, QAHistory
from .serializers import BookSerializer, BookListSerializer, AIInsightsSerializer, QAHistorySerializer
from .vector_store import (
    add_chunks_to_vector_store, 
    similarity_search, delete_book_from_vector_store,
    add_chunks_to_global_store, global_similarity_search
)
from .llm_integration import (
    generate_summary, classify_genre, analyze_sentiment, 
    get_recommendations, rag_answer
)

# Import new services
from .services.scraper import scrape_books, get_available_sources, is_valid_source
from .services.chunker import chunk_text
from .services.rag import ask_question as ragAskQuestion

logger = logging.getLogger(__name__)


def chunk_text(text, chunk_size=500, overlap=50):
    """Split text into overlapping chunks."""
    if not text or len(text) < chunk_size:
        return [text] if text else []
    
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]
        chunks.append(chunk.strip())
        start = end - overlap
    
    return chunks


class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    
    def get_serializer_class(self):
        if self.action == 'list':
            return BookListSerializer
        return BookSerializer
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        delete_book_from_vector_store(instance.id)
        return super().destroy(request, *args, **kwargs)


class BookListView(APIView):
    """List all books with search and genre filtering."""
    
    def get(self, request):
        search = request.query_params.get('search', '')
        genre = request.query_params.get('genre', '')
        
        queryset = Book.objects.all()
        
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) | Q(author__icontains=search)
            )
        
        if genre:
            queryset = queryset.filter(genre__icontains=genre)
        
        serializer = BookListSerializer(queryset, many=True)
        return Response(serializer.data)


class BookDetailView(APIView):
    """Get single book details."""
    
    def get(self, request, pk):
        try:
            book = Book.objects.get(pk=pk)
            serializer = BookSerializer(book)
            return Response(serializer.data)
        except Book.DoesNotExist:
            return Response({'error': 'Book not found'}, status=404)


class BookChunksView(APIView):
    """Get chunks for a book."""
    
    def get(self, request, pk):
        try:
            book = Book.objects.get(pk=pk)
            chunks = book.chunks.all()
            from .serializers import BookChunkSerializer
            serializer = BookChunkSerializer(chunks, many=True)
            return Response(serializer.data)
        except Book.DoesNotExist:
            return Response({'error': 'Book not found'}, status=404)


class BookInsightsView(APIView):
    """Get or generate AI insights for a book."""
    
    def get(self, request, pk):
        try:
            insights = AIInsights.objects.get(book_id=pk)
            serializer = AIInsightsSerializer(insights)
            return Response(serializer.data)
        except AIInsights.DoesNotExist:
            return Response({'error': 'Insights not found'}, status=404)
    
    def post(self, request, pk):
        """Generate new insights."""
        try:
            book = Book.objects.get(pk=pk)
        except Book.DoesNotExist:
            return Response({'error': 'Book not found'}, status=404)
        
        book_text = book.description or f"{book.title} by {book.author}"
        
        # Generate insights
        summary = generate_summary(book_text)
        genre = classify_genre(book_text)
        sentiment_data = analyze_sentiment(book_text)
        
        all_books = Book.objects.all().values('title', 'author', 'genre')
        recommendations = get_recommendations(
            book.title, 
            genre, 
            list(all_books)
        )
        
        insights, created = AIInsights.objects.update_or_create(
            book=book,
            defaults={
                'summary': summary,
                'genre_prediction': genre,
                'sentiment': sentiment_data.get('label', 'Neutral'),
                'sentiment_score': sentiment_data.get('score', 0.5),
                'recommendations': recommendations
            }
        )
        
        serializer = AIInsightsSerializer(insights)
        return Response(serializer.data)


class BookRelatedView(APIView):
    """Get related books."""
    
    def get(self, request, pk):
        try:
            book = Book.objects.get(pk=pk)
        except Book.DoesNotExist:
            return Response({'error': 'Book not found'}, status=404)
        
        related = Book.objects.filter(
            Q(genre__icontains=book.genre) | Q(author__icontains=book.author)
        ).exclude(id=book.id)[:5]
        
        serializer = BookListSerializer(related, many=True)
        return Response(serializer.data)


class ScrapeBooksView(APIView):
    """
    Scrape books from web with proper source handling.
    
    POST /api/scrape/
    {
        "source": "toscrape",  # or "openlibrary", "gutenberg"
        "count": 10,
        "num_pages": 2
    }
    """
    
    def post(self, request):
        # FIXED: Source parameter now properly controls scraping
        source = request.data.get('source', 'toscrape')
        count = request.data.get('count', 10)
        num_pages = request.data.get('num_pages', 2)
        
        # Validate source
        if not is_valid_source(source):
            return Response({
                'error': f'Invalid source: {source}',
                'available_sources': get_available_sources()
            }, status=400)
        
        # Scrape using new service
        scraped_books = scrape_books(source=source, count=count, num_pages=num_pages)
        
        if not scraped_books:
            return Response({
                'error': 'No books scraped. Check if source is available.',
                'source': source
            }, status=400)
        
        created_books = []
        for book_data in scraped_books:
            book = Book.objects.create(
                title=book_data.get('title', 'Unknown'),
                author=book_data.get('author', 'Unknown'),
                description=book_data.get('description', ''),
                rating=book_data.get('rating'),
                cover_url=book_data.get('cover_url', ''),
                book_url=book_data.get('book_url', ''),
                genre=book_data.get('genre', 'Fiction')
            )
            
            # Create chunks
            text_content = f"{book.title} {book.author} {book.description}"
            chunks = chunk_text(text_content, settings.CHUNK_SIZE, settings.CHUNK_OVERLAP)
            
            for i, chunk_content in enumerate(chunks):
                BookChunk.objects.create(
                    book=book,
                    chunk_text=chunk_content,
                    chunk_index=i
                )
            
            # Add to vector store
            add_chunks_to_vector_store(book.id, chunks)
            add_chunks_to_global_store(book.id, book.title, chunks)
            created_books.append(book.id)
        
        return Response({
            'message': f'Successfully scraped {len(created_books)} books',
            'source': source,
            'book_ids': created_books
        })


class GenerateEmbeddingsView(APIView):
    """Regenerate embeddings for a book."""
    
    def post(self, request, pk):
        try:
            book = Book.objects.get(pk=pk)
        except Book.DoesNotExist:
            return Response({'error': 'Book not found'}, status=404)
        
        delete_book_from_vector_store(book.id)
        BookChunk.objects.filter(book=book).delete()
        
        text_content = f"{book.title} {book.author} {book.description}"
        chunks = chunk_text(text_content, settings.CHUNK_SIZE, settings.CHUNK_OVERLAP)
        
        for i, chunk_content in enumerate(chunks):
            BookChunk.objects.create(
                book=book,
                chunk_text=chunk_content,
                chunk_index=i
            )
        
        add_chunks_to_vector_store(book.id, chunks)
        add_chunks_to_global_store(book.id, book.title, chunks)
        
        return Response({
            'message': f'Generated {len(chunks)} embeddings',
            'chunk_count': len(chunks)
        })


class AskQuestionView(APIView):
    """
    RAG question answering endpoint.
    
    POST /api/qa/ask/
    {
        "question": "What is this book about?",
        "book_id": 1  # optional - if empty, searches all books
    }
    """
    
    def post(self, request):
        question = request.data.get('question', '')
        book_id = request.data.get('book_id')
        
        if not question:
            return Response({'error': 'Question is required'}, status=400)
        
        # Use the new RAG service for proper citations
        result = ragAskQuestion(question, book_id)
        
        return Response(result)


class QAHistoryView(APIView):
    """Get Q&A history."""
    
    def get(self, request):
        book_id = request.query_params.get('book_id')
        
        if book_id:
            qa_history = QAHistory.objects.filter(book_id=book_id)[:20]
        else:
            qa_history = QAHistory.objects.all()[:20]
        
        serializer = QAHistorySerializer(qa_history, many=True)
        return Response(serializer.data)


class SeedBooksView(APIView):
    """Seed sample books for demo."""
    
    def post(self, request):
        sample_books = [
            {
                'title': 'The Great Gatsby',
                'author': 'F. Scott Fitzgerald',
                'description': "A novel set in the Jazz Age on Long Island, near New York City. The novel depicts first-person narrator Nick Carraway's interactions with mysterious millionaire Jay Gatsby and explores themes of decadence, idealism, resistance to change, social upheaval, and excess.",
                'rating': 4.5,
                'genre': 'Fiction',
                'cover_url': 'https://covers.openlibrary.org/b/id/7222246-L.jpg',
                'book_url': 'https://www.gutenberg.org/ebooks/64317'
            },
            {
                'title': '1984',
                'author': 'George Orwell',
                'description': 'A dystopian social science fiction novel and cautionary tale, warning against totalitarianism and censorship. The novel examines the role of truth and facts within politics and the ways in which they are manipulated.',
                'rating': 4.4,
                'genre': 'Science Fiction',
                'cover_url': 'https://covers.openlibrary.org/b/id/7222336-L.jpg',
                'book_url': 'https://www.gutenberg.org/ebooks/2148'
            },
            {
                'title': 'To Kill a Mockingbird',
                'author': 'Harper Lee',
                'description': 'The novel explores the irrationality of racial attitudes in the Deep South of the 1930s. It covers adult themes to children with a humorous tone and engages with issues of racial injustice and discrimination.',
                'rating': 4.6,
                'genre': 'Fiction',
                'cover_url': 'https://covers.openlibrary.org/b/id/8228691-L.jpg',
                'book_url': 'https://www.gutenberg.org/ebooks/11193'
            },
            {
                'title': 'Pride and Prejudice',
                'author': 'Jane Austen',
                'description': 'A romantic novel that charts the emotional development of Elizabeth Bennet, who learns the difference between the superficial and the essential, and comes to appreciate the difference between the pride of wealth and vanity.',
                'rating': 4.7,
                'genre': 'Romance',
                'cover_url': 'https://covers.openlibrary.org/b/id/8231856-L.jpg',
                'book_url': 'https://www.gutenberg.org/ebooks/1342'
            },
            {
                'title': 'The Hobbit',
                'author': 'J.R.R. Tolkien',
                'description': 'A fantasy novel about the adventures of the hobbit Bilbo Baggins, who is recruited by the wizard Gandalf to help a group of dwarves reclaim their homeland from the dragon Smaug.',
                'rating': 4.8,
                'genre': 'Fantasy',
                'cover_url': 'https://covers.openlibrary.org/b/id/8406786-L.jpg',
                'book_url': 'https://www.gutenberg.org/ebooks/20022'
            },
            {
                'title': "Harry Potter and the Sorcerer's Stone",
                'author': 'J.K. Rowling',
                'description': 'The first novel in the Harry Potter series, following a young wizard as he discovers his magical heritage and begins his education at Hogwarts School of Witchcraft and Wizardry.',
                'rating': 4.9,
                'genre': 'Fantasy',
                'cover_url': 'https://covers.openlibrary.org/b/id/10521270-L.jpg',
                'book_url': 'https://www.bloomsbury.com/uk/harry-potter-and-the-philosophers-stone-9780747532693/'
            },
            {
                'title': 'The Alchemist',
                'author': 'Paulo Coelho',
                'description': 'A allegorical novel about a shepherd named Santiago who travels from Spain to Egypt in search of a treasure buried in the Pyramids. The novel explores themes of following your dreams and listening to your heart.',
                'rating': 4.4,
                'genre': 'Fiction',
                'cover_url': 'https://covers.openlibrary.org/b/id/7387966-L.jpg',
                'book_url': 'https://www.paulocoelho.com/thealchemist/'
            },
            {
                'title': '1984',
                'author': 'George Orwell',
                'description': 'A dystopian social science fiction novel set in a totalitarian society where truth is flexible and the state controls all information. The protagonist Winston Smith works at the Ministry of Truth and secretly rebels against the Party.',
                'rating': 4.5,
                'genre': 'Science Fiction',
                'cover_url': 'https://covers.openlibrary.org/b/id/7222336-L.jpg',
                'book_url': 'https://www.gutenberg.org/ebooks/2148'
            }
        ]
        
        created_books = []
        for book_data in sample_books:
            book = Book.objects.create(**book_data)
            
            text_content = f"{book.title} {book.author} {book.description}"
            chunks = chunk_text(text_content, settings.CHUNK_SIZE, settings.CHUNK_OVERLAP)
            
            for i, chunk_content in enumerate(chunks):
                BookChunk.objects.create(
                    book=book,
                    chunk_text=chunk_content,
                    chunk_index=i
                )
            
            add_chunks_to_vector_store(book.id, chunks)
            add_chunks_to_global_store(book.id, book.title, chunks)
            created_books.append(book.id)
        
        return Response({
            'message': f'Successfully created {len(created_books)} sample books',
            'book_ids': created_books
        })