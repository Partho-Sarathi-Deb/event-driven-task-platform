from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime

DATABASE_URL = "sqlite:///./notifications.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class NotificationModel(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    event_type = Column(String, nullable=False)
    task_id = Column(Integer, nullable=True)
    payload = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

# Initialize database table
Base.metadata.create_all(bind=engine)
