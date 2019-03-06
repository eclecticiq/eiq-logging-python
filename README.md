# `eiq_logging`

This package exists to make it easy to configure logging in a consistent way
across multiple EclecticIQ Python projects.

## Installation

    pip install eiq-logging

## Usage

In your application's entrypoint, whatever that may be:

    import eiq_logging
    eiq_logging.configure()

The `configure` function takes a few arguments:

- `stream` determines where logs are written. Defaults to `sys.stderr`.
- `log_format` can be either "plain" or "json". "plain" means plain text and is meant to be read by humans. "json" is newline-delimited JSON, meant for log aggregation and machine parsing.
- `log_levels` can be either a dict of `{logger_name: log_level}` or a string which will be parsed as such. The string is comma-separated, and each item in the string should be in the format of "logger_name:log_level" - for example, `root:info,example:debug` will set the root logger to the level INFO, and the logger "example" to level DEBUG.

If you leave out the `log_format` and `log_level` arguments, you can configure these through the environment variables `EIQ_LOG_FORMAT` and `EIQ_LOG_LEVEL`.

If you're using Gunicorn, you don't need to call `configure` yourself, you can just start the process with the `--config` flag:

    gunicorn --config=python:eiq_logging.gunicorn myapp
