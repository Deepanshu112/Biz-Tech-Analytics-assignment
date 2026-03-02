from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class Worker(Base):
    __tablename__ = "workers"
    id = Column(String, primary_key=True, index=True)
    name = Column(String)

class Workstation(Base):
    __tablename__ = "workstations"
    id = Column(String, primary_key=True, index=True)
    name = Column(String)
    type = Column(String)

class Event(Base):
    __tablename__ = "events"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    timestamp = Column(DateTime, index=True)
    worker_id = Column(String, index=True)
    workstation_id = Column(String, index=True)
    event_type = Column(String, index=True)
    confidence = Column(Float)
    count = Column(Integer, default=0)
