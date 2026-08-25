import json
import time
import pika
import os

RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "rabbitmq")

def process_message(body: bytes) -> dict:
    """Parses incoming RabbitMQ byte payload matching task-service schema."""
    data = json.loads(body.decode("utf-8"))
    
    event_type = data.get("event_type", "UNKNOWN_EVENT")
    payload = data.get("payload", {})
    
    # Handle both nested payload.id and flat task_id for backward compatibility
    task_id = payload.get("id") or data.get("task_id")
    title = payload.get("title") or data.get("title", "Untitled Task")
    
    if not task_id:
        raise ValueError("Invalid message payload: missing task ID")
        
    message = f"[{event_type}] Notification processed for task #{task_id}: '{title}'"
    return {
        "event_type": event_type,
        "task_id": task_id,
        "title": title,
        "message": message
    }

def start_consumer():
    """Establishes active RabbitMQ connection and starts consumption loop."""
    # Retries loop for startup container synchronization
    connection = None
    for _ in range(10):
        try:
            connection = pika.BlockingConnection(pika.ConnectionParameters(host=RABBITMQ_HOST))
            break
        except pika.exceptions.AMQPConnectionError:
            time.sleep(3)

    if not connection:
        print("[!] Failed to connect to RabbitMQ after retries.")
        return

    channel = connection.channel()
    channel.queue_declare(queue="task_events", durable=True)

    def callback(ch, method, properties, body):
        try:
            notification = process_message(body)
            print(f"[x] Successfully processed: {notification['message']}")
            ch.basic_ack(delivery_tag=method.delivery_tag)
        except Exception as e:
            print(f"[!] Processing failed: {e}")
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)

    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue="task_events", on_message_callback=callback)
    print("[*] Consumer active and waiting for messages...")
    channel.start_consuming()
