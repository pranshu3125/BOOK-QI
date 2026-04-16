"""
Text Chunking Service
==============
Handles intelligent text chunking for RAG pipeline.
Supports multiple strategies:
- Fixed-size overlapping chunks (default)
- Semantic chunking (planned)

Usage:
    from books.services.chunker import chunk_text, create_chunks
    chunks = chunk_text(text, chunk_size=500, overlap=50)
"""

import re
import logging
from typing import List, Dict, Optional
from django.conf import settings

logger = logging.getLogger(__name__)

# Default settings
DEFAULT_CHUNK_SIZE = getattr(settings, 'CHUNK_SIZE', 500)
DEFAULT_CHUNK_OVERLAP = getattr(settings, 'CHUNK_OVERLAP', 50)


def chunk_text(
    text: str,
    chunk_size: int = DEFAULT_CHUNK_SIZE,
    overlap: int = DEFAULT_CHUNK_OVERLAP
) -> List[str]:
    """
    Split text into overlapping fixed-size chunks.
    
    Args:
        text: Input text to chunk
        chunk_size: Maximum size of each chunk
        overlap: Number of overlapping characters between chunks
    
    Returns:
        List of text chunks
    
    Example:
        >>> chunks = chunk_text("Long book description...", chunk_size=500, overlap=50)
        >>> len(chunks)
        3
    """
    if not text:
        return []
    
    # If text is shorter than chunk size, return as single chunk
    if len(text) <= chunk_size:
        return [text.strip()]
    
    chunks = []
    start = 0
    text_length = len(text)
    
    while start < text_length:
        end = start + chunk_size
        
        # Try to break at a sentence boundary
        if end < text_length:
            # Look for sentence endings
            for boundary in ['. ', '! ', '? ', '\n']:
                last_boundary = text.rfind(boundary, start, end)
                if last_boundary > start:
                    end = last_boundary + 1
                    break
        
        chunk = text[start:end].strip()
        if chunk:  # Only add non-empty chunks
            chunks.append(chunk)
        
        # Move with overlap
        start = end - overlap
        if start >= text_length:
            break
    
    return chunks


def create_chunks(
    book_id: int,
    book_title: str,
    book_description: str,
    book_author: str = '',
    chunk_size: int = DEFAULT_CHUNK_SIZE,
    overlap: int = DEFAULT_CHUNK_OVERLAP
) -> List[Dict]:
    """
    Create structured chunks with metadata for a book.
    
    Args:
        book_id: Database ID of the book
        book_title: Title of the book
        book_description: Book description text
        book_author: Author name (optional)
        chunk_size: Size of each chunk
        overlap: Overlap between chunks
    
    Returns:
        List of chunk dictionaries with metadata
    
    Example:
        >>> chunks = create_chunks(1, "The Great Gatsby", "A novel about...", "F. Scott Fitzgerald")
        >>> chunks[0]
        {
            'book_id': 1,
            'book_title': 'The Great Gatsby',
            'chunk_index': 0,
            'chunk_text': 'A novel about...',
            'source': 'book_description'
        }
    """
    # Combine relevant text
    text_parts = [book_title]
    if book_author:
        text_parts.append(f"by {book_author}")
    if book_description:
        text_parts.append(book_description)
    
    combined_text = ' '.join(text_parts)
    
    # Generate chunks
    text_chunks = chunk_text(combined_text, chunk_size, overlap)
    
    # Create structured chunks with metadata
    chunks = []
    for i, chunk_text in enumerate(text_chunks):
        chunks.append({
            'book_id': book_id,
            'book_title': book_title,
            'chunk_index': i,
            'chunk_text': chunk_text,
            'source': 'book_description' if i > 0 else 'book_title',
            'char_count': len(chunk_text)
        })
    
    logger.info(f"Created {len(chunks)} chunks for book {book_id}")
    return chunks


def get_chunk_metadata(chunk: Dict) -> Dict:
    """
    Extract clean metadata from a chunk for vector storage.
    """
    return {
        'book_id': chunk.get('book_id'),
        'book_title': chunk.get('book_title'),
        'chunk_index': chunk.get('chunk_index'),
        'source': chunk.get('source'),
        'char_count': chunk.get('char_count')
    }


def merge_chunks(chunks: List[str], max_length: int = 1000) -> List[str]:
    """
    Merge small chunks into larger ones.
    Useful for creating more context-rich chunks.
    """
    if not chunks:
        return []
    
    merged = []
    current = chunks[0]
    
    for chunk in chunks[1:]:
        if len(current) + len(chunk) <= max_length:
            current += ' ' + chunk
        else:
            merged.append(current)
            current = chunk
    
    merged.append(current)
    return merged


def count_chunks(text: str, chunk_size: int = DEFAULT_CHUNK_SIZE) -> int:
    """Quick estimate of chunk count without creating them."""
    if not text or len(text) <= chunk_size:
        return 1
    return len(text) // (chunk_size - 100) + 1