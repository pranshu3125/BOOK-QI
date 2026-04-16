"""
AI Insights Service
================
Generates AI-based insights for books:
- Summary
- Genre Classification
- Sentiment Analysis
- Recommendations

Usage:
    from books.services.insights import generate_all_insights
    insights = generate_all_insights(book_id, book.title, book.description)
"""

import logging
from typing import Dict, Optional, List

from django.conf import settings
from books.llm_integration import (
    generate_summary,
    classify_genre,
    analyze_sentiment,
    get_recommendations
)
from books.models import Book, AIInsights
from .cache import get_cached_response, cache_response

logger = logging.getLogger(__name__)

# Settings
LLM_PROVIDER = getattr(settings, 'LLM_PROVIDER', 'lmstudio')
LLM_MODEL = getattr(settings, 'LLM_MODEL', 'local-model')


def generate_summary_insight(text: str, book_id: int = None) -> str:
    """Generate a summary for book text."""
    if not text:
        return "No description available"
    
    cache_key = f"summary_{book_id or hash(text)}"
    
    # Check cache
    cached = get_cached_response(text[:500], LLM_PROVIDER, LLM_MODEL)
    if cached:
        return cached
    
    # Generate summary
    summary = generate_summary(text)
    
    # Cache it
    cache_response(text[:500], summary, LLM_PROVIDER, LLM_MODEL)
    
    return summary


def generate_genre_insight(text: str, book_id: int = None) -> str:
    """Classify the genre of a book."""
    if not text:
        return "Unknown"
    
    genre = classify_genre(text)
    return genre


def generate_sentiment_insight(text: str, book_id: int = None) -> Dict:
    """Analyze sentiment of book description."""
    if not text:
        return {'label': 'Neutral', 'score': 0.5}
    
    sentiment = analyze_sentiment(text)
    return sentiment


def generate_recommendations_insight(book_title: str, book_genre: str, all_books: List[Dict]) -> List[str]:
    """Generate book recommendations."""
    if not book_title or not all_books:
        return []
    
    recommendations = get_recommendations(book_title, book_genre, all_books)
    return recommendations


def generate_all_insights(
    book: Book,
    force_regenerate: bool = False
) -> Dict:
    """
    Generate all AI insights for a book.
    
    Args:
        book: Book model instance
        force_regenerate: Force regeneration even if insights exist
    
    Returns:
        Dict with insights data
    """
    # Check existing insights
    if not force_regenerate:
        try:
            existing = AIInsights.objects.get(book=book)
            if existing.summary:
                return {
                    'summary': existing.summary,
                    'genre_prediction': existing.genre_prediction,
                    'sentiment': existing.sentiment,
                    'sentiment_score': existing.sentiment_score,
                    'recommendations': existing.recommendations,
                    'cached': True
                }
        except AIInsights.DoesNotExist:
            pass
    
    # Get book text
    book_text = book.description or f"{book.title} by {book.author}"
    
    # Generate insights
    summary = generate_summary_insight(book_text, book.id)
    genre = generate_genre_insight(book_text, book.id)
    sentiment = generate_sentiment_insight(book_text, book.id)
    
    # Get recommendations
    all_books = list(Book.objects.exclude(id=book.id).values('title', 'author', 'genre'))
    recommendations = generate_recommendations_insight(book.title, genre, all_books)
    
    # Save to database
    insights, created = AIInsights.objects.update_or_create(
        book=book,
        defaults={
            'summary': summary,
            'genre_prediction': genre,
            'sentiment': sentiment.get('label', 'Neutral'),
            'sentiment_score': sentiment.get('score', 0.5),
            'recommendations': recommendations
        }
    )
    
    return {
        'summary': summary,
        'genre_prediction': genre,
        'sentiment': sentiment.get('label', 'Neutral'),
        'sentiment_score': sentiment.get('score', 0.5),
        'recommendations': recommendations,
        'cached': False
    }


def get_insights_for_book(book_id: int) -> Optional[Dict]:
    """Get existing insights for a book."""
    try:
        insights = AIInsights.objects.get(book_id=book_id)
        return {
            'summary': insights.summary,
            'genre_prediction': insights.genre_prediction,
            'sentiment': insights.sentiment,
            'sentiment_score': insights.sentiment_score,
            'recommendations': insights.recommendations,
            'created_at': insights.created_at,
            'updated_at': insights.updated_at
        }
    except AIInsights.DoesNotExist:
        return None