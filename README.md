# Event-Driven Microservices Task Platform

A decoupled, event-driven microservices backend built with Python, FastAPI, RabbitMQ, and SQLAlchemy.

## 🏗 Architecture Overview

- **Task Service (REST API):** Manages task lifecycle (CRUD operations) using FastAPI and SQLite. Publishes events (`TASK_CREATED`, `TASK_UPDATED`, `TASK_DELETED`) to RabbitMQ upon state changes.
- **Message Broker (RabbitMQ):** Implements a `fanout` exchange (`task_events`) for asynchronous message passing and decoupling.
- **Notification Service (Consumer):** Listens for task events in real-time and persists full audit event logs into an independent SQLite database.

## 🛠 Tech Stack

- **Framework:** FastAPI, Python 3.x
- **Messaging:** RabbitMQ, Pika
- **ORM & Database:** SQLAlchemy, SQLite
- **Architecture:** Microservices, Event-Driven Architecture (EDA), Publish-Subscribe Pattern

## 🚀 Getting Started

### Prerequisites
- Docker Desktop (for running RabbitMQ)
- Python 3.10+

### Running the Application

1. **Start RabbitMQ:**
   ```bash
   docker run -d --name rabbitmq -p 5672:5672 -p 15672:15672 rabbitmq:3-management

### Running Task Service

cd task-service
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8000

### Running Notification Service

cd notification-service
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python consumer.py

---

### Step 2: Generate `requirements.txt` Files

Run these two commands so the `pip install -r requirements.txt` step actually works for anyone cloning your repository:

1. **In Terminal 1 (`task-service` with active `venv`):**
   ```cmd
   pip freeze > requirements.txt