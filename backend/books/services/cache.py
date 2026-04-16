"""
Caching Service
============
Provides intelligent caching for AI responses.
Includes provider and model in cache key to avoid conflicts.

Usage:
    from books.services.cache import get_cached_response, cache_response
    cached = get_cached_response("prompt_key", provider="claude", model="haiku")
"""

import hashlib
import json
import logging
from typing import Optional, Any

from django.conf import settings
from django.core.cache import cache as django_cache

logger = logging.getLogger(__name__)

# Get settings
CACHE_ENABLED = getattr(settings, 'CACHE_ENABLED', True)
CACHE_TTL = getattr(settings, 'CACHE_TTL', 86400)  # 24 hours
LLM_PROVIDER = getattr(settings, 'LLM_PROVIDER', 'lmstudio')
LLM_MODEL = getattr(settings, 'LLM_MODEL', 'local-model')


def make_cache_key(prompt: str, provider: str = None, model: str = None, prefix: str = 'llm') -> str:
    """
    Create a cache key that includes provider and model.
    
    Args:
        prompt: The prompt text
        provider: LLM provider (claude, openai, lmstudio)
        model: Model name
        prefix: Cache key prefix
    
    Returns:
        Cache key string
    """
    provider = provider or LLM_PROVIDER
    model = model or LLM_MODEL
    
    # Create hash of prompt
    prompt_hash = hashlib.md5(prompt.encode()).hexdigest()[:16]
    
    # Include provider and model in key
    return f"{prefix}_{provider}_{model}_{prompt_hash}"


def get_cached_response(
    prompt: str,
    provider: str = None,
    model: str = None
) -> Optional[str]:
    """
    Get a cached AI response if available.
    
    Args:
        prompt: The prompt that was used
        provider: LLM provider
        model: Model name
    
    Returns:
        Cached response or None
    """
    if not CACHE_ENABLED:
        return None
    
    try:
        cache_key = make_cache_key(prompt, provider, model)
        return django_cache.get(cache_key)
    except Exception as e:
        logger.warning(f"Cache read error: {e}")
        return None


def cache_response(
    prompt: str,
    response: str,
    provider: str = None,
    model: str = None,
    ttl: int = None
) -> bool:
    """
    Cache an AI response.
    
    Args:
        prompt: The prompt used
        response: The response to cache
        provider: LLM provider
        model: Model name
        ttl: Time to live in seconds
    
    Returns:
        True if successful
    """
    if not CACHE_ENABLED:
        return False
    
    if not response or response.startswith('Error'):
        return False
    
    try:
        cache_key = make_cache_key(prompt, provider, model)
        time_to_live = ttl or CACHE_TTL
        django_cache.set(cache_key, response, time_to_live)
        return True
    except Exception as e:
        logger.warning(f"Cache write error: {e}")
        return False


def invalidate_cache(pattern: str = 'llm_*') -> int:
    """
    Invalidate cache entries matching a pattern.
    Note: Django file-based cache doesn't support pattern deletion well.
    This is a placeholder for future implementation.
    """
    logger.info(f"Cache invalidation requested for pattern: {pattern}")
    return 0


def clear_all_cache() -> bool:
    """
    Attempt to clear all Django cache.
    """
    try:
        django_cache.clear()
        logger.info("Cache cleared")
        return True
    except Exception as e:
        logger.error(f"Failed to clear cache: {e}")
        return False


def get_cache_stats() -> dict:
    """Get cache statistics."""
    return {
        'enabled': CACHE_ENABLED,
        'ttl_seconds': CACHE_TTL,
        'provider': LLM_PROVIDER,
        'model': LLM_MODEL
    }