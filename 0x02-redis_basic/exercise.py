#!/usr/bin/env python3
""" Module for Redis db """
import redis
from uuid import uuid4
from typing import Union, Callable, Optional
from functools import wraps


UnionOfTypes = Union[str, bytes, int, float]

def count_calls(method: Callable) -> Callable:
    """
    Decorator that counts the number of times a method is called.
    
    Args:
        method (Callable): The method to be decorated.
    
    Returns:
        Callable: The decorated method.
    """
    @wraps(method)
    def wrapper(self, *args, **kwargs):
        """
        Wrapper function that increments the count in Redis for the
        qualified name of the method being called.
        """
        # Access Redis instance via `self`
        key = method.__qualname__
        
        # Increment the counter in Redis
        self._redis.incr(key)
        
        # Call the original method
        return method(self, *args, **kwargs)
    
    return wrapper

def call_history(method: Callable) -> Callable:
    """
    Decorator that stores the history of inputs and outputs of a method.
    
    Args:
        method (Callable): The method to be decorated.
    
    Returns:
        Callable: The decorated method.
    """
    @wraps(method)
    def wrapper(self, *args, **kwargs):
        """
        Wrapper function that stores inputs and outputs in Redis.
        """
        # Construct input and output keys
        input_key = f"{method.__qualname__}:inputs"
        output_key = f"{method.__qualname__}:outputs"
        
        # Convert args to a string for storage
        self._redis.rpush(input_key, str(args))
        
        # Call the original method and capture the output
        result = method(self, *args, **kwargs)
        
        # Store the output in Redis
        self._redis.rpush(output_key, str(result))
        
        return result

    return wrapper

class Cache:
    """ Class for methods that operate a caching system """

    def __init__(self):
        """ Instance of the Redis db """
        self._redis = redis.Redis()
        self._redis.flushdb()

    def store(self, data: UnionOfTypes) -> str:
        """
        Method takes a data argument and returns a string
        """
        self._key = str(uuid4())
        self._redis.set(self._key, data)
        return self._key

    def get(self, key: str,
            fn: Optional[Callable] = None) -> UnionOfTypes:
        """
        Retrieves data stored in redis using a key
        converts the result/value back to the desired format
        """
        value = self._redis.get(key)
        return fn(value) if fn else value

    def get_str(self, value: str) -> str:
        """ get a string """
        return self.get(self._key, str)

    def get_int(self, value: str) -> int:
        """ get an int """
        return self.get(self._key, int)
