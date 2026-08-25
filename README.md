# Task Platform - Event-Driven Microservices

An event-driven microservice architecture built with FastAPI, RabbitMQ, PostgreSQL, and Docker Compose.

The system consists of two primary services:
* Task Service: Manages tasks, persists data to PostgreSQL, and publishes asynchronous TASK_CREATED events to RabbitMQ.
* Notification Service: Runs a background consumer thread that listens to RabbitMQ, consuming task events asynchronously.

---

## Architecture Overview
```
[Client] ---> (POST /tasks) ---> [Task Service] ---> (Write) ---> [PostgreSQL]
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
Docker Compose will build the services and ensure postgres and rabbitmq health checks pass before launching task-service and notification-service.

### 2. Verify Container Health

Check that all containers are healthy and running:
```
docker-compose ps
```
---

## Service Endpoints
```
| Service | Protocol / Port | Base URL / Description |
|---|---|---|
| Task Service | HTTP / 8000 | http://localhost:8000 |
| Notification Service | HTTP / 8001 | http://localhost:8001 |
| RabbitMQ Management | AMQP / 5672, HTTP / 15672 | http://localhost:15672 (guest / guest) |
| PostgreSQL | TCP / 5432 | Internal network |
```
---

## Testing the End-to-End Pipeline

### Step 1: Create a Task (Task Service)

Send a POST request to task-service to create a new task:
```
curl -X POST "http://localhost:8000/tasks" -H "Content-Type: application/json" -d "{\"title\": \"Build Pipeline\", \"description\": \"Verify microservices messaging\"}"
```
Expected Response (200 OK):
```
{"id": 1, "title": "Build Pipeline", "description": "Verify microservices messaging"}
```
### Step 2: Verify Message Consumption (Notification Service)

Inspect the logs of notification-service to confirm the background thread consumed the event:
```
docker-compose logs notification-service
```
Expected Log Output:
```
[*] Consumer active and waiting for messages...
[x] Successfully processed: [TASK_CREATED] Notification processed for task #1: 'Build Pipeline'
```
---

## Project Structure
```
task-platform/
├── docker-compose.yml
├── task-service/
│   ├── main.py
│   ├── publisher.py
│   ├── Dockerfile
│   └── requirements.txt
└── notification-service/
    ├── main.py
    ├── consumer.py
    ├── Dockerfile
    └── requirements.txt
```
---

## Stopping the Services

To shut down containers and remove networks:
```
docker-compose down
```
To perform a complete teardown (including persistent database volumes):
```
docker-compose down -v
```