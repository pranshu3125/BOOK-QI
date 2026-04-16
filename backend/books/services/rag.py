"""
RAG (Retrieval-Augmented Generation) Service
========================================
Handles question answering with proper source citations.
Pipeline:
1. Generate embedding for user question
2. Retrieve relevant chunks from vector store
3. Build context from retrieved chunks
4. Call LLM for answer
5. Return answer with citations

Usage:
    from books.services.rag import ask_question, search_similar
    result = ask_question("What is this book about?", book_id=1)
"""

import logging
from typing import List, Dict, Optional, Tuple

from django.conf import settings

from .embeddings import generate_embedding
from books.vector_store import (
    get_chroma_client, 
    similarity_search, 
    global_similarity_search,
    get_or_create_collection,
    get_global_collection
)

logger = logging.getLogger(__name__)

DEFAULT_TOP_K = getattr(settings, 'RAG_TOP_K', 5)


def search_similar(
    question: str,
    book_id: Optional[int] = None,
    top_k: int = DEFAULT_TOP_K
) -> Dict:
    """
    Search for similar chunks to a question.
    
    Args:
        question: User question
        book_id: Specific book to search (optional)
        top_k: Number of results
    
    Returns:
        Dict with 'chunks', 'metadatas', 'distances'
    """
    try:
        # Generate embedding
        query_embedding = generate_embedding(question)
        if not query_embedding:
            return {'chunks': [], 'metadatas': [], 'distances': [], 'error': 'Failed to generate embedding'}
        
        if book_id:
            # Search within specific book
            results = similarity_search(book_id, question, top_k=top_k)
        else:
            # Search across all books
            results = global_similarity_search(question, top_k=top_k)
        
        if not results or not results.get('documents'):
            return {'chunks': [], 'metadatas': [], 'distances': [], 'error': None}
        
        return {
            'chunks': results.get('documents', [[]])[0],
            'metadatas': results.get('metadatas', [[]])[0],
            'distances': results.get('distances', [[]])[0] if results.get('distances') else [],
            'error': None
        }
    except Exception as e:
        logger.error(f"Search error: {e}")
        return {'chunks': [], 'metadatas': [], 'distances': [], 'error': str(e)}


def build_context(chunks: List[str], metadatas: List[Dict]) -> str:
    """
    Build context string from retrieved chunks with source citations.
    """
    if not chunks:
        return ""
    
    context_parts = []
    for i, (chunk, meta) in enumerate(zip(chunks, metadatas)):
        book_title = meta.get('book_title', 'Unknown')
        chunk_index = meta.get('chunk_index', i)
        source = meta.get('source', 'book')
        
        citation = f"[Source {i+1}: {book_title} - {source}]"
        context_parts.append(f"{citation}\n{chunk}")
    
    return "\n\n".join(context_parts)


def format_sources(chunks: List[str], metadatas: List[Dict]) -> List[Dict]:
    """
    Format sources for API response.
    """
    sources = []
    for i, (chunk, meta) in enumerate(zip(chunks, metadatas)):
        sources.append({
            'index': i + 1,
            'book_id': meta.get('book_id'),
            'book_title': meta.get('book_title', 'Unknown'),
            'chunk_index': meta.get('chunk_index', i),
            'source': meta.get('source', 'book'),
            'text': chunk[:300] + '...' if len(chunk) > 300 else chunk
        })
    return sources


def ask_question(
    question: str,
    book_id: Optional[int] = None,
    top_k: int = DEFAULT_TOP_K
) -> Dict:
    """
    Answer a question using RAG.
    
    Args:
        question: User question
        book_id: Specific book to ask about (optional)
        top_k: Number of chunks to retrieve
    
    Returns:
        Dict with 'answer', 'sources', 'question', 'chunks_used'
    
    Example:
        >>> result = ask_question("What is The Great Gatsby about?", book_id=1)
        >>> result['answer']
        'The Great Gatsby is a novel set in...'
        >>> result['sources'][0]['book_title']
        'The Great Gatsby'
    """
    if not question:
        return {
            'answer': 'Question is required',
            'sources': [],
            'question': question,
            'chunks_used': 0,
            'error': 'Empty question'
        }
    
    try:
        # Step 1 & 2: Search for similar chunks
        search_results = search_similar(question, book_id, top_k)
        
        chunks = search_results.get('chunks', [])
        metadatas = search_results.get('metadatas', [])
        
        if not chunks:
            return {
                'answer': 'No relevant information found. Try loading sample books first.',
                'sources': [],
                'question': question,
                'chunks_used': 0,
                'error': None
            }
        
        # Step 3: Build context
        context = build_context(chunks, metadatas)
        
        # Get book titles for prompt
        book_titles = list(set([m.get('book_title', 'Unknown') for m in metadatas]))
        source_name = book_titles[0] if len(book_titles) == 1 else f"{len(book_titles)} books"
        
        # Step 4: Get answer from LLM
        from books.llm_integration import rag_answer
        answer = rag_answer(question, chunks, source_name)
        
        # Step 5: Format response
        sources = format_sources(chunks, metadatas)
        
        return {
            'answer': answer,
            'sources': sources,
            'question': question,
            'chunks_used': len(chunks),
            'error': None
        }
        
    except Exception as e:
        logger.error(f"RAG error: {e}")
        return {
            'answer': f'Error processing question: {str(e)}',
            'sources': [],
            'question': question,
            'chunks_used': 0,
            'error': str(e)
        }


def get_rag_stats() -> Dict:
    """Get statistics about the RAG system."""
    try:
        client = get_chroma_client()
        
        # Check global collection
        try:
            global_col = get_global_collection()
            global_count = global_col.count()
        except:
            global_count = 0
        
        return {
            'global_chunks': global_count,
            'status': 'active'
        }
    except Exception as e:
        return {'status': 'error', 'error': str(e)}