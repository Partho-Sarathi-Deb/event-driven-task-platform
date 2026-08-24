# Event-Driven Task Management Platform

An event-driven microservices platform built with **FastAPI**, **PostgreSQL**, **RabbitMQ**, and **Docker**. Designed with clean architecture, containerized isolation, asynchronous messaging, and automated CI pipelines.

---

## Architecture Overview

* **Task Service (FastAPI + PostgreSQL):** REST API for managing tasks. Publishes event payloads (`TASK_CREATED`, `TASK_UPDATED`, `TASK_DELETED`) to RabbitMQ upon database modifications.
* **Notification Service (FastAPI + PostgreSQL):** Asynchronous background consumer that listens to RabbitMQ queues and logs task events into an audit log database.
* **Message Broker (RabbitMQ):** Facilitates decoupled, asynchronous communication between microservices.
* **Database (PostgreSQL):** Persistent relational storage for tasks and event logs.

---

## Tech Stack
```
| Component | Technology |
| --- | --- |
| **Language** | Python 3.12 |
| **Framework** | FastAPI, Uvicorn |
| **Database** | PostgreSQL, SQLAlchemy (ORM) |
| **Messaging** | RabbitMQ, Pika |
| **Containerization** | Docker, Docker Compose |
| **Testing & CI** | Pytest, GitHub Actions |
```
---

## Project Structure
```
task-platform/
├── .github/
│   └── workflows/
│       └── ci.yml
├── task-service/
│   ├── database.py
│   ├── main.py
│   ├── models.py
│   ├── requirements.txt
│   └── test_main.py
├── notification-service/
│   ├── database.py
│   ├── main.py
│   ├── models.py
│   ├── requirements.txt
│   └── test_main.py
├── docker-compose.yml
└── README.md
```
---

## Getting Started

### Prerequisites
* Docker Desktop installed and running
* Git

### Running with Docker Compose

1. Clone the repository:
   git clone https://github.com/YOUR_USERNAME/YOUR_REPOSITORY_NAME.git
   cd task-platform

2. Build and start all services:
   docker-compose up --build

3. Access Interactive API Docs (Swagger UI):
   * Task Service: http://localhost:8000/docs
   * Notification Service: http://localhost:8001/docs
   * RabbitMQ Management Dashboard: http://localhost:15672 (Guest / Guest)

---

## Local Development & Testing

### Running Tests Locally

1. Set up a virtual environment:
   python -m venv venv
   # On Windows:
   .\venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate

2. Install dependencies:
   pip install -r task-service/requirements.txt
   pip install -r notification-service/requirements.txt

3. Run tests via pytest:
   pytest task-service/
   pytest notification-service/

---

## Continuous Integration (CI)

This project uses GitHub Actions to automate unit testing on every push or pull request to the main branch. 

Workflows run isolated unit tests using an in-memory SQLite configuration and mock messaging interfaces to ensure reliability across builds.

---

## License

This project is open-source and available under the MIT License.
