import sys
import logging, logging.handlers
import functools

import tg_settings

logger = None
debug = None

def export(fn):
    mod = sys.modules[fn.__module__]
    if hasattr(mod, '__all__'):
        mod.__all__.append(fn.__name__)
    else:
        mod.__all__ = [fn.__name__]
    return fn

def getLoggerName():
    return tg_settings.tg_keyword+"_bot"

# Define a few command handlers. These usually take the two arguments bot and
# update. Error handlers also receive the raised TelegramError object in error.
def log(func):
    logger = logging.getLogger(getLoggerName())
    @functools.wraps(func)
    def decorator(*args, **kwargs):
        logger.debug('>>> Entering: %s', func.__name__)
        result = func(*args, **kwargs)
        logger.debug(result)
        logger.debug('<<< Exiting: %s', func.__name__)
        return result

    return decorator