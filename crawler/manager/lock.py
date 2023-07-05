from functools import wraps
import os
import time
import fcntl
from functools import wraps

from crawler import utils

LOG = utils.get_logger(__file__)

LOCK_RETRY = int(os.environ.get('LOCK_RETRY'))
LOCK_TIMEOUT = int(os.environ.get('LOCK_TIMEOUT'))
LOCK_RETRY_INTERVAL = float(os.environ.get('LOCK_RETRY_INTERVAL'))


def lock(lock_name):
    """
    Decorator to lock the file while the function is running.
    """

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            retries = 0

            while retries < LOCK_RETRY:
                try:
                    lock_file = open(lock_name, 'w')
                    fcntl.flock(lock_file, fcntl.LOCK_EX | fcntl.LOCK_NB)
                    result = func(*args, **kwargs)
                    fcntl.flock(lock_file, fcntl.LOCK_UN)
                    return result
                except IOError:
                    LOG.info("Failed to acquire lock. Another process is currently accessing the code.")
                    retries += 1
                    time.sleep(LOCK_RETRY_INTERVAL)
                finally:
                    lock_file.close()

            LOG.error("Failed to acquire lock after maximum retries.")
            # Handle the case when the lock couldn't be acquired (retry logic or error handling)

        return wrapper

    return decorator
