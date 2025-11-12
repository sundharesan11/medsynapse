"""
Structured logging and performance tracking for the multi-agent system.

Provides:
- JSON-formatted logs for production monitoring
- Performance metrics tracking (duration, tokens, costs)
- Retry logic with exponential backoff
- Centralized metrics collection
"""

import logging
import json
import time
import functools
from datetime import datetime
from typing import Dict, List, Any, Optional
from collections import defaultdict


class StructuredFormatter(logging.Formatter):
    """
    JSON formatter for structured logging.

    Output format:
    {
        "timestamp": "2024-01-15T10:30:45.123Z",
        "level": "INFO",
        "logger": "agents.intake",
        "message": "Processing patient intake",
        "patient_id": "P001",
        "agent": "intake",
        "duration_ms": 1234,
        "tokens": 450,
        "cost_usd": 0.0023,
        "status": "success"
    }
    """

    def format(self, record: logging.LogRecord) -> str:
        log_data = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

        # Add extra fields if present
        if hasattr(record, 'patient_id'):
            log_data['patient_id'] = record.patient_id
        if hasattr(record, 'agent'):
            log_data['agent'] = record.agent
        if hasattr(record, 'duration_ms'):
            log_data['duration_ms'] = record.duration_ms
        if hasattr(record, 'tokens'):
            log_data['tokens'] = record.tokens
        if hasattr(record, 'cost_usd'):
            log_data['cost_usd'] = record.cost_usd
        if hasattr(record, 'status'):
            log_data['status'] = record.status
        if hasattr(record, 'error_type'):
            log_data['error_type'] = record.error_type
        if hasattr(record, 'similar_cases_found'):
            log_data['similar_cases_found'] = record.similar_cases_found
        if hasattr(record, 'search_query'):
            log_data['search_query'] = record.search_query

        return json.dumps(log_data)


def setup_logging(log_level: str = "INFO") -> logging.Logger:
    """
    Configure dual logging: human-readable console + structured JSON file.

    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR)

    Returns:
        Configured logger instance
    """
    # Create logger
    logger = logging.getLogger("medsynapse")
    logger.setLevel(getattr(logging, log_level.upper()))

    # Remove existing handlers to avoid duplicates
    logger.handlers.clear()

    # Console handler - human readable
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_format = logging.Formatter(
        '[%(levelname)s] %(name)s - %(message)s'
    )
    console_handler.setFormatter(console_format)
    logger.addHandler(console_handler)

    # File handler - structured JSON
    try:
        file_handler = logging.FileHandler('logs/medsynapse.log')
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(StructuredFormatter())
        logger.addHandler(file_handler)
    except FileNotFoundError:
        # Create logs directory if it doesn't exist
        import os
        os.makedirs('logs', exist_ok=True)
        file_handler = logging.FileHandler('logs/medsynapse.log')
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(StructuredFormatter())
        logger.addHandler(file_handler)

    return logger


def track_performance(agent_name: str):
    """
    Decorator to track agent performance metrics.

    Automatically logs:
    - Start/end of agent execution
    - Duration in milliseconds
    - Success/failure status
    - Error details if failed

    Usage:
        @track_performance("intake")
        def intake_agent(state: GraphState) -> GraphState:
            ...
    """
    def decorator(func):
        @functools.wraps(func)
        async def async_wrapper(state, *args, **kwargs):
            logger = logging.getLogger(f"medsynapse.agents.{agent_name}")

            patient_id = getattr(state.patient_intake, 'patient_id', 'unknown') if hasattr(state, 'patient_intake') and state.patient_intake else 'unknown'

            # Log start
            logger.info(
                f"Starting {agent_name} agent",
                extra={
                    'agent': agent_name,
                    'patient_id': patient_id,
                    'status': 'started'
                }
            )

            start_time = time.time()

            try:
                # Execute agent
                result = await func(state, *args, **kwargs)

                # Calculate duration
                duration_ms = int((time.time() - start_time) * 1000)

                # Log success
                logger.info(
                    f"Completed {agent_name} agent",
                    extra={
                        'agent': agent_name,
                        'patient_id': patient_id,
                        'duration_ms': duration_ms,
                        'status': 'success'
                    }
                )

                # Update metrics
                MetricsCollector.record_agent_execution(agent_name, duration_ms, True)

                return result

            except Exception as e:
                # Calculate duration
                duration_ms = int((time.time() - start_time) * 1000)

                # Log error
                logger.error(
                    f"Failed {agent_name} agent: {str(e)}",
                    extra={
                        'agent': agent_name,
                        'patient_id': patient_id,
                        'duration_ms': duration_ms,
                        'status': 'failed',
                        'error_type': type(e).__name__
                    }
                )

                # Update metrics
                MetricsCollector.record_agent_execution(agent_name, duration_ms, False)
                MetricsCollector.record_error(agent_name, type(e).__name__, str(e))

                raise

        @functools.wraps(func)
        def sync_wrapper(state, *args, **kwargs):
            logger = logging.getLogger(f"medsynapse.agents.{agent_name}")

            patient_id = getattr(state.patient_intake, 'patient_id', 'unknown') if hasattr(state, 'patient_intake') and state.patient_intake else 'unknown'

            # Log start
            logger.info(
                f"Starting {agent_name} agent",
                extra={
                    'agent': agent_name,
                    'patient_id': patient_id,
                    'status': 'started'
                }
            )

            start_time = time.time()

            try:
                # Execute agent
                result = func(state, *args, **kwargs)

                # Calculate duration
                duration_ms = int((time.time() - start_time) * 1000)

                # Log success
                logger.info(
                    f"Completed {agent_name} agent",
                    extra={
                        'agent': agent_name,
                        'patient_id': patient_id,
                        'duration_ms': duration_ms,
                        'status': 'success'
                    }
                )

                # Update metrics
                MetricsCollector.record_agent_execution(agent_name, duration_ms, True)

                return result

            except Exception as e:
                # Calculate duration
                duration_ms = int((time.time() - start_time) * 1000)

                # Log error
                logger.error(
                    f"Failed {agent_name} agent: {str(e)}",
                    extra={
                        'agent': agent_name,
                        'patient_id': patient_id,
                        'duration_ms': duration_ms,
                        'status': 'failed',
                        'error_type': type(e).__name__
                    }
                )

                # Update metrics
                MetricsCollector.record_agent_execution(agent_name, duration_ms, False)
                MetricsCollector.record_error(agent_name, type(e).__name__, str(e))

                raise

        # Return appropriate wrapper based on function type
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper

    return decorator


