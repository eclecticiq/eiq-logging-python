"""
Standardized logging configuration for EIQ projects.
"""

import os
import logging
import sys
import traceback

import structlog


DELIMITER = ","
DEFAULT_FORMAT = "json"
DEFAULT_LEVELS = {
    "": logging.INFO,
    "requests": logging.WARNING,
    "urllib3": logging.WARNING,
}
ENV_PREFIX = "EIQ_"

# if for whatever reason we switch away from structlog in the future?
get_logger = structlog.get_logger


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


def render_log_in_plaintext(logger, level, event):
    """
    Render a structlog event in plaintext.
    """
    event = event.copy()  # prevent mutation of dict from caller side
    ret = "{timestamp} [{level:7}] [{logger}] {event}".format(
        timestamp=event.pop("timestamp"),
        logger=event.pop("logger", logger.name if logger else "UNKNOWN"),
        level=event.pop("level", level).upper(),
        event=event.pop("event"),
    )
    exc_info = event.pop("exc_info", None)
    # format any leftover key-value pairs
    if event:
        kv_pairs = ", ".join("%s=%s" % (k, v) for k, v in event.items())
        ret += " [%s]" % kv_pairs
    if exc_info:
        ret += "\n"
        ret += "".join(traceback.format_exception(*exc_info)).strip("\n")
    return ret


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
        renderer = render_log_in_plaintext
    elif log_format == "json":
        renderer = structlog.processors.JSONRenderer(sort_keys=True)
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
    logging.captureWarnings(True)

    configure_root_logger(stream, log_format)

    configure_log_levels(log_levels)


class AtomicStreamHandler(logging.StreamHandler):
    """
    A ``StreamHandler`` override that provides ``emit`` method which
    does only one ``write`` per record to the underlying stream. This
    is to keep an individual logging record per line. It's important
    for JSON logging.

    In our case we have pre-forked gunicorn worker processes which
    inherit ``stdout`` from the master process and write into it
    concurrently [1]_. Kernel has the following guarantee for
    write [2]_::

        The adjustment of the file offset and the write operation
        are performed as an atomic step.

    On Python side, ``_io.TextIOWrapper``, which is the type of
    ``sys.stdout``, doesn't provide explicit guarantee but experiments
    show that for records of 8KB and 50 forked processes, lines are
    not interleaved.

    Output stream buffering [3]_ doesn't seem to have an effect.

    .. [1]: https://github.com/benoitc/gunicorn/issues/1272
    .. [2]: https://linux.die.net/man/2/write
    .. [3]: https://eklitzke.org/stdout-buffering
    """

    def emit(self, record):
        try:
            self.stream.write(self.format(record) + "\n")
            self.flush()
        except Exception:
            self.handleError(record)


def get_gunicorn_logconfig_dict():
    """
    Get a dict to be used as ``logconfig_dict`` in a Gunicorn config file.
    """
    return {
        "version": 1,
        "disable_existing_loggers": False,
        "loggers": {"gunicorn.error": {"level": "NOTSET", "propagate": True}},
    }
