import time
from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_root():
    response = client.get("/")

    assert response.status_code == 200
    assert response.json() == {
        "name": "TaskFlow",
        "status": "running"
    }


def test_create_task():
    response = client.post(
        "/tasks",
        json={
            "task_type": "add",
            "args": [10, 20],
            "priority": 5
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert "task_id" in data
    assert data["status"] == "pending"


def test_get_task():
    create_response = client.post(
        "/tasks",
        json={
            "task_type": "add",
            "args": [10, 20]
        }
    )

    task_id = create_response.json()["task_id"]

    for _ in range(20):
        response = client.get(f"/tasks/{task_id}")

        assert response.status_code == 200

        data = response.json()

        if data["status"] == "completed":
            break

        time.sleep(0.1)

    assert response.json()["status"] == "completed"

    assert response.status_code == 200

    data = response.json()

    assert data["task_id"] == task_id
    assert data["task_type"] == "add"
    assert data["status"] == "completed"
    assert data["result"] == 30
    assert data["error"] is None

def test_cancel_task():
    response = client.post(
        "/tasks",
        json={
            "task_type": "sleep",
            "args": [10]
        }
    )

    assert response.status_code == 200

    task_id = response.json()["task_id"]

    cancel_response = client.post(
        f"/tasks/{task_id}/cancel"
    )

    assert cancel_response.status_code == 200

    data = cancel_response.json()

    assert data["task_id"] == task_id
    assert data["status"] == "cancelled"

def test_get_nonexistent_task():
    response = client.get(
        "/tasks/does-not-exist"
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Task not found"


def test_cancel_nonexistent_task():
    response = client.post(
        "/tasks/does-not-exist/cancel"
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Task not found"

def test_create_task_with_invalid_type():
    response = client.post(
        "/tasks",
        json={
            "task_type": "does_not_exist",
            "args": []
        }
    )

    assert response.status_code == 400
    assert response.json()["detail"] == (
        "Unknown task type: does_not_exist"
    )

def test_list_tasks():
    response = client.post(
        "/tasks",
        json={
            "task_type": "add",
            "args": [5, 10]
        }
    )

    assert response.status_code == 200

    task_id = response.json()["task_id"]

    import time
    time.sleep(0.5)

    response = client.get("/tasks")

    assert response.status_code == 200

    tasks = response.json()

    assert isinstance(tasks, list)

    task_ids = [
        task["task_id"]
        for task in tasks
    ]

    assert task_id in task_ids

def test_list_tasks_by_status():
    response = client.post(
        "/tasks",
        json={
            "task_type": "add",
            "args": [100, 200]
        }
    )

    assert response.status_code == 200

    task_id = response.json()["task_id"]

    for _ in range(20):
        response = client.get(f"/tasks/{task_id}")

        assert response.status_code == 200

        data = response.json()

        if data["status"] == "completed":
            break

        time.sleep(0.1)

    assert response.json()["status"] == "completed"

    response = client.get("/tasks?status=completed")

    assert response.status_code == 200

    tasks = response.json()

    task_ids = [
        task["task_id"]
        for task in tasks
    ]

    assert task_id in task_ids

def test_list_tasks_with_limit():
    for _ in range(5):
        response = client.post(
            "/tasks",
            json={
                "task_type": "add",
                "args": [1, 2]
            }
        )
        assert response.status_code == 200

    time.sleep(0.5)

    response = client.get("/tasks?limit=3")

    assert response.status_code == 200

    data = response.json()

    assert len(data) <= 3

def test_list_tasks_with_offset():
    response = client.get("/tasks?limit=2&offset=2")

    assert response.status_code == 200

    data = response.json()

    assert len(data) <= 2

def test_list_tasks_invalid_pagination():
    response = client.get("/tasks?limit=0")

    assert response.status_code == 422

    response = client.get("/tasks?limit=101")

    assert response.status_code == 422

    response = client.get("/tasks?offset=-1")

    assert response.status_code == 422