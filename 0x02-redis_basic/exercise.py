#!/usr/bin/env python3
"""
Redis config file
"""


import redis
import uuid


class Cache:
    '''
    Class for redis cache
    '''

    def __init__(self):
        '''
        Initializes the Redis client and flushes the current database.
        '''
        self._redis = redis.Redis(
            host='localhost', port=6379, decode_responses=True)
        self._redis.flushdb()

    def store(self, data: str) -> str:
        """
        Stores the given data in Redis with a generated UUID key.

        Args:
            data (str): The data to store.

        Returns:
            str: The generated UUID key under which the data is stored.
        """

        uuid_value = str(uuid.uuid4())
        self._redis.set(uuid_value, data)

        return uuid_value
