import asyncio
from collections.abc import Awaitable
from typing import Optional, Set

from app.__core__.application.logger import logger


class TaskManager:
    def __init__(self) -> None:
        self._tasks: Set[asyncio.Task] = set()

    def create(self, coroutine: Awaitable, *, name: Optional[str] = None) -> None:
        task = asyncio.create_task(coroutine, name=name)
        self._tasks.add(task)

        def _done_callback(task: asyncio.Task):
            try:
                task.result()
            except asyncio.CancelledError:
                logger.info("task_cancelled", task_name=task.get_name())
            except Exception:
                logger.exception("task_failed", task_name=task.get_name())
            finally:
                self._tasks.discard(task)

        task.add_done_callback(_done_callback)

    async def shutdown(self) -> None:
        pending = [task for task in self._tasks if not task.done()]
        for task in pending:
            task.cancel()
        if pending:
            await asyncio.gather(*pending, return_exceptions=True)
