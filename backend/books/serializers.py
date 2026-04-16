from rest_framework import serializers
from .models import Book, BookChunk, AIInsights, QAHistory


class BookChunkSerializer(serializers.ModelSerializer):
    class Meta:
        model = BookChunk
        fields = ['id', 'chunk_text', 'chunk_index']


class BookSerializer(serializers.ModelSerializer):
    chunks = BookChunkSerializer(many=True, read_only=True)
    
    class Meta:
        model = Book
        fields = [
            'id', 'title', 'author', 'description', 'rating', 
            'review_count', 'genre', 'cover_url', 'book_url',
            'price', 'published_date', 'created_at', 'updated_at', 'chunks'
        ]


class BookListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = [
            'id', 'title', 'author', 'description', 'rating', 
            'review_count', 'genre', 'cover_url', 'book_url', 'price'
        ]


class AIInsightsSerializer(serializers.ModelSerializer):
    class Meta:
        model = AIInsights
        fields = ['id', 'summary', 'genre_prediction', 'sentiment', 'sentiment_score', 'recommendations', 'created_at', 'updated_at']


class QAHistorySerializer(serializers.ModelSerializer):
    book_title = serializers.CharField(source='book.title', read_only=True)
    
    class Meta:
        model = QAHistory
        fields = ['id', 'book', 'book_title', 'question', 'answer', 'sources', 'created_at']
