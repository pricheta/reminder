import logging
from threading import Thread
import time
from typing import Callable

from pydantic import BaseModel


logger = logging.getLogger(__name__)

Task = Callable[[], None]


class WorkerConfig(BaseModel):
    REPEAT_FREQUENCY_SECONDS: int = 300


class Worker:
    def __init__(self, config: WorkerConfig) -> None:
        self.config = config
        self.tasks: list[Task] = []

    def add_task(self, task: Task) -> None:
        self.tasks.append(task)

    def run(self) -> None:
        logger.info(f"Worker started at")

        while True:
            start_time = time.time()

            threads = []
            for task in self.tasks:
                threads.append(Thread(target=task, daemon=True))

            logger.info(f"Worker running {len(threads)} tasks")
            for thread in threads:
                thread.start()
            for thread in threads:
                thread.join()

            time_elapsed = time.time() - start_time
            logger.info(f"Tasks finished in {time_elapsed} seconds")

            time_to_sleep = self.config.REPEAT_FREQUENCY_SECONDS - time_elapsed
            time_to_sleep = max(0, time_to_sleep)
            time.sleep(time_to_sleep)