"""
Retry Logic with Exponential Backoff - Phase 4

Provides decorators and utilities for retrying failed operations with exponential backoff.
Useful for handling transient failures in API calls (Groq, Qdrant) and network operations.
"""

import time
import functools
from typing import Callable, TypeVar, Any, Type, Tuple
import logging

logger = logging.getLogger(__name__)

T = TypeVar('T')


def retry_with_exponential_backoff(
    max_retries: int = 3,
    initial_delay: float = 1.0,
    exponential_base: float = 2.0,
    jitter: bool = True,
    exceptions: Tuple[Type[Exception], ...] = (Exception,),
    on_retry: Callable[[Exception, int, float], None] = None
):
    """
    Decorator to retry a function with exponential backoff.

    This decorator will retry a function if it raises one of the specified exceptions.
    The delay between retries increases exponentially with each attempt.

    Args:
        max_retries: Maximum number of retry attempts (default: 3)
        initial_delay: Initial delay in seconds before first retry (default: 1.0)
        exponential_base: Base for exponential backoff calculation (default: 2.0)
        jitter: Add random jitter to delay to avoid thundering herd (default: True)
        exceptions: Tuple of exception types to catch and retry (default: all exceptions)
        on_retry: Optional callback function called before each retry
                  Signature: (exception, attempt_number, delay) -> None

    Returns:
        Decorated function that will retry on failure

    Example:
        >>> @retry_with_exponential_backoff(max_retries=3, initial_delay=1.0)
        ... def call_external_api():
        ...     return requests.get("https://api.example.com/data")
        ...
        >>> result = call_external_api()  # Will retry up to 3 times on failure

    Retry Delays (with exponential_base=2.0, initial_delay=1.0):
        - Attempt 1: 1.0 seconds
        - Attempt 2: 2.0 seconds
        - Attempt 3: 4.0 seconds
        - Attempt 4: 8.0 seconds (if max_retries=4)
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> T:
            last_exception = None

            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e

                    # Don't retry after last attempt
                    if attempt >= max_retries:
                        break

                    # Calculate delay with exponential backoff
                    delay = initial_delay * (exponential_base ** attempt)

                    # Add jitter to avoid thundering herd problem
                    if jitter:
                        import random
                        delay *= (0.5 + random.random())  # Random factor between 0.5 and 1.5

                    # Call retry callback if provided
                    if on_retry:
                        on_retry(e, attempt + 1, delay)
                    else:
                        logger.warning(
                            f"Retry attempt {attempt + 1}/{max_retries} for {func.__name__} "
                            f"after error: {type(e).__name__}: {str(e)}. "
                            f"Waiting {delay:.2f}s before retry..."
                        )

                    time.sleep(delay)

            # All retries exhausted, raise the last exception
            logger.error(
                f"All {max_retries} retry attempts failed for {func.__name__}. "
                f"Final error: {type(last_exception).__name__}: {str(last_exception)}"
            )
            raise last_exception

        return wrapper
    return decorator


def async_retry_with_exponential_backoff(
    max_retries: int = 3,
    initial_delay: float = 1.0,
    exponential_base: float = 2.0,
    jitter: bool = True,
    exceptions: Tuple[Type[Exception], ...] = (Exception,),
    on_retry: Callable[[Exception, int, float], None] = None
):
    """
    Async version of retry_with_exponential_backoff decorator.

    Use this for async functions (those defined with async def).

    Args:
        Same as retry_with_exponential_backoff

    Returns:
        Decorated async function that will retry on failure

    Example:
        >>> @async_retry_with_exponential_backoff(max_retries=3)
        ... async def call_external_api():
        ...     async with aiohttp.ClientSession() as session:
        ...         async with session.get("https://api.example.com/data") as resp:
        ...             return await resp.json()
        ...
        >>> result = await call_external_api()
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs) -> T:
            import asyncio
            last_exception = None

            for attempt in range(max_retries + 1):
                try:
                    return await func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e

                    # Don't retry after last attempt
                    if attempt >= max_retries:
                        break

                    # Calculate delay with exponential backoff
                    delay = initial_delay * (exponential_base ** attempt)

                    # Add jitter
                    if jitter:
                        import random
                        delay *= (0.5 + random.random())

                    # Call retry callback if provided
                    if on_retry:
                        on_retry(e, attempt + 1, delay)
                    else:
                        logger.warning(
                            f"Retry attempt {attempt + 1}/{max_retries} for {func.__name__} "
                            f"after error: {type(e).__name__}: {str(e)}. "
                            f"Waiting {delay:.2f}s before retry..."
                        )

                    await asyncio.sleep(delay)

            # All retries exhausted
            logger.error(
                f"All {max_retries} retry attempts failed for {func.__name__}. "
                f"Final error: {type(last_exception).__name__}: {str(last_exception)}"
            )
            raise last_exception

        return wrapper
    return decorator


# Convenience decorators for common use cases

def retry_on_network_error(max_retries: int = 3):
    """
    Convenience decorator for retrying on common network errors.

    Retries on: ConnectionError, TimeoutError, OSError
    """
    return retry_with_exponential_backoff(
        max_retries=max_retries,
        initial_delay=1.0,
        exceptions=(ConnectionError, TimeoutError, OSError)
    )


def retry_on_api_error(max_retries: int = 2):
    """
    Convenience decorator for retrying on API errors (rate limits, server errors).

    Uses shorter initial delay (0.5s) and fewer retries since API errors
    may be more persistent.
    """
    return retry_with_exponential_backoff(
        max_retries=max_retries,
        initial_delay=0.5,
        exponential_base=2.0
    )
