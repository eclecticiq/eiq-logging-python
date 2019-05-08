from logging import StreamHandler


class AtomicStreamHandler(StreamHandler):
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
