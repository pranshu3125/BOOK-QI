"""
Embedding Generation Service
====================
Handles text embeddings generation using sentence transformers.
Supports:
- Single text embedding
- Batch embedding generation
- Caching

Usage:
    from books.services.embeddings import generate_embedding, generate_embeddings
    emb = generate_embedding("What is this book about?")
"""

import os
import logging
from typing import List, Optional
import numpy as np

from django.conf import settings

logger = logging.getLogger(__name__)

# Singleton embedding model
_embedding_model = None


def get_embedding_model():
    """
    Get or create the sentence transformer model.
    Uses singleton pattern to avoid reloading.
    """
    global _embedding_model
    
    if _embedding_model is None:
        try:
            from sentence_transformers import SentenceTransformer
            model_name = getattr(settings, 'EMBEDDING_MODEL', 'sentence-transformers/all-MiniLM-L6-v2')
            _embedding_model = SentenceTransformer(model_name)
            logger.info(f"Loaded embedding model: {model_name}")
        except Exception as e:
            logger.error(f"Failed to load embedding model: {e}")
            raise
    
    return _embedding_model


def generate_embedding(text: str) -> List[float]:
    """
    Generate embedding for a single text.
    
    Args:
        text: Input text
    
    Returns:
        Embedding as list of floats
    
    Example:
        >>> emb = generate_embedding("What is The Great Gatsby about?")
        >>> len(emb)
        384
    """
    if not text:
        return []
    
    try:
        model = get_embedding_model()
        embedding = model.encode([text])[0]
        return embedding.tolist()
    except Exception as e:
        logger.error(f"Embedding generation failed: {e}")
        return []


def generate_embeddings(texts: List[str], show_progress: bool = False) -> List[List[float]]:
    """
    Generate embeddings for multiple texts.
    
    Args:
        texts: List of input texts
        show_progress: Whether to show progress bar
    
    Returns:
        List of embeddings
    """
    if not texts:
        return []
    
    try:
        model = get_embedding_model()
        embeddings = model.encode(texts, show_progress_bar=show_progress)
        return embeddings.tolist()
    except Exception as e:
        logger.error(f"Batch embedding failed: {e}")
        return []


def get_embedding_dimension() -> int:
    """Get the dimension of the embedding vector."""
    try:
        model = get_embedding_model()
        return model.get_sentence_embedding_dimension()
    except:
        return 384  # Default for all-MiniLM-L6-v2


def get_model_info() -> dict:
    """Get information about the loaded model."""
    try:
        model = get_embedding_model()
        return {
            'model_name': getattr(settings, 'EMBEDDING_MODEL', 'sentence-transformers/all-MiniLM-L6-v2'),
            'dimension': get_embedding_dimension(),
            'max_seq_length': model.max_seq_length
        }
    except Exception as e:
        return {'error': str(e)}


def clear_embedding_cache():
    """Clear the embedding model from memory."""
    global _embedding_model
    _embedding_model = None
    logger.info("Cleared embedding model cache")


def preload_model():
    """Preload model on startup if needed."""
    try:
        get_embedding_model()
        logger.info("Embedding model preloaded successfully")
    except Exception as e:
        logger.warning(f"Could not preload embedding model: {e}")