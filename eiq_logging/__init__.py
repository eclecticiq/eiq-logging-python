"""
Standardized logging configuration for EIQ projects.
"""
import structlog

from .handlers import AtomicStreamHandler
from .helpers import configure, get_gunicorn_logconfig_dict


__all__ = [
    'get_logger',
    'AtomicStreamHandler',
    'configure',
    'get_gunicorn_logconfig_dict'
]


# if for whatever reason we switch away from structlog in the future?
get_logger = structlog.get_logger
