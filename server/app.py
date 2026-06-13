from datetime import datetime, timedelta

from anyio.functools import lru_cache
from fastapi import FastAPI, Depends, HTTPException, Query
from starlette import status

from database import DatabaseClient, DatabaseClientConfig
from worker.jobs.task_reminder.models import Task

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

    if not db_task.frequency_hours:
        database_client.delete(task_id=db_task.id)
        return

    now = datetime.now()
    while db_task.remind_after < now:
        db_task.remind_after += timedelta(hours=db_task.frequency_hours)

    database_client.update(db_task)


@fastapi_app.get("/delay_task", status_code=status.HTTP_200_OK)
async def delay_task(
    task_id: int,
    minutes: int = Query(ge=0, default=0),
    hours: int = Query(ge=0, default=0),
    days: int = Query(ge=0, default=0),
    database_client: DatabaseClient = Depends(get_database_client)
) -> Task:
    db_task = database_client.get_task(task_id)
    if not db_task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    now = datetime.now()
    db_task.delayed_until = now + timedelta(minutes=minutes, hours=hours, days=days)

    database_client.update(db_task)

    return Task.model_validate(db_task, from_attributes=True)

@fastapi_app.get("/delay_all_tasks", status_code=status.HTTP_200_OK)
async def delay_all_tasks(
    minutes: int = Query(ge=0, default=0),
    hours: int = Query(ge=0, default=0),
    days: int = Query(ge=0, default=0),
    database_client: DatabaseClient = Depends(get_database_client)
) -> None:
    for task in database_client.get_all_tasks():
        await delay_task(task.id, minutes=minutes, hours=hours, days=days, database_client=database_client)
