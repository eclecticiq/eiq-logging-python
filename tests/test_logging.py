import io
import json
import logging
from datetime import datetime, timedelta, timezone

import pytest
import structlog

import eiq_logging


def parse_iso8601(value):
    datetime_format = "%Y-%m-%dT%H:%M:%S.%fZ"
    if not value.endswith('Z'):
        datetime_format += '%z'
    dt = datetime.strptime(value, datetime_format)
    if value.endswith('Z'):
        dt = dt.replace(tzinfo=timezone.utc)
    return dt


@pytest.fixture
def log_stream():
    stream = io.StringIO()
    eiq_logging.configure(stream=stream)
    yield stream


def test_stdlib_structlog_same_output(log_stream):
    now = datetime.now(timezone.utc)

    logging.getLogger("foo").info("stdlib works")
    structlog.get_logger("bar").info("structlog works")

    lines = list(map(json.loads, log_stream.getvalue().splitlines()))

    assert 2 == len(lines)
    for i in range(2):
        line_created = parse_iso8601(lines[i].pop("timestamp"))
        assert line_created - now < timedelta(seconds=1)

    assert [
        {"event": "stdlib works", "level": "info", "logger": "foo"},
        {"event": "structlog works", "level": "info", "logger": "bar"},
    ] == lines


def test_stdlib_structlog_same_output_caplog(log_stream, caplog):
    logging.getLogger("foo").info("stdlib works")
    structlog.get_logger("bar").info("structlog works")

    assert 2 == len(caplog.records)
    assert "stdlib works" == caplog.records[0].msg

    # We use ``structlog.stdlib.ProcessorFormatter.wrap_for_formatter``
    # so ``msg`` for ``LogRecord`` is a ``dict``.
    assert "structlog works" == caplog.records[1].msg["event"]
