#!/usr/bin/env python3
"""
Web caching and tracking module using Redis.
"""
import requests
import redis
from typing import Callable
from functools import wraps


def cache_page(method: Callable) -> Callable:
    """
    Decorator to cache web page content and track access counts.

    Args:
        method (Callable): The method to be decorated.

    Returns:
        Callable: Wrapped function that caches content and tracks URL access.
    """
    @wraps(method)
    def wrapper(url: str) -> str:
        redis_client = redis.Redis(decode_responses=True)
        count_key = f"count:{url}"
        cache_key = f"cache:{url}"
        
        # Increment access count
        redis_client.incr(count_key)
        
        # Check cache
        cached_content = redis_client.get(cache_key)
        if cached_content is not None:
            return cached_content
        
        # Fetch and cache content
        content = method(url)
        redis_client.setex(cache_key, 10, content)
        return content
    return wrapper


@cache_page
def get_page(url: str) -> str:
    """
    Fetch HTML content from a URL and cache it with a 10-second expiration.

    Args:
        url (str): The URL to fetch content from.

    Returns:
        str: The HTML content of the URL or an error message if the request fails.
    """
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.text
    except requests.RequestException as e:
        return f"Error fetching {url}: {str(e)}"
