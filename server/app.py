from fastapi import FastAPI

fastapi_app = FastAPI(docs_url="/")

@fastapi_app.get("/mark_task_done")
async def mark_task_done():
    return "done"
