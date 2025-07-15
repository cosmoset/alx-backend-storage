import requests
import redis
import functools
import time

# Initialize Redis client
redis_client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)

def cache_page(func):
    """Decorator to cache page content and track URL access count."""
    @functools.wraps(func)
    def wrapper(url: str) -> str:
        # Define cache and count keys
        cache_key = f"cache:{url}"
        count_key = f"count:{url}"
        
        # Increment access count
        redis_client.incr(count_key)
        
        # Check if page is in cache
        cached_content = redis_client.get(cache_key)
        if cached_content is not None:
            return cached_content
            
        # If not in cache, get page content
        content = func(url)
        
        # Store in cache with 10-second expiration
        redis_client.setex(cache_key, 10, content)
        return content
    return wrapper

@cache_page
def get_page(url: str) -> str:
    """Fetch HTML content from a URL."""
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.text
    except requests.RequestException as e:
        return f"Error fetching {url}: {str(e)}"
