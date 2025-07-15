#!/usr/bin/env python3
"""
Redis config file
"""


import redis
import uuid
from typing import Union, Optional, Callable
from functools import wraps


def count_calls(method: Callable) -> Callable:
    '''
    Decorator that counts how many times a method is called
    '''
    @wraps(method)
    def wrapper(self, *args, **kwargs):
        '''Wrapper that increments the count and calls'''
        key = method.__qualname__
        self._redis.incr(key)

        return method(self, *args, **kwargs)

    return wrapper


def call_history(method: Callable) -> Callable:
    """
    Decorator that stores the history of inputs and outputs for a function.
    """
    @wraps(method)
    def wrapper(self, *args, **kwargs):
        key = method.__qualname__
        input_key = f"{key}:inputs"
        output_key = f"{key}:outputs"

        self._redis.rpush(input_key, str(args))

        result = method(self, *args, **kwargs)
        self._redis.rpush(output_key, result)

        return result
    return wrapper


def replay(method: Callable):
    """
    Display the history of calls of a particular function.
    """
    r = method.__self__._redis
    key = method.__qualname__

    inputs = r.lrange(f"{key}:inputs", 0, -1)
    outputs = r.lrange(f"{key}:outputs", 0, -1)

    print(f"{key} was called {len(inputs)} times:")
    for inp, out in zip(inputs, outputs):
        print(f"{key}(*{inp.decode('utf-8')}) -> {out.decode('utf-8')}")


class Cache:
    '''
    Class for redis cache
    '''

    def __init__(self):
        '''
        Initializes the Redis client and flushes the current database.
        '''
        self._redis = redis.Redis(
            host='localhost', port=6379, decode_responses=False)
        self._redis.flushdb()

    @call_history
    @count_calls
    def store(self, data: Union[str | int | float | bytes]) -> str:
        """
        Stores the given data in Redis with a generated UUID key.

        Args:
            data (str | bytes | int | float): The data to store.

        Returns:
            str: The generated UUID key under which the data is stored.
        """

        uuid_value = str(uuid.uuid4())
        self._redis.set(uuid_value, data)

        return uuid_value

    def get(
            self, key: str, fn: Optional[Callable] = None
    ) -> Optional[Union[str, int, bytes]]:
        """
        Retrieve data from redis
        """
        data = self._redis.get(key)
        if data is None:
            return None
        return fn(data) if fn else data

    def get_str(self, key: str) -> str:
        """
        Retrieves string data from redis
        """
        return self.get(key, fn=lambda d: d.decode("utf-8"))

    def get_int(self, key: str) -> str:
        """
        Retrieves int from redis
        """
        return self.get(key, fn=int)
