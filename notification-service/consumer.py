import json
import pika
from database import SessionLocal, NotificationModel

def save_notification(event_type: str, data: dict):
    db = SessionLocal()
    try:
        notification = NotificationModel(
            event_type=event_type,
            task_id=data.get("id"),
            payload=json.dumps(data)
        )
        db.add(notification)
        db.commit()
        db.refresh(notification)
        print(f"💾 [DATABASE] Saved event '{event_type}' to DB (Record ID: {notification.id})")
    except Exception as e:
        db.rollback()
        print(f"❌ [DATABASE ERROR] Failed to save notification: {e}")
    finally:
        db.close()

def process_event(event_type: str, data: dict):
    print("\n" + "="*50)
    if event_type == "TASK_CREATED":
        print(f"📩 [NOTIFICATION] New Task Created! (ID: {data.get('id')})")
    elif event_type == "TASK_UPDATED":
        print(f"🔄 [NOTIFICATION] Task Updated! (ID: {data.get('id')})")
    elif event_type == "TASK_DELETED":
        print(f"🗑️ [NOTIFICATION] Task Deleted! (ID: {data.get('id')})")
    else:
        print(f"⚠️ [NOTIFICATION] Unknown event type: {event_type}")
    print("="*50)

    # Persist event to SQLite
    save_notification(event_type, data)

def callback(ch, method, properties, body):
    try:
        payload = json.loads(body)
        event_type = payload.get("event")
        data = payload.get("data", {})
        process_event(event_type, data)
    except Exception as e:
        print(f"Error processing message: {e}")

def start_consumer():
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host="localhost")
    )
    channel = connection.channel()

    channel.exchange_declare(exchange="task_events", exchange_type="fanout")

    result = channel.queue_declare(queue="", exclusive=True)
    queue_name = result.method.queue

    channel.queue_bind(exchange="task_events", queue=queue_name)

    print(" [*] Notification Service running. Listening and saving events...")
    
    channel.basic_consume(
        queue=queue_name, on_message_callback=callback, auto_ack=True
    )
    channel.start_consuming()

if __name__ == "__main__":
    try:
        start_consumer()
    except KeyboardInterrupt:
        print("\nStopping Notification Service consumer...")
