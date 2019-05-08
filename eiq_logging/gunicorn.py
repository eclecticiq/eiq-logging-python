"""
This is the configuration module imported by Gunicorn. It's
passed to is as ``--config python:eiq_logging.gunicorn``.
The desired effect is to remove ``gunicorn.error`` logger's stream
handler and restore propagation to the root logger, which should
follow our ``structlog`` configuration.
"""
from .helpers import configure, get_gunicorn_logconfig_dict


logconfig_dict = get_gunicorn_logconfig_dict()
configure()
