"""
This is the configuration module imported by Gunicorn. It's
passed to is as ``--config python:eiq_logging.gunicorn``.
The desired effect is to remove ``gunicorn.error`` logger's stream
handler and restore propagation to the root logger, which should
follow our ``structlog`` configuration.
"""

import eiq_logging


logconfig_dict = {
    "version": 1,
    "disable_existing_loggers": False,
    "loggers": {"gunicorn.error": {"level": "NOTSET", "propagate": True}},
}
eiq_logging.configure()
