"""tinyretry - retry a callable with exponential backoff."""

from .core import RetryError, retry

__all__ = ["retry", "RetryError"]
__version__ = "0.2.0"
