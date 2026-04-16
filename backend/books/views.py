from rest_framework import viewsets, status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView
from django.conf import settings
from django.db.models import Q
import hashlib

from .models import Book, BookChunk, AIInsights, QAHistory
from .serializers import BookSerializer, BookListSerializer, AIInsightsSerializer, QAHistorySerializer
from .vector_store import (
    generate_embeddings, add_chunks_to_vector_store, 
    similarity_search, delete_book_from_vector_store
)
from .llm_integration import (
    generate_summary, classify_genre, analyze_sentiment, 
    get_recommendations, rag_answer
)
from .scraper import scrape_books


def chunk_text(text, chunk_size=500, overlap=50):
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
    def get(self, request, pk):
        try:
            book = Book.objects.get(pk=pk)
            serializer = BookSerializer(book)
            return Response(serializer.data)
        except Book.DoesNotExist:
            return Response({'error': 'Book not found'}, status=404)


class BookChunksView(APIView):
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
    def get(self, request, pk):
        try:
            insights = AIInsights.objects.get(book_id=pk)
            serializer = AIInsightsSerializer(insights)
            return Response(serializer.data)
        except AIInsights.DoesNotExist:
            return Response({'error': 'Insights not found'}, status=404)
    
    def post(self, request, pk):
        try:
            book = Book.objects.get(pk=pk)
        except Book.DoesNotExist:
            return Response({'error': 'Book not found'}, status=404)
        
        book_text = book.description or f"{book.title} by {book.author}"
        
        summary = generate_summary(book_text)
        genre = classify_genre(book_text)
        sentiment = analyze_sentiment(book_text)
        
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
                'sentiment': sentiment,
                'recommendations': recommendations
            }
        )
        
        serializer = AIInsightsSerializer(insights)
        return Response(serializer.data)


class BookRelatedView(APIView):
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
    def post(self, request):
        source = request.data.get('source', 'goodreads')
        count = request.data.get('count', 10)
        
        scraped_books = scrape_books(sources=[source], count=count)
        
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
            
            text_content = f"{book.title} {book.author} {book.description}"
            chunks = chunk_text(text_content, settings.CHUNK_SIZE, settings.CHUNK_OVERLAP)
            
            for i, chunk_text in enumerate(chunks):
                BookChunk.objects.create(
                    book=book,
                    chunk_text=chunk_text,
                    chunk_index=i
                )
            
            add_chunks_to_vector_store(book.id, chunks)
            created_books.append(book.id)
        
        return Response({
            'message': f'Successfully scraped and created {len(created_books)} books',
            'book_ids': created_books
        })


class GenerateEmbeddingsView(APIView):
    def post(self, request, pk):
        try:
            book = Book.objects.get(pk=pk)
        except Book.DoesNotExist:
            return Response({'error': 'Book not found'}, status=404)
        
        delete_book_from_vector_store(book.id)
        BookChunk.objects.filter(book=book).delete()
        
        text_content = f"{book.title} {book.author} {book.description}"
        chunks = chunk_text(text_content, settings.CHUNK_SIZE, settings.CHUNK_OVERLAP)
        
        for i, chunk_text in enumerate(chunks):
            BookChunk.objects.create(
                book=book,
                chunk_text=chunk_text,
                chunk_index=i
            )
        
        add_chunks_to_vector_store(book.id, chunks)
        
        return Response({
            'message': f'Generated {len(chunks)} embeddings',
            'chunk_count': len(chunks)
        })


class AskQuestionView(APIView):
    def post(self, request):
        question = request.data.get('question', '')
        book_id = request.data.get('book_id')
        
        if not question:
            return Response({'error': 'Question is required'}, status=400)
        
        if book_id:
            try:
                book = Book.objects.get(pk=book_id)
            except Book.DoesNotExist:
                return Response({'error': 'Book not found'}, status=404)
            
            results = similarity_search(book_id, question, top_k=5)
            
            context_chunks = []
            if results and results.get('documents'):
                context_chunks = results['documents'][0]
            
            answer = rag_answer(question, context_chunks, book.title)
            
            sources = []
            for i, chunk in enumerate(context_chunks):
                sources.append({
                    'index': i + 1,
                    'text': chunk[:200] + '...' if len(chunk) > 200 else chunk
                })
            
            qa = QAHistory.objects.create(
                book=book,
                question=question,
                answer=answer,
                sources=sources
            )
        else:
            answer = "Please select a book to ask questions about."
            sources = []
            qa = QAHistory.objects.create(
                question=question,
                answer=answer,
                sources=sources
            )
        
        return Response({
            'question': question,
            'answer': answer,
            'sources': sources,
            'qa_id': qa.id
        })


class QAHistoryView(APIView):
    def get(self, request):
        book_id = request.query_params.get('book_id')
        
        if book_id:
            qa_history = QAHistory.objects.filter(book_id=book_id)[:20]
        else:
            qa_history = QAHistory.objects.all()[:20]
        
        serializer = QAHistorySerializer(qa_history, many=True)
        return Response(serializer.data)


class SeedBooksView(APIView):
    def post(self, request):
        sample_books = [
            {
                'title': 'The Great Gatsby',
                'author': 'F. Scott Fitzgerald',
                'description': 'A novel set in the Jazz Age on Long Island, near New York City. The novel depicts first-person narrator Nick Carraway\'s interactions with mysterious millionaire Jay Gatsby and explores themes of decadence, idealism, resistance to change, social upheaval, and excess.',
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
                'title': 'The Catcher in the Rye',
                'author': 'J.D. Salinger',
                'description': 'A story about a teenage boy named Holden Caulfield who has been expelled from prep school and wanders around New York City for three days, dealing with themes of teenage angst, alienation, and identity.',
                'rating': 4.3,
                'genre': 'Fiction',
                'cover_url': 'https://covers.openlibrary.org/b/id/8231637-L.jpg',
                'book_url': 'https://www.gutenberg.org/ebooks/8232'
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
                'title': 'Harry Potter and the Sorcerer\'s Stone',
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
            }
        ]
        
        created_books = []
        for book_data in sample_books:
            book = Book.objects.create(**book_data)
            
            text_content = f"{book.title} {book.author} {book.description}"
            chunks = chunk_text(text_content, settings.CHUNK_SIZE, settings.CHUNK_OVERLAP)
            
            for i, chunk_text in enumerate(chunks):
                BookChunk.objects.create(
                    book=book,
                    chunk_text=chunk_text,
                    chunk_index=i
                )
            
            add_chunks_to_vector_store(book.id, chunks)
            created_books.append(book.id)
        
        return Response({
            'message': f'Successfully created {len(created_books)} sample books',
            'book_ids': created_books
        })
