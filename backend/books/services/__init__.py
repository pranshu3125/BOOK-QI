"""
Services Module
=============
Backend service modules for BOOK-QI Document Intelligence Platform.

Available services:
- scraper: Web scraping from multiple sources
- chunker: Text chunking for RAG
- embeddings: Embedding generation
- rag: Question answering with RAG
- insights: AI insights generation
- cache: Response caching

Usage:
    from books.services import scraper, rag, insights
    books = scraper.scrape_books(source='toscrape', count=10)
    result = rag.ask_question("What is this book about?")
"""

from .scraper import scrape_books, get_available_sources, is_valid_source
from .chunker import chunk_text, create_chunks
from .embeddings import generate_embedding, generate_embeddings
from .rag import ask_question, search_similar

__all__ = [
    'scrape_books',
    'get_available_sources', 
    'is_valid_source',
    'chunk_text',
    'create_chunks',
    'generate_embedding',
    'generate_embeddings',
    'ask_question',
    'search_similar',
]