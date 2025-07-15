#!/bin/bash/env python3
"""
Caching a request
"""

import requests
import redis


def get_page(url: str) -> str:
    """
    Fetch HTML content of the given URL with caching
    """
    _redis = redis.Redis(
        host='localhost', port=6379, decode_responses=True)

    _redis.incr(f"count:{url}")

    cached = _redis.get(url)
    if cached:
        return cached

    response = requests.get(url)
    html = response.text

    _redis.setex(url, 10, html)
    return html
