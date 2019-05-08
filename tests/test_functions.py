import sys

from eiq_logging.constants import DEFAULT_LEVELS
from eiq_logging.helpers import (
    parse_str, get_loggers_dict,
    sort_loggers, render_log_in_plaintext)


def test_parse_str_to_dict():
    expected = {"": "info", "example": "debug", "urllib3": "warning"}
    var = "root:info,example:debug,urllib3:warning"
    assert parse_str(var) == expected
    var = "info,example:debug,urllib3:warning"
    assert parse_str(var) == expected


def test_get_loggers_dict_root_str():
    loggers_dict = get_loggers_dict('info')
    assert loggers_dict == {'': 'info'}


def test_get_loggers_dict_root_dict():
    loggers_dict = get_loggers_dict({'': 'info'})
    assert loggers_dict == {'': 'info'}


def test_get_loggers_dict_specific_logger():
    expected = DEFAULT_LEVELS.copy()
    expected['foo'] = 'info'

    loggers_dict = get_loggers_dict('foo:info')
    assert loggers_dict == expected

    loggers_dict = get_loggers_dict({'foo': 'info'})
    assert loggers_dict == expected


def test_sort_loggers():
    expected = ["", "foo", "foo.bar", "foobar", "xyz"]
    values = {"": 0, "foo": 0, "foo.bar": 0, "foobar": 0, "xyz": 0}
    assert [l[0] for l in sort_loggers(values)] == expected


def test_plaintext_logger():
    event = {
        "timestamp": "2018-08-16T08:50:55.711270Z",
        "logger": "test",
        "level": "info",
        "event": "test-event",
    }
    ret = render_log_in_plaintext(None, None, event)
    assert ret == "2018-08-16T08:50:55.711270Z [INFO   ] [test] test-event"

    event = {
        "timestamp": "2018-08-16T08:50:55.711270Z",
        "logger": "test",
        "level": "warning",
        "event": "test-event",
        "extra": "foo",
    }
    ret = render_log_in_plaintext(None, None, event)
    assert ret == (
        "2018-08-16T08:50:55.711270Z [WARNING] [test] test-event" " [extra=foo]"
    )

    try:
        raise Exception("test")
    except Exception:
        exc_info = sys.exc_info()
    event = {
        "timestamp": "2018-08-16T08:50:55.711270Z",
        "logger": "test",
        "level": "error",
        "event": "err",
        "exc_info": exc_info,
    }
    line = render_log_in_plaintext(None, None, event).split("\n")
    assert line[0] == "2018-08-16T08:50:55.711270Z [ERROR  ] [test] err"
    assert line[1] == "Traceback (most recent call last):"
    assert line[-2] == '    raise Exception("test")'
    assert line[-1] == "Exception: test"
