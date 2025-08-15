import time
from functools import wraps
from json import JSONDecodeError

from app.__core__.application.logger import logger
from app.__core__.domain.exception.exception import RetryError


def limited_sleep(seconds: float) -> None:
    time.sleep(min(seconds, 4))


def retry_with_backoff(
    rate_limit_error_cls: Exception,
):
    def decorator(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            retries = getattr(self, "MAX_RETRIES")
            current_retry = 0
            backoff = 1.0

            while current_retry < retries:
                try:
                    return func(self, *args, **kwargs)

                except rate_limit_error_cls as exc:
                    logger.warning(
                        "rate_limit_exceeded",
                        extra={"retry": current_retry, "backoff": backoff},
                        exc_info=exc,
                    )
                    if current_retry == retries - 1:
                        raise RetryError(exc)
                    limited_sleep(backoff)
                    backoff *= 2
                    current_retry += 1

                except (KeyError, JSONDecodeError) as exc:
                    logger.error("parsing_error", exc_info=exc)
                    if current_retry == retries - 1:
                        raise RetryError(exc)
                    current_retry += 1

                except Exception as exc:
                    logger.error("unexpected_error", exc_info=exc)
                    raise RetryError(exc)

        return wrapper

    return decorator
