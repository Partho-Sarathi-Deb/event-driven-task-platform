import json
import os
import pika
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel, ConfigDict
from sqlalchemy.orm import Session

from database import engine, Base, get_db
import models

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Only create tables on real app startup (not during pytest imports)
    Base.metadata.create_all(bind=engine)
    yield

app = FastAPI(title="TaskService", lifespan=lifespan)

# Pydantic Schemas
class TaskCreate(BaseModel):
    title: str
    description: str | None = None

class TaskResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    title: str
    description: str | None = None

class TaskUpdate(BaseModel):
    title: str | None = None
    description: str | None = None

def publish_event(event_type: str, payload: dict):
    rabbitmq_host = os.getenv("RABBITMQ_HOST", "localhost")
    try:
        connection = pika.BlockingConnection(pika.ConnectionParameters(host=rabbitmq_host))
        channel = connection.channel()
        channel.queue_declare(queue="task_events", durable=True)
        message = json.dumps({"event_type": event_type, "payload": payload})
        channel.basic_publish(exchange="", routing_key="task_events", body=message)
        connection.close()
    except Exception as e:
        print(f"Failed to publish event to RabbitMQ: {e}")

# REST API Endpoints
@app.post("/tasks", response_model=TaskResponse)
def create_task(task_data: TaskCreate, db: Session = Depends(get_db)):
    db_task = models.Task(title=task_data.title, description=task_data.description)
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    
    publish_event("TASK_CREATED", {"id": db_task.id, "title": db_task.title})
    return db_task

@app.get("/tasks")
def list_tasks(db: Session = Depends(get_db)):
    return db.query(models.Task).all()

@app.get("/tasks/{task_id}", response_model=TaskResponse)
def get_task(task_id: int, db: Session = Depends(get_db)):
    task = db.query(models.Task).filter(models.Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

@app.put("/tasks/{task_id}", response_model=TaskResponse)
def update_task(task_id: int, task_data: TaskUpdate, db: Session = Depends(get_db)):
    db_task = db.query(models.Task).filter(models.Task.id == task_id).first()
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
    }
    publish_event("TASK_UPDATED", event_payload)
    return db_task

@app.delete("/tasks/{task_id}", status_code=200)
def delete_task(task_id: int, db: Session = Depends(get_db)):
    db_task = db.query(models.Task).filter(models.Task.id == task_id).first()
    if not db_task:
        raise HTTPException(status_code=404, detail="Task not found")

    event_payload = {"id": db_task.id, "title": db_task.title}
    db.delete(db_task)
    db.commit()

    publish_event("TASK_DELETED", event_payload)
    return {"message": f"Task {task_id} deleted successfully"}
