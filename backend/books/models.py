from django.db import models
from django.utils import timezone


class Book(models.Model):
    title = models.CharField(max_length=500)
    author = models.CharField(max_length=300, blank=True)
    description = models.TextField(blank=True)
    rating = models.FloatField(null=True, blank=True)
    review_count = models.IntegerField(default=0)
    genre = models.CharField(max_length=100, blank=True)
    cover_url = models.URLField(blank=True)
    book_url = models.URLField(blank=True)
    price = models.CharField(max_length=50, blank=True)
    published_date = models.CharField(max_length=50, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title


class BookChunk(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='chunks')
    chunk_text = models.TextField()
    chunk_index = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['chunk_index']

    def __str__(self):
        return f"{self.book.title} - Chunk {self.chunk_index}"


class AIInsights(models.Model):
    book = models.OneToOneField(Book, on_delete=models.CASCADE, related_name='insights')
    summary = models.TextField(blank=True)
    genre_prediction = models.CharField(max_length=100, blank=True)
    sentiment = models.CharField(max_length=50, blank=True)
    recommendations = models.JSONField(default=list)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Insights for {self.book.title}"


class QAHistory(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE, null=True, blank=True, related_name='qa_history')
    question = models.TextField()
    answer = models.TextField()
    sources = models.JSONField(default=list)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Q: {self.question[:50]}..."
