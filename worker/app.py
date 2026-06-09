from threading import Thread
import time
from typing import Callable

from pydantic import BaseModel


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
        while True:
            start_time = time.time()

            threads = []
            for task in self.tasks:
                threads.append(Thread(target=task, daemon=True))

            for thread in threads:
                thread.start()

            for thread in threads:
                thread.join()

            time_elapsed = time.time() - start_time

            time_to_sleep = self.config.REPEAT_FREQUENCY_SECONDS - time_elapsed
            time_to_sleep = max(0, time_to_sleep)
            time.sleep(time_to_sleep)