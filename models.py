
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Float, Text, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os

Base = declarative_base()

class Business(Base):
    __tablename__ = 'businesses'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    phone = Column(String(50))
    address = Column(Text)
    category = Column(String(100))
    rating = Column(Float)
    reviews_count = Column(Integer)
    website = Column(String(255))
    created_at = Column(DateTime, default=datetime.now)
    scraped_keyword = Column(String(100))
    
class MessageLog(Base):
    __tablename__ = 'message_logs'
    
    id = Column(Integer, primary_key=True)
    business_id = Column(Integer)
    business_name = Column(String(255))
    phone = Column(String(50))
    message_sent = Column(Boolean, default=False)
    sent_at = Column(DateTime)
    error_message = Column(Text)
    created_at = Column(DateTime, default=datetime.now)

class ScrapingSession(Base):
    __tablename__ = 'scraping_sessions'
    
    id = Column(Integer, primary_key=True)
    keyword = Column(String(100))
    total_found = Column(Integer)
    successful_scrapes = Column(Integer)
    started_at = Column(DateTime, default=datetime.now)
    completed_at = Column(DateTime)
    status = Column(String(50), default='running')

# Database setup
from config import get_config

config = get_config()
DATABASE_URL = config.DATABASE_URL
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    os.makedirs('data', exist_ok=True)
    Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
