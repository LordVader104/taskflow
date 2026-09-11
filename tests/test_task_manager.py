from app.task_manager import TaskManager
from app.tasks import Task


def test_add_and_get_task():
    manager = TaskManager()

    task = Task(
        task_type="add",
        args=[10, 20],
        kwargs={},
        priority=5
    )

    manager.add_task(task)

    saved_task = manager.get_task(task.id)

    assert saved_task is not None
    assert saved_task.id == task.id
    assert saved_task.task_type == "add"
    assert saved_task.args == [10, 20]
    assert saved_task.kwargs == {}
    assert saved_task.status == "pending"
    assert saved_task.priority == 5


def test_get_nonexistent_task():
    manager = TaskManager()

    task = manager.get_task("does-not-exist")

    assert task is None


def test_cancel_task():
    manager = TaskManager()

    task = Task(
        task_type="sleep",
        args=[10],
        priority=1
    )

    manager.add_task(task)

    result = manager.cancel_task(task.id)

    assert result is True

    cancelled_task = manager.get_task(task.id)

    assert cancelled_task is not None
    assert cancelled_task.status == "cancelled"


def test_cancel_completed_task(db_connection):
    manager = TaskManager()

    task = Task(
        task_type="add",
        args=[10, 20],
        priority=1
    )

    manager.add_task(task)

    with db_connection.cursor() as cur:
        cur.execute(
            """
            UPDATE tasks
            SET status = 'completed'
            WHERE id = %s
            """,
            (task.id,)
        )

    db_connection.commit()

    result = manager.cancel_task(task.id)

    assert result is False


def test_list_tasks():
    manager = TaskManager()

    task1 = Task(
        task_type="add",
        args=[1, 2]
    )

    task2 = Task(
        task_type="multiply",
        args=[3, 4]
    )

    manager.add_task(task1)
    manager.add_task(task2)

    tasks = manager.list_tasks()

    ids = [row[0] for row in tasks]

    assert task1.id in ids
    assert task2.id in ids