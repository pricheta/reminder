from dotenv import load_dotenv
load_dotenv()

from worker.app import Worker, WorkerConfig
from worker.task_reminder.task import TaskReminder
from vk_client import VKClient, VKClientConfig
from database import DatabaseClientConfig, DatabaseClient


if __name__ == "__main__":
    database_client_config = DatabaseClientConfig()
    database_client = DatabaseClient(database_client_config)

    vk_client_config = VKClientConfig()
    vk_client = VKClient(vk_client_config)

    task_reminder = TaskReminder(database_client, vk_client)

    worker_config = WorkerConfig()
    worker = Worker()
    worker.add_task(task_reminder.run_once)

