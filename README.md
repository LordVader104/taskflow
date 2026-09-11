# TaskFlow

## Purpose & Learning Goals

TaskFlow was built as a hands-on project to understand how task queue and worker-based systems are designed and implemented.

The main learning goals were:

- Understanding task queue architecture
- Designing producer-consumer systems
- Working with concurrent workers and threads
- Implementing priority-based task scheduling
- Managing task lifecycle and state transitions
- Implementing retry mechanisms and exponential backoff
- Persisting task state and results with PostgreSQL
- Designing and implementing REST APIs with FastAPI
- Validating API input and responses with Pydantic
- Writing automated tests with pytest
- Handling database access safely across multiple worker threads
- Designing a system that can later be extended into a distributed architecture

The project intentionally started with an in-memory queue and local worker threads. This provides a simple foundation for later introducing Redis, independent worker processes, and containerized deployment.

TaskFlow is a lightweight task queue and worker system built with Python and FastAPI.

The project demonstrates task scheduling, priority-based execution, concurrent workers, retry handling, task cancellation, PostgreSQL persistence, and a REST API.

## Features

- REST API built with FastAPI
- Priority-based task queue
- Multiple concurrent workers
- PostgreSQL task persistence
- Task status tracking
- Task cancellation
- Automatic retry mechanism
- Exponential retry delay
- Pagination and status filtering
- Pydantic request/response validation
- Automated tests with pytest

## Architecture

```text
                ┌──────────────┐
                │    Client    │
                └──────┬───────┘
                       │
                       ▼
                ┌──────────────┐
                │   FastAPI    │
                │     API      │
                └──────┬───────┘
                       │
             ┌─────────┴─────────┐
             │                   │
             ▼                   ▼
      ┌─────────────┐     ┌──────────────┐
      │ PostgreSQL  │     │ Task Queue   │
      │ Persistence │     │ PriorityQueue│
      └─────────────┘     └──────┬───────┘
                                  │
                    ┌─────────────┼─────────────┐
                    ▼             ▼             ▼
               ┌─────────┐   ┌─────────┐   ┌─────────┐
               │ Worker 1│   │ Worker 2│   │ Worker 3│
               └─────────┘   └─────────┘   └─────────┘