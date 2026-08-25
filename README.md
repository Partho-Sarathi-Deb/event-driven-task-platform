# Task Platform - Event-Driven Microservices

An event-driven microservice architecture built with FastAPI, RabbitMQ, PostgreSQL, and Docker Compose.

The system consists of two services communicating asynchronously through a message broker:

* **Task Service** — REST API for managing tasks. Persists data to PostgreSQL and publishes `TASK_CREATED`, `TASK_UPDATED`, and `TASK_DELETED` events to RabbitMQ on every write.
* **Notification Service** — Runs a background consumer thread that listens to RabbitMQ and processes task events asynchronously, independent of the API's request/response cycle.

---

## Architecture Overview

```
[Client] ---> (POST/PUT/DELETE /tasks) ---> [Task Service] ---> (Write) ---> [PostgreSQL]
                                                   |
                                           (Publish Event)
                                                   v
                                             [RabbitMQ]
                                                   |
                                           (Consume Event)
                                                   v
                                        [Notification Service]
```

---

## Tech Stack

| Component        | Technology              |
|-------------------|--------------------------|
| Language          | Python 3.12              |
| API Framework     | FastAPI, Uvicorn         |
| Database          | PostgreSQL, SQLAlchemy   |
| Messaging         | RabbitMQ, Pika           |
| Containerization  | Docker, Docker Compose   |
| Testing & CI      | Pytest, GitHub Actions   |

---

## Prerequisites

* Docker & Docker Compose
* curl or Postman (for API testing)

---

## Quick Start

### 1. Run the Platform

Clone the repository and start all containers in detached mode:
```
docker-compose up -d --build
```
Docker Compose builds both services and waits for the PostgreSQL and RabbitMQ health checks to pass before starting `task-service` and `notification-service`.

### 2. Verify Container Health

```
docker-compose ps
```
All four containers (`postgres`, `rabbitmq`, `task-service`, `notification-service`) should show as `healthy` or `running`.

---

## Service Endpoints

| Service               | Protocol / Port              | URL                              |
|------------------------|-------------------------------|-----------------------------------|
| Task Service           | HTTP / 8000                   | http://localhost:8000            |
| Task Service Docs      | HTTP / 8000                   | http://localhost:8000/docs       |
| Notification Service   | HTTP / 8001                   | http://localhost:8001            |
| Notification Service Docs | HTTP / 8001                | http://localhost:8001/docs       |
| RabbitMQ Management     | AMQP / 5672, HTTP / 15672     | http://localhost:15672 (guest/guest) |
| PostgreSQL              | TCP / 5432                    | Internal network                 |

---

## Testing the End-to-End Pipeline

### 1. Create a Task

```
curl -X POST "http://localhost:8000/tasks" -H "Content-Type: application/json" -d "{\"title\": \"Build Pipeline\", \"description\": \"Verify microservices messaging\"}"
```

Expected response (`200 OK`):
```json
{"id": 1, "title": "Build Pipeline", "description": "Verify microservices messaging"}
```

### 2. Update or Delete a Task

```
curl -X PUT "http://localhost:8000/tasks/1" -H "Content-Type: application/json" -d "{\"title\": \"Updated Title\"}"
curl -X DELETE "http://localhost:8000/tasks/1"
```

Each of these publishes a `TASK_UPDATED` or `TASK_DELETED` event in addition to `TASK_CREATED` on creation.

### 3. Verify Message Consumption

```
docker-compose logs notification-service
```

Expected log output:
```
[*] Consumer active and waiting for messages...
[x] Successfully processed: [TASK_CREATED] Notification processed for task #1: 'Build Pipeline'
```

---

## Running Tests Locally

### 1. Set up a virtual environment

```
python -m venv venv
```

**Windows:**
```
venv\Scripts\activate
```

**macOS/Linux:**
```
source venv/bin/activate
```

### 2. Install dependencies

```
pip install -r task-service/requirements.txt
pip install -r notification-service/requirements.txt
```

### 3. Run tests

```
pytest task-service/
pytest notification-service/
```

---

## Continuous Integration

This project uses GitHub Actions (`.github/workflows/ci.yml`) to run the test suite for both services automatically on every push and pull request to `main`.

---

## Project Structure

```
task-platform/
├── .github/
│   └── workflows/
│       └── ci.yml
├── docker-compose.yml
├── .gitignore
├── .env.example
├── task-service/
│   ├── main.py
│   ├── database.py
│   ├── models.py
│   ├── test_main.py
│   ├── Dockerfile
│   └── requirements.txt
└── notification-service/
    ├── main.py
    ├── consumer.py
    ├── database.py
    ├── models.py
    ├── test_consumer.py
    ├── Dockerfile
    └── requirements.txt
```

---

## Stopping the Services

Stop containers and remove networks:
```
docker-compose down
```

Full teardown, including persistent database volumes:
```
docker-compose down -v
```

---

## License

This project is open-source and available under the MIT License.