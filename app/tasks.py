from dataclasses import dataclass, field
from datetime import datetime
from typing import Any
import uuid
import time
import httpx
from pathlib import Path
from pypdf import PdfReader

@dataclass
class Task:
    task_type: str
    args: list[Any] = field(default_factory=list)
    kwargs: dict[str, Any] = field(default_factory=dict)

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    status: str = "pending"
    result: Any = None
    error: str | None = None

    max_retries: int = 3
    retry_count: int = 0
    retry_delay: float = 1.0
    cancelled: bool = False
    priority: int = 0

    created_at: datetime = field(default_factory=datetime.now)

def add(a, b):
    return a + b

def multiply(a, b):
    return a * b

def sleep_task(seconds):
    time.sleep(seconds)
    return f"Slept for {seconds} seconds"

def fail_task():
    raise RuntimeError("Task failed intentionally")

def index_document(document_path):
    response = httpx.post(
        "http://127.0.0.1:8001/internal/index",
        params={
            "document_path": document_path
        },
        #test için değiştirdim 30 orjinali
        timeout=300
    )

    response.raise_for_status()

    return response.json()

def process_document_chunk(document_path, start_page, end_page):


    file_path = Path(document_path)

    start = time.perf_counter()

    reader = PdfReader(file_path)

    pages = []

    for page_index in range(start_page - 1, min(end_page, len(reader.pages))):
        page = reader.pages[page_index]
        text = page.extract_text()

        if text:
            pages.append({
                "page": page_index + 1,
                "text": text
            })

    elapsed = time.perf_counter() - start

    print(
        f"[Chunk] {file_path.name} | "
        f"pages={start_page}-{end_page} | "
        f"extracted={len(pages)} | "
        f"time={elapsed:.2f}s"
    )

    return {
        "document": str(file_path),
        "start_page": start_page,
        "end_page": end_page,
        "pages": pages,
        "elapsed": round(elapsed, 2)
    }


TASK_REGISTRY = {
    "add": add,
    "multiply": multiply,
    "sleep": sleep_task,
    "fail": fail_task,
    "index_document": index_document,
}

