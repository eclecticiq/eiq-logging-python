import os
import logging
import sys

import structlog

from .constants import DEFAULT_FORMAT, DEFAULT_LEVELS, DELIMITER, ENV_PREFIX
from .handlers import AtomicStreamHandler
from .renderers import render_plaintext, render_json


def parse_str(var):
    """
    Parse a string (from an environment variable, for example), turning it into
    a dictionary of {logger_name: log_level}.
    """
    loggers = {}
    parts = var.split(DELIMITER)
    for part in parts:
        if ":" in part:
            logger, _, level = part.partition(":")
        else:
            logger = ""
            level = part

        if logger == "root":
            logger = ""

        loggers[logger] = level
    return loggers


def sort_loggers(loggers_dict):
    """
    Sort a dictionary of {logger_name: log_level} in the order in which they
    should be configured (least specific first, most specific last).
    """
    root_level = loggers_dict.pop("", None)
    if root_level is not None:
        yield "", root_level
    yield from sorted(loggers_dict.items(), key=lambda i: i[0].split("."))


def get_loggers_dict(levels):
    """
    Given a user input of log levels (string or dict), construct a complete
    dict of {logger_name: log_level}.
    """
    loggers_dict = DEFAULT_LEVELS.copy()
    if levels:
        if isinstance(levels, str):
            levels = parse_str(levels)
        # if the user is setting the root logger level, let that override
        # the default config entirely rather than appending to it
        if "" in levels:
            loggers_dict = levels
        else:
            loggers_dict.update(levels)
    return loggers_dict


def configure_log_levels(levels):
    """
    Given a string or dict of log levels, configure them.
    """
    loggers_dict = get_loggers_dict(levels)
    for logger, level in sort_loggers(loggers_dict):
        if isinstance(level, str):
            level = logging.getLevelName(level.upper())
        logging.getLogger(logger).setLevel(level)


def configure_root_logger(stream, log_format):
    """
    Configure the root logger.

    log_format can be either "plain" or "json".
    """
    stdlib_processors = [
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
    ]

    if log_format == "plain":
        renderer = render_plaintext
    elif log_format == "json":
        renderer = render_json
    else:
        raise ValueError("unknown log_format: %r" % log_format)

    formatter = structlog.stdlib.ProcessorFormatter(
        processor=renderer, foreign_pre_chain=stdlib_processors
    )

    if not structlog.is_configured():
        # See the recommended configuration from the structlog docs.
        structlog.configure(
            processors=(
                [structlog.stdlib.filter_by_level]
                + stdlib_processors
                + [
                    structlog.stdlib.PositionalArgumentsFormatter(),
                    structlog.processors.StackInfoRenderer(),
                    structlog.processors.format_exc_info,
                    structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
                ]
            ),
            context_class=dict,
            logger_factory=structlog.stdlib.LoggerFactory(),
            wrapper_class=structlog.stdlib.BoundLogger,
            cache_logger_on_first_use=True,
        )

    handler = AtomicStreamHandler(stream)
    handler.setFormatter(formatter)
    root_logger = logging.getLogger()
    root_logger.handlers = [handler]


def configure(stream=sys.stderr, log_levels=None, log_format=None):
    """
    Configure all logging.
    """

    if log_levels is None:
        log_levels = os.getenv(ENV_PREFIX + "LOG_LEVELS")
    if log_format is None:
        log_format = os.getenv(ENV_PREFIX + "LOG_FORMAT", DEFAULT_FORMAT)

    # ensure that `warnings` module stuff will be logged
    logging.captureWarnings(capture=True)

    configure_root_logger(stream, log_format)

    configure_log_levels(log_levels)


def get_gunicorn_logconfig_dict():
    """
    Get a dict to be used as ``logconfig_dict`` in a Gunicorn config file.
    """
    return {
        "version": 1,
        "disable_existing_loggers": False,
        "loggers": {"gunicorn.error": {"level": "NOTSET", "propagate": True}},
    }
