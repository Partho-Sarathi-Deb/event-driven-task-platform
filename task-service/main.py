import json
import pika
import os
import models
from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel, ConfigDict
from sqlalchemy import create_engine, Column, Integer, String, Boolean
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from database import engine, Base, get_db

Base.metadata.create_all(bind=engine)

app = FastAPI()

# 1. SQLite Database Connection Setup
DATABASE_URL = "sqlite:///./tasks.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


# 2. Database Models
class TaskModel(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(String, nullable=True)
    completed = Column(Boolean, default=False)


Base.metadata.create_all(bind=engine)


# 3. Pydantic Schemas
class TaskCreate(BaseModel):
    title: str
    description: str | None = None


class TaskResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    title: str
    description: str | None = None
    completed: bool


class TaskUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    completed: bool | None = None


# 4. FastAPI Setup & Dependencies
app = FastAPI(title="TaskService")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def publish_event(event_type: str, data: dict):
    try:
        rabbitmq_host = os.getenv("RABBITMQ_HOST", "localhost")
        connection = pika.BlockingConnection(
            pika.ConnectionParameters(host="rabbitmq_host")
        )
        channel = connection.channel()

        # Declare fanout exchange named 'task_events'
        channel.exchange_declare(exchange="task_events", exchange_type="fanout")

        message = json.dumps({"event_type": event_type, "data": data, "payload": payload})
        channel.basic_publish(exchange="", routing_key="task_events", body=message)

        connection.close()
    except Exception as e:
        print(f"Failed to publish event to RabbitMQ: {e}")


# 5. REST API Endpoints
@app.post("/tasks")
def create_task(title: str, description: str = None, db: Session = Depends(get_db)):
    db_task = models.Task(title=title, description=description)
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    
    # Publish event after DB insertion
    publish_event("task_created", {"id": db_task.id, "title": db_task.title})
    return db_task


@app.get("/tasks")
def list_tasks(db: Session = Depends(get_db)):
    return db.query(models.Task).all()


@app.get("/tasks/{task_id}", response_model=TaskResponse)
def get_task(task_id: int, db: Session = Depends(get_db)):
    task = db.query(TaskModel).filter(TaskModel.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@app.put("/tasks/{task_id}", response_model=TaskResponse)
def update_task(
    task_id: int, task_data: TaskUpdate, db: Session = Depends(get_db)
):
    db_task = db.query(TaskModel).filter(TaskModel.id == task_id).first()
    if not db_task:
        raise HTTPException(status_code=404, detail="Task not found")

    update_dict = task_data.model_dump(exclude_unset=True)
    for key, value in update_dict.items():
        setattr(db_task, key, value)

    db.commit()
    db.refresh(db_task)

    event_payload = {
        "id": db_task.id,
        "title": db_task.title,
        "description": db_task.description,
        "completed": db_task.completed,
    }
    publish_event("TASK_UPDATED", event_payload)
    return db_task


@app.delete("/tasks/{task_id}", status_code=200)
def delete_task(task_id: int, db: Session = Depends(get_db)):
    db_task = db.query(TaskModel).filter(TaskModel.id == task_id).first()
    if not db_task:
        raise HTTPException(status_code=404, detail="Task not found")

    event_payload = {"id": db_task.id, "title": db_task.title}

    db.delete(db_task)
    db.commit()

    # Publish event using unified publish_event function
    publish_event("TASK_DELETED", event_payload)

    return {"message": f"Task {task_id} deleted successfully"}

