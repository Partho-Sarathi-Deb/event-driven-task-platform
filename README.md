# Event-Driven Task Management Platform

An event-driven microservices platform built with FastAPI, RabbitMQ, PostgreSQL, and Docker Compose.

## Architecture Overview
```
+-----------------------+
|     task-service      | (FastAPI)
+-----------+-----------+
            | Publishes Events
            v
+-----------------------+
|       RabbitMQ        | (Exchange: task_events)
+-----------+-----------+
            | Consumes Events
            v
+-----------------------+
| notification-service  | (Consumer)
+-----------+-----------+
            | Persists Audit Logs
            v
+-----------------------+
|      PostgreSQL       | (Database)
+-----------------------+
```
* task-service: Handles CRUD operations for tasks and emits events (task_created, task_updated, task_deleted) to RabbitMQ.
* rabbitmq: Acts as the message broker, broadcasting events via fanout exchange.
* notification-service: Background worker consuming events and persisting audit logs to PostgreSQL.
* postgres: Central relational database storage.

---

## Quick Start (Docker)

### Prerequisites
* Docker Desktop installed and running.

### 1. Run the Application
Spin up all microservices, message broker, and database with a single command:

docker-compose up --build

### 2. Verify Services

| Service | Endpoint / Access | Description |
| :--- | :--- | :--- |
| Task API Docs | http://localhost:8000/docs | Interactive Swagger UI |
| RabbitMQ Management | http://localhost:15672 | User: guest / Pass: guest |
| PostgreSQL | localhost:5432 | User: app_user / DB: task_platform |

---

## Testing Event Flow

Create a new task via curl to trigger an asynchronous RabbitMQ event:

curl -X POST http://localhost:8000/tasks -H "Content-Type: application/json" -d "{\"title\": \"Build README\", \"description\": \"Document the docker setup\"}"

Check the notification-service logs to confirm event consumption:

docker-compose logs notification-service --tail 20

---

## Repository Structure
```
├── docker-compose.yml
├── task-service/
│   ├── main.py
│   ├── Dockerfile
│   └── requirements.txt
└── notification-service/
    ├── consumer.py
    ├── Dockerfile
    └── requirements.txt
```
