"""
https://stackoverflow.com/a/22156618

Since requests' timeout parameter is not a really timeout,
we need this solution.

Usage:
    Use only this module in the main thread, which is the case for the
"""
import signal

MAX_CONNECTION_LENGTH = 30


class Timeout():
    """ Timeout for use with the `with` statement. """

    class TimeoutException(Exception):
        """ Simple Exception to be called on timeouts. """

    def _timeout(self, frame):
        """ Raise an TimeoutException.

        This is intended for use as a signal handler.
        The signum and frame arguments passed to this are ignored.

        """
        raise Timeout.TimeoutException()

    def __init__(self, timeout=30):
        self.timeout = timeout
        signal.signal(signal.SIGALRM, Timeout._timeout)

    def __enter__(self):
        signal.alarm(self.timeout)

    def __exit__(self, exc_type, exc_value, traceback):
        signal.alarm(0)
        return exc_type is Timeout.TimeoutException
