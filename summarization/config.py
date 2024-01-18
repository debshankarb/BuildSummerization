from pydantic import BaseSettings
from functools import lru_cache
import logging
import sys


class Settings(BaseSettings):
    APP_API_KEY: str

    class Config:
        env_file = ".env"

# New decorator for cache
@lru_cache()
def get_settings():
    return Settings()

# Set up basic configuration for logging

logging.basicConfig(stream=sys.stdout, level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def log_entry_exit(func):
    def wrapper(*args, **kwargs):
        print(f"Entering {func.__name__} with arguments: {args}, {kwargs}")
        result = func(*args, **kwargs)
        print(f"Exiting {func.__name__} with result: {result}")
        return result
    return wrapper
