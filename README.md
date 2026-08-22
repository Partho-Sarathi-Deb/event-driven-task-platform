# Event-Driven Microservices Task Platform

A decoupled, event-driven microservices backend built with Python, FastAPI, RabbitMQ, and SQLAlchemy.

---

## 🏗️ Architecture Overview

* **Task Service (REST API):** Manages task lifecycles (CRUD operations) using FastAPI and SQLite. Publishes events (`TASK_CREATED`, `TASK_UPDATED`, `TASK_DELETED`) to RabbitMQ upon state changes.
* **Message Broker (RabbitMQ):** Implements a `fanout` exchange (`task_events`) for asynchronous message passing and service decoupling.
* **Notification Service (Consumer):** Listens for task events in real-time and persists audit logs into an independent SQLite database.

---

## 🛠️ Tech Stack

* **Framework:** FastAPI, Python 3.10+
* **Messaging:** RabbitMQ, Pika
* **ORM & Database:** SQLAlchemy, SQLite
* **Architecture:** Microservices, Event-Driven Architecture (EDA), Publish-Subscribe Pattern

---

## 🚀 Getting Started

### Prerequisites

* [Docker Desktop](https://www.docker.com/) (for running RabbitMQ)
* Python 3.10+

### 1. Start RabbitMQ Container

docker run -d --name rabbitmq -p 5672:5672 -p 15672:15672 rabbitmq:3-management

### 2. Run Task Service

cd task-service
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8000

### 3. Run Notification Service

cd notification-service
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python consumer.py
