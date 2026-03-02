from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import List
import random

import models
import schemas
import database
import metrics

app = FastAPI(title="AI Productivity Dashboard API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def on_startup():
    database.init_db()
    db = next(database.get_db())
    try:
        workers_count = db.query(models.Worker).count()
        if workers_count == 0:
            seed_data_internal(db)
    finally:
        db.close()

def seed_data_internal(db: Session):
    print("Seeding database...")

    workers = [
        models.Worker(id=f"W{i}", name=f"Worker {i}") for i in range(1, 7)
    ]
    stations = [
        models.Workstation(id=f"S{i}", name=f"Station {i}", type="Assembly") for i in range(1, 7)
    ]
    db.add_all(workers)
    db.add_all(stations)
    db.commit()
    
    current_time = datetime.utcnow() - timedelta(hours=2)
    event_types = ["working", "idle", "absent"]
    
    for i in range(120): 
        w = f"W{random.randint(1, 6)}"
        s = f"S{random.randint(1, 6)}"
        e_type = random.choices(event_types, weights=(0.7, 0.2, 0.1))[0]
        
        db.add(models.Event(
            timestamp=current_time,
            worker_id=w,
            workstation_id=s,
            event_type=e_type,
            confidence=round(random.uniform(0.7, 0.99), 2),
            count=0
        ))
        
        if e_type == "working" and random.random() > 0.6:
            db.add(models.Event(
                timestamp=current_time + timedelta(seconds=15),
                worker_id=w,
                workstation_id=s,
                event_type="product_count",
                confidence=round(random.uniform(0.7, 0.99), 2),
                count=random.randint(1, 3)
            ))
            
        current_time += timedelta(minutes=1)
        
    db.commit()

@app.post("/api/seed")
def seed_data(db: Session = Depends(database.get_db)):
   
    db.query(models.Event).delete()
    db.query(models.Worker).delete()
    db.query(models.Workstation).delete()
    db.commit()
    seed_data_internal(db)
    return {"message": "Data generated successfully."}

@app.post("/api/events", response_model=schemas.EventResponse)
def create_event(event: schemas.EventCreate, db: Session = Depends(database.get_db)):
    db_event = models.Event(**event.model_dump())
    db.add(db_event)
    db.commit()
    db.refresh(db_event)
    return db_event

@app.get("/api/metrics/factory", response_model=schemas.FactoryMetrics)
def get_factory_metrics(db: Session = Depends(database.get_db)):
    return metrics.compute_factory_metrics(db)

@app.get("/api/metrics/workers", response_model=List[schemas.WorkerMetrics])
def get_worker_metrics(db: Session = Depends(database.get_db)):
    return metrics.compute_worker_metrics(db)

@app.get("/api/metrics/workstations", response_model=List[schemas.WorkstationMetrics])
def get_workstation_metrics(db: Session = Depends(database.get_db)):
    return metrics.compute_workstation_metrics(db)
