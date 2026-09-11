import json
import urllib.request

tasks = [
    {"task_type": "sleep", "args": [2], "kwargs": {}, "priority": 1},
    {"task_type": "sleep", "args": [2], "kwargs": {}, "priority": 10},
    {"task_type": "sleep", "args": [2], "kwargs": {}, "priority": 5},
    {"task_type": "sleep", "args": [2], "kwargs": {}, "priority": 20},
    {"task_type": "sleep", "args": [2], "kwargs": {}, "priority": 2},
]

print("Tasks gönderiliyor...\n")

for task in tasks:
    data = json.dumps(task).encode("utf-8")

    request = urllib.request.Request(
        "http://127.0.0.1:8000/tasks",
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST"
    )

    with urllib.request.urlopen(request) as response:
        result = json.loads(response.read().decode("utf-8"))

    print(
        f"priority={task['priority']} "
        f"-> {result['task_id']}"
    )

print("\nTüm tasklar gönderildi.")