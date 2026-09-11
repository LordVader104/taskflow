from pydantic import BaseModel, Field

from app.task_manager import TaskManager
from app.queue import TaskQueue
from app.tasks import Task, TASK_REGISTRY

from worker.worker import Worker

from datetime import datetime

from fastapi import FastAPI, HTTPException, Query


app = FastAPI(
    title="TaskFlow",
    version="0.1.0"
)


task_manager = TaskManager()
task_queue = TaskQueue()

workers = []

for i in range(3):
    worker = Worker(
        worker_id=i + 1,
        task_queue=task_queue
    )

    worker.start()
    workers.append(worker)


class TaskRequest(BaseModel):
    task_type: str = Field(min_length=1)
    args: list = Field(default_factory=list)
    kwargs: dict = Field(default_factory=dict)
    priority: int = Field(default=0, ge=0)


class TaskResponse(BaseModel):
    task_id: str
    status: str


class TaskDetailResponse(BaseModel):
    task_id: str
    task_type: str
    status: str
    result: object | None = None
    error: str | None = None


class TaskListItem(BaseModel):
    task_id: str
    task_type: str
    status: str
    result: object | None = None
    error: str | None = None
    priority: int
    created_at: datetime

class CancelResponse(BaseModel):
    task_id: str
    status: str


@app.get("/")
def root():
    return {
        "name": "TaskFlow",
        "status": "running"
    }


@app.post("/tasks", response_model=TaskResponse)
def create_task(request: TaskRequest):
    if request.task_type not in TASK_REGISTRY:
        raise HTTPException(
            status_code=400,
            detail=f"Unknown task type: {request.task_type}"
        )

    task = Task(
        task_type=request.task_type,
        args=request.args,
        kwargs=request.kwargs,
        priority=request.priority
    )

    task_manager.add_task(task)
    task_queue.add_task(task)

    return {
        "task_id": task.id,
        "status": task.status
    }

@app.get("/tasks", response_model=list[TaskListItem])
def list_tasks(
    status: str | None = None,
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0)
):
    tasks = task_manager.list_tasks(
        status=status,
        limit=limit,
        offset=offset
    )

    return [
        {
            "task_id": row[0],
            "task_type": row[1],
            "status": row[2],
            "result": row[3],
            "error": row[4],
            "priority": row[5],
            "created_at": row[6]
        }
        for row in tasks
    ]


@app.get("/tasks/{task_id}", response_model=TaskDetailResponse)
def get_task(task_id: str):
    task = task_manager.get_task(task_id)

    if task is None:
        raise HTTPException(
            status_code=404,
            detail="Task not found"
        )

    return {
        "task_id": task.id,
        "task_type": task.task_type,
        "status": task.status,
        "result": task.result,
        "error": task.error
    }


@app.post(
    "/tasks/{task_id}/cancel",
    response_model=CancelResponse
)
def cancel_task(task_id: str):
    result = task_manager.cancel_task(task_id)

    if result is None:
        raise HTTPException(
            status_code=404,
            detail="Task not found"
        )

    if result is False:
        raise HTTPException(
            status_code=400,
            detail="Task cannot be cancelled"
        )

    return {
        "task_id": task_id,
        "status": "cancelled"
    }