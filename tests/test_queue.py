from app.queue import TaskQueue
from app.tasks import Task


def test_priority_order():
    queue = TaskQueue()

    low_priority = Task(
        task_type="sleep",
        args=[1],
        priority=1
    )

    high_priority = Task(
        task_type="sleep",
        args=[1],
        priority=10
    )

    medium_priority = Task(
        task_type="sleep",
        args=[1],
        priority=5
    )

    queue.add_task(low_priority)
    queue.add_task(high_priority)
    queue.add_task(medium_priority)

    first = queue.get_task()
    second = queue.get_task()
    third = queue.get_task()

    assert first.id == high_priority.id
    assert second.id == medium_priority.id
    assert third.id == low_priority.id

    queue.task_done()
    queue.task_done()
    queue.task_done()