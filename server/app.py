from datetime import datetime, timedelta

from anyio.functools import lru_cache
from fastapi import FastAPI, Depends, HTTPException
from starlette import status

from database import DatabaseClient, DatabaseClientConfig
from worker.task_reminder.models import Task

fastapi_app = FastAPI(docs_url="/")


@lru_cache
def get_database_client():
    config = DatabaseClientConfig()
    return DatabaseClient(config)


@fastapi_app.get("/mark_task_done", status_code=status.HTTP_200_OK)
async def mark_task_done(task_id: int, database_client: DatabaseClient = Depends(get_database_client)) -> None:
    db_task = database_client.get_task(task_id)
    if not db_task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    task = Task.model_validate(db_task, from_attributes=True)

    if not task.frequency_hours:
        database_client.delete_task(task_id=task.id)
        return

    now = datetime.now()
    while task.next_time_to_do < now:
        task.next_time_to_do += timedelta(hours=task.frequency_hours)

    database_client.update_task_next_time_to_do(task_id=task.id, next_time_to_do=task.next_time_to_do)


@fastapi_app.get("/delay_task", status_code=status.HTTP_200_OK)
async def delay_task(task_id: int, times: int, database_client: DatabaseClient = Depends(get_database_client)) -> None:
    db_task = database_client.get_task(task_id)
    if not db_task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    task = Task.model_validate(db_task, from_attributes=True)

    if task.frequency_hours:
        for _ in range(times):
            task.next_time_to_do += timedelta(hours=task.frequency_hours)
    else:
        task.next_time_to_do += timedelta(hours=times)

    database_client.update_task_next_time_to_do(task_id=task.id, next_time_to_do=task.next_time_to_do)
