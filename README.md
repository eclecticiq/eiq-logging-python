# `eiq_logging`

This package exists to make it easy to configure logging in a consistent way
across multiple EclecticIQ Python projects.

## Installation

    pip install eiq-logging

## Usage

In your application's entrypoint, whatever that may be:

    import eiq_logging
    eiq_logging.configure()

If you're using Gunicorn, you can start it with the `--config` flag:

    gunicorn --config=python:eiq_logging.gunicorn myapp
