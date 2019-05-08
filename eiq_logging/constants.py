import logging


DELIMITER = ","
DEFAULT_FORMAT = "json"
DEFAULT_LEVELS = {
    "": logging.INFO,
    "requests": logging.WARNING,
    "urllib3": logging.WARNING,
}
ENV_PREFIX = "EIQ_"