class MetricsCollector:
    """
    Centralized metrics collection for monitoring and dashboards.

    Tracks:
    - Agent execution durations
    - Token usage and costs
    - Error rates and types
    - Case completion statistics
    """

    # Class-level storage (in production, use Redis or database)
    _agent_durations: Dict[str, List[float]] = defaultdict(list)
    _agent_successes: Dict[str, int] = defaultdict(int)
    _agent_failures: Dict[str, int] = defaultdict(int)
    _errors: List[Dict[str, Any]] = []
    _total_tokens: int = 0
    _total_cost: float = 0.0
    _cases_completed: int = 0
    _cases_failed: int = 0

    @classmethod
    def record_agent_execution(cls, agent_name: str, duration_ms: int, success: bool):
        """Record agent execution metrics."""
        cls._agent_durations[agent_name].append(duration_ms)
        if success:
            cls._agent_successes[agent_name] += 1
        else:
            cls._agent_failures[agent_name] += 1

    @classmethod
    def record_error(cls, agent_name: str, error_type: str, error_message: str):
        """Record error details."""
        cls._errors.append({
            'timestamp': datetime.utcnow().isoformat() + "Z",
            'agent': agent_name,
            'error_type': error_type,
            'message': error_message
        })

    @classmethod
    def record_tokens(cls, tokens: int, cost: float):
        """Record token usage and cost."""
        cls._total_tokens += tokens
        cls._total_cost += cost

    @classmethod
    def record_case_completion(cls, success: bool):
        """Record case completion status."""
        if success:
            cls._cases_completed += 1
        else:
            cls._cases_failed += 1

    @classmethod
    def get_summary(cls) -> Dict[str, Any]:
        """
        Get aggregated metrics summary for dashboard.

        Returns:
            Dictionary with performance metrics:
            - Agent performance (avg duration, success rate)
            - Token usage and costs
            - Error statistics
            - Case completion rates
        """
        agent_stats = {}
        for agent_name in cls._agent_durations.keys():
            durations = cls._agent_durations[agent_name]
            successes = cls._agent_successes[agent_name]
            failures = cls._agent_failures[agent_name]
            total_calls = successes + failures

            agent_stats[agent_name] = {
                'avg_duration_ms': int(sum(durations) / len(durations)) if durations else 0,
                'min_duration_ms': int(min(durations)) if durations else 0,
                'max_duration_ms': int(max(durations)) if durations else 0,
                'total_calls': total_calls,
                'success_rate': round(successes / total_calls * 100, 2) if total_calls > 0 else 0,
                'failures': failures
            }

        return {
            'agent_performance': agent_stats,
            'token_usage': {
                'total_tokens': cls._total_tokens,
                'total_cost_usd': round(cls._total_cost, 4)
            },
            'case_statistics': {
                'completed': cls._cases_completed,
                'failed': cls._cases_failed,
                'success_rate': round(
                    cls._cases_completed / (cls._cases_completed + cls._cases_failed) * 100, 2
                ) if (cls._cases_completed + cls._cases_failed) > 0 else 0
            },
            'recent_errors': cls._errors[-10:],  # Last 10 errors
            'total_errors': len(cls._errors)
        }

    @classmethod
    def reset(cls):
        """Reset all metrics (useful for testing)."""
        cls._agent_durations.clear()
        cls._agent_successes.clear()
        cls._agent_failures.clear()
        cls._errors.clear()
        cls._total_tokens = 0
        cls._total_cost = 0.0
        cls._cases_completed = 0
        cls._cases_failed = 0


def retry_with_backoff(max_attempts: int = 3, initial_delay: float = 1.0):
    """
    Decorator for retry logic with exponential backoff.

    Retries failed operations with increasing delays:
    - Attempt 1: immediate
    - Attempt 2: wait 1 second
    - Attempt 3: wait 2 seconds
    - Attempt 4: wait 4 seconds

    Args:
        max_attempts: Maximum number of retry attempts
        initial_delay: Initial delay in seconds (doubles each retry)

    Usage:
        @retry_with_backoff(max_attempts=3)
        async def search_similar_cases(...):
            ...
    """
    def decorator(func):
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            logger = logging.getLogger("medsynapse.retry")

            for attempt in range(max_attempts):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_attempts - 1:
                        # Last attempt failed, raise the error
                        logger.error(f"All {max_attempts} attempts failed for {func.__name__}: {str(e)}")
                        raise

                    # Calculate delay with exponential backoff
                    delay = initial_delay * (2 ** attempt)
                    logger.warning(
                        f"Attempt {attempt + 1}/{max_attempts} failed for {func.__name__}: {str(e)}. "
                        f"Retrying in {delay}s..."
                    )

                    await asyncio.sleep(delay)

        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            logger = logging.getLogger("medsynapse.retry")

            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_attempts - 1:
                        # Last attempt failed, raise the error
                        logger.error(f"All {max_attempts} attempts failed for {func.__name__}: {str(e)}")
                        raise

                    # Calculate delay with exponential backoff
                    delay = initial_delay * (2 ** attempt)
                    logger.warning(
                        f"Attempt {attempt + 1}/{max_attempts} failed for {func.__name__}: {str(e)}. "
                        f"Retrying in {delay}s..."
                    )

                    time.sleep(delay)

        # Return appropriate wrapper
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper

    return decorator


# Missing import for asyncio
import asyncio

# Initialize logger on module import
logger = setup_logging()
