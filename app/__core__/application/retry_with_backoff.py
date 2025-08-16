import asyncio
from functools import wraps
from json.decoder import JSONDecodeError

from app.__core__.application.logger import logger
from app.__core__.domain.exception.exception import RetryError


async def limited_sleep(seconds: float) -> None:
    await asyncio.sleep(min(seconds, 4))


def retry_with_backoff(
    rate_limit_error_cls: Exception,
):
    def decorator(func):
        @wraps(func)
        async def async_wrapper(self, *args, **kwargs):
            retries = getattr(self, "MAX_RETRIES")
            current_retry = 0
            backoff = 1.0

            while current_retry < retries:
                try:
                    return await func(self, *args, **kwargs)

                except rate_limit_error_cls as exc:
                    logger.warning(
                        "rate_limit_exceeded",
                        extra={"retry": current_retry, "backoff": backoff},
                    )
                    if current_retry == retries - 1:
                        raise RetryError(exc)
                    await limited_sleep(backoff)
                    backoff *= 2
                    current_retry += 1

                except (KeyError, JSONDecodeError):
                    logger.warning("parsing_error")
                    return None

                except Exception as exc:
                    logger.error("unexpected_error", exc_info=exc)
                    raise RetryError(exc)

        return async_wrapper

    return decorator
