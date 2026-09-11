import psycopg

from app.queue import TaskQueue
from app.tasks import Task
from app.config import DATABASE_URL
from app.task_manager import TaskManager
from worker.worker import execute_task

import time

from worker.worker import Worker


def test_execute_task_success():
    conn = psycopg.connect(DATABASE_URL)

    try:
        manager = TaskManager()

        task = Task(
            task_type="add",
            args=[10, 20],
            priority=5
        )

        manager.add_task(task)

        result = execute_task(task, conn)

        assert result is True
        assert task.status == "completed"
        assert task.result == 30
        assert task.error is None

        saved_task = manager.get_task(task.id)

        assert saved_task is not None
        assert saved_task.status == "completed"
        assert saved_task.result == 30
        assert saved_task.error is None

    finally:
        conn.close()

def test_execute_task_retry():
    conn = psycopg.connect(DATABASE_URL)

    try:
        manager = TaskManager()

        task = Task(
            task_type="fail",
            max_retries=3,
            retry_delay=0
        )

        manager.add_task(task)

        result = execute_task(task, conn)

        assert result is False
        assert task.status == "retrying"
        assert task.retry_count == 1
        assert task.error == "Task failed intentionally"

        saved_task = manager.get_task(task.id)

        assert saved_task is not None
        assert saved_task.status == "retrying"
        assert saved_task.retry_count == 1
        assert saved_task.error == "Task failed intentionally"

    finally:
        conn.close()

def test_execute_task_final_failure():
    conn = psycopg.connect(DATABASE_URL)

    try:
        manager = TaskManager()

        task = Task(
            task_type="fail",
            max_retries=3,
            retry_delay=0
        )

        manager.add_task(task)

        for _ in range(4):
            result = execute_task(task, conn)

        assert result is True
        assert task.status == "failed"
        assert task.retry_count == 4
        assert task.error == "Task failed intentionally"

        saved_task = manager.get_task(task.id)

        assert saved_task is not None
        assert saved_task.status == "failed"
        assert saved_task.retry_count == 4
        assert saved_task.error == "Task failed intentionally"

    finally:
        conn.close()

def test_cancelled_task_is_not_executed():
    manager = TaskManager()

    task_queue = TaskQueue()

    task = Task(
        task_type="add",
        args=[10, 20],
        priority=5
    )

    manager.add_task(task)
    task_queue.add_task(task)

    result = manager.cancel_task(task.id)

    assert result is True

    worker = Worker(
        worker_id=1,
        task_queue=task_queue
    )
    assert worker.is_cancelled(task.id) is True

def test_worker_processes_task():
    manager = TaskManager()
    task_queue = TaskQueue()

    task = Task(
        task_type="add",
        args=[15, 25],
        priority=5
    )

    manager.add_task(task)
    task_queue.add_task(task)

    worker = Worker(
        worker_id=1,
        task_queue=task_queue
    )

    worker.start()

    task_queue.join()

    saved_task = manager.get_task(task.id)

    assert saved_task is not None
    assert saved_task.status == "completed"
    assert saved_task.result == 40
    assert saved_task.error is None

def test_multiple_workers_process_tasks_in_parallel():
    manager = TaskManager()
    task_queue = TaskQueue()

    workers = []

    for i in range(3):
        worker = Worker(
            worker_id=i + 1,
            task_queue=task_queue
        )
        worker.start()
        workers.append(worker)

    tasks = [
        Task(task_type="sleep", args=[1]),
        Task(task_type="sleep", args=[1]),
        Task(task_type="sleep", args=[1]),
    ]

    for task in tasks:
        manager.add_task(task)
        task_queue.add_task(task)

    start = time.time()

    task_queue.join()

    elapsed = time.time() - start

    for task in tasks:
        saved_task = manager.get_task(task.id)

        assert saved_task is not None
        assert saved_task.status == "completed"
        assert saved_task.result == "Slept for 1 seconds"

    assert elapsed < 2.5