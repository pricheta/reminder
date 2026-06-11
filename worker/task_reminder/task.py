import logging
from datetime import datetime, timezone

from database import DatabaseClient
from vk_client import VKClient

from worker.task_reminder.models import Task


logger = logging.getLogger(__name__)



class TaskReminder:
    def __init__(self, database_client: DatabaseClient, vk_client: VKClient):
        self.database_client = database_client
        self.vk_client = vk_client


    def run_once(self):
        tasks_to_remind_about = self._get_tasks_to_remind_about()
        if not tasks_to_remind_about:
            return

        self._send_reminder(tasks_to_remind_about)


    def _send_reminder(self, tasks_to_remind_about: list[Task]) -> None:
        message = "Пора выполнять таски:\n"

        for task in tasks_to_remind_about:
            message += f"{task.id}.{task.title}\n"

        logger.info('Отправляю напоминалку с сообщением:\n\n{message}')
        self.vk_client.send_message(message)


    def _get_tasks_to_remind_about(self) -> list[Task]:
        all_db_tasks = self.database_client.get_all_tasks()
        if not all_db_tasks:
            return []

        all_tasks = [Task.model_validate(db_task, from_attributes=True) for db_task in all_db_tasks]
        now = datetime.now()

        tasks_to_remind_about = []
        for task in all_tasks:
            delay_active = not task.delayed_until or task.delayed_until < now
            should_remind = task.remind_after < now and not delay_active
            if should_remind:
                tasks_to_remind_about.append(task)

        tasks_to_remind_about = sorted(tasks_to_remind_about, key=lambda task: task.id)

        logger.info(f'Таски, о которых нужно напомнить: {tasks_to_remind_about}')
        return tasks_to_remind_about