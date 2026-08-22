import json
import pika
import os
from database import SessionLocal, NotificationModel


def save_notification(event_type: str, task_id: int, payload_data: dict):
    db = SessionLocal()
    try:
        notification = NotificationModel(
            event_type=event_type,
            task_id=task_id,
            payload=json.dumps(payload_data)
        )
        db.add(notification)
        db.commit()
        db.refresh(notification)
        print(f"💾 [DATABASE] Saved event '{event_type}' (Record ID: {notification.id})")
    except Exception as e:
        db.rollback()
        print(f"❌ [DATABASE ERROR] Failed to save notification: {e}")
    finally:
        db.close()


def process_event(payload: dict):
    event_type = payload.get("event")
    
    # Extract task_id safely whether it's nested or flat
    task_id = payload.get("task_id") or payload.get("data", {}).get("id") or payload.get("id")
    
    print("\n" + "="*50)
    if event_type == "TASK_CREATED":
        print(f"📩 [NOTIFICATION] New Task Created! (ID: {task_id})")
    elif event_type == "TASK_UPDATED":
        print(f"🔄 [NOTIFICATION] Task Updated! (ID: {task_id})")
    elif event_type == "TASK_DELETED":
        print(f"🗑️ [NOTIFICATION] Task Deleted! (ID: {task_id})")
    else:
        print(f"⚠️ [NOTIFICATION] Unknown event type: {event_type}")
    print("="*50)

    # Persist event to SQLite database
    save_notification(event_type, task_id, payload)


def callback(ch, method, properties, body):
    try:
        payload = json.loads(body)
        print(f"📩 [NOTIFICATION] Received event: {payload}", flush=True)
        process_event(payload)
    except Exception as e:
        print(f"❌ Error processing message: {e}", flush=True)


def start_consumer():
    # Uses 'rabbitmq' inside Docker, falls back to 'localhost' if run standalone
    rabbitmq_host = os.getenv("RABBITMQ_HOST", "localhost")

    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host=rabbitmq_host)
    )
    channel = connection.channel()

    channel.exchange_declare(exchange="task_events", exchange_type="fanout")

    result = channel.queue_declare(queue="", exclusive=True)
    queue_name = result.method.queue

    channel.queue_bind(exchange="task_events", queue=queue_name)

    print(f" [*] Notification Service connected to {rabbitmq_host}. Listening for events...")

    channel.basic_consume(
        queue=queue_name, on_message_callback=callback, auto_ack=True
    )
    channel.start_consuming()

if __name__ == "__main__":
    try:
        start_consumer()
    except KeyboardInterrupt:
        print("\nStopping Notification Service consumer...")
