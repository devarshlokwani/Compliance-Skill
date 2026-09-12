"""Retry with exponential backoff and jitter. Standard library only."""

from __future__ import annotations

import functools
import random
import time
from typing import Callable, TypeVar

T = TypeVar("T")


class RetryError(RuntimeError):
    """Raised when every attempt has been exhausted."""

    def __init__(self, attempts: int, last: BaseException) -> None:
        super().__init__(f"gave up after {attempts} attempts")
        self.attempts = attempts
        self.last = last


def retry(
    attempts: int = 3,
    base_delay: float = 0.1,
    max_delay: float = 5.0,
    jitter: bool = True,
    catching: tuple[type[BaseException], ...] = (Exception,),
) -> Callable[[Callable[..., T]], Callable[..., T]]:
    """Retry the wrapped callable, backing off exponentially between tries."""

    if attempts < 1:
        raise ValueError("attempts must be at least 1")

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> T:
            last: BaseException | None = None
            for attempt in range(attempts):
                try:
                    return func(*args, **kwargs)
                except catching as exc:
                    last = exc
                    if attempt == attempts - 1:
                        break
                    time.sleep(_backoff(attempt, base_delay, max_delay, jitter))
            raise RetryError(attempts, last)  # type: ignore[arg-type]

        return wrapper

    return decorator


def _backoff(attempt: int, base: float, ceiling: float, jitter: bool) -> float:
    delay = min(base * (2 ** attempt), ceiling)
    return delay * random.uniform(0.5, 1.0) if jitter else delay
