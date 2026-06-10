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

    now = datetime.now()
    while task.last_time_done < now:
        task.last_time_done += timedelta(hours=task.frequency_hours)

    database_client.update_task_last_time_done(task_id=task.id, task_last_time_done=task.last_time_done)

