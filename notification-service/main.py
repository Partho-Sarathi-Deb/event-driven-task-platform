import threading
from contextlib import asynccontextmanager
from fastapi import FastAPI
from consumer import start_consumer


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Launch consumer in a non-blocking background thread
    consumer_thread = threading.Thread(target=start_consumer, daemon=True)
    consumer_thread.start()
    print("[*] Background RabbitMQ consumer thread started.")
    yield


app = FastAPI(title="Notification Service", lifespan=lifespan)


@app.get("/health")
def health_check():
    return {"status": "healthy"}
