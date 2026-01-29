"""
Logging configuration with structured logging.

This module provides:
- Structured logging with structlog
- Request logging middleware
- Sentry integration placeholder
"""

import logging
import sys
from typing import Any, Dict

import structlog

from app.core.config import get_settings

settings = get_settings()


def configure_logging() -> None:
    """Configure structured logging for the application."""
    # Configure standard library logging
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=logging.DEBUG if settings.debug else logging.INFO,
    )
    
    # Configure structlog
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.processors.JSONRenderer() if settings.app_env == "production"
            else structlog.dev.ConsoleRenderer(),
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )


def get_logger(name: str = __name__) -> structlog.BoundLogger:
    """
    Get a structured logger.
    
    Args:
        name: Logger name.
        
    Returns:
        BoundLogger: Structured logger instance.
    """
    return structlog.get_logger(name)


def init_sentry() -> None:
    """Initialize Sentry for error tracking if configured."""
    if settings.sentry_dsn:
        try:
            import sentry_sdk
            from sentry_sdk.integrations.fastapi import FastApiIntegration
            from sentry_sdk.integrations.starlette import StarletteIntegration
            
            sentry_sdk.init(
                dsn=settings.sentry_dsn,
                environment=settings.app_env,
                integrations=[
                    StarletteIntegration(),
                    FastApiIntegration(),
                ],
                traces_sample_rate=0.1,
            )
        except ImportError:
            pass
