from django.contrib import admin
from .models import Book, BookChunk, AIInsights, QAHistory

@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'author', 'rating', 'genre', 'created_at']
    search_fields = ['title', 'author']
    list_filter = ['genre', 'created_at']

@admin.register(BookChunk)
class BookChunkAdmin(admin.ModelAdmin):
    list_display = ['id', 'book', 'chunk_index']
    list_filter = ['book']

@admin.register(AIInsights)
class AIInsightsAdmin(admin.ModelAdmin):
    list_display = ['id', 'book', 'genre_prediction', 'sentiment']
    list_filter = ['genre_prediction']

@admin.register(QAHistory)
class QAHistoryAdmin(admin.ModelAdmin):
    list_display = ['id', 'question', 'book', 'created_at']
    list_filter = ['book', 'created_at']
    search_fields = ['question']
