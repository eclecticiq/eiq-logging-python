import traceback

import structlog


def render_plaintext(logger, level, event):
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


def render_json(logger, level, event):
    event = structlog.processors.format_exc_info(logger, level, event)
    renderer = structlog.processors.JSONRenderer(sort_keys=True)
    return renderer(logger, level, event)
