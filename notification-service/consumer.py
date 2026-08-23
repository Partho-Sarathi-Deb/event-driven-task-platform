import pika
import json
import os
from database import engine, SessionLocal, Base
import models

Base.metadata.create_all(bind=engine)

def process_message(ch, method, properties, body):
    data = json.loads(body.decode("utf-8"))
    payload = data.get("payload", {})
    
    db = SessionLocal()
    try:
        log_entry = models.NotificationLog(
            task_id=payload.get("id"),
            message=f"Notification sent for task: {payload.get('title')}"
        )
        db.add(log_entry)
        db.commit()
        print(f" [x] Logged notification for Task ID: {payload.get('id')}")
    finally:
        db.close()

    ch.basic_ack(delivery_tag=method.delivery_tag)

def start_consumer():
    rabbitmq_host = os.getenv("RABBITMQ_HOST", "localhost")
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=rabbitmq_host))
    channel = connection.channel()
    channel.queue_declare(queue="task_events", durable=True)
    channel.basic_consume(queue="task_events", on_message_callback=process_message)
    print(" [*] Waiting for messages...")
    channel.start_consuming()

if __name__ == "__main__":
    start_consumer()

