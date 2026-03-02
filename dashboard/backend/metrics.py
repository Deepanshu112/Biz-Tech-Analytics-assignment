from sqlalchemy.orm import Session
from datetime import datetime
from typing import List, Dict
import models
import schemas

def compute_worker_metrics(db: Session) -> List[schemas.WorkerMetrics]:
    workers = db.query(models.Worker).all()
    events = db.query(models.Event).order_by(models.Event.worker_id, models.Event.timestamp).all()
    
    worker_events = {}
    for ev in events:
        if ev.worker_id not in worker_events:
            worker_events[ev.worker_id] = []
        worker_events[ev.worker_id].append(ev)
        
    results = []
    
    for worker in workers:
        w_events = worker_events.get(worker.id, [])
        active_time = 0.0
        idle_time = 0.0
        total_units = 0
        
        for i in range(len(w_events)):
            ev = w_events[i]
            if ev.event_type == 'product_count':
                total_units += (ev.count or 0)
                
            duration = 0.0
            if i < len(w_events) - 1:
                next_ev = w_events[i+1]
                duration = (next_ev.timestamp - ev.timestamp).total_seconds()
            else:
                duration = 60.0

            if ev.event_type == 'working':
                active_time += duration
            elif ev.event_type == 'idle':
                idle_time += duration
                
        total_time = active_time + idle_time
        utilization = (active_time / total_time * 100) if total_time > 0 else 0.0
        hours_active = active_time / 3600.0
        uph = (total_units / hours_active) if hours_active > 0 else 0.0
        
        results.append(schemas.WorkerMetrics(
            worker_id=worker.id,
            name=worker.name,
            total_active_time_s=round(active_time, 2),
            total_idle_time_s=round(idle_time, 2),
            utilization_percentage=round(utilization, 2),
            total_units_produced=total_units,
            units_per_hour=round(uph, 2)
        ))
        
    return results

def compute_workstation_metrics(db: Session) -> List[schemas.WorkstationMetrics]:
    stations = db.query(models.Workstation).all()
    events = db.query(models.Event).order_by(models.Event.workstation_id, models.Event.timestamp).all()
    
    station_events = {}
    for ev in events:
        if ev.workstation_id not in station_events:
            station_events[ev.workstation_id] = []
        station_events[ev.workstation_id].append(ev)
        
    results = []
    
    for st in stations:
        st_events = station_events.get(st.id, [])
        occupancy_time = 0.0
        total_units = 0
        working_time = 0.0
        idle_time = 0.0
        
        for i in range(len(st_events)):
            ev = st_events[i]
            if ev.event_type == 'product_count':
                total_units += (ev.count or 0)
                
            duration = 0.0
            if i < len(st_events) - 1:
                next_ev = st_events[i+1]
                duration = (next_ev.timestamp - ev.timestamp).total_seconds()
            else:
                duration = 60.0

            if ev.event_type in ['working', 'idle']:
                occupancy_time += duration
            
            if ev.event_type == 'working':
                working_time += duration
            elif ev.event_type == 'idle':
                idle_time += duration
                
        utilization = (working_time / occupancy_time * 100) if occupancy_time > 0 else 0.0
        hours_occupied = occupancy_time / 3600.0
        throughput = (total_units / hours_occupied) if hours_occupied > 0 else 0.0
        
        results.append(schemas.WorkstationMetrics(
            workstation_id=st.id,
            name=st.name,
            occupancy_time_s=round(occupancy_time, 2),
            utilization_percentage=round(utilization, 2),
            total_units_produced=total_units,
            throughput_rate_per_hour=round(throughput, 2)
        ))
        
    return results

def compute_factory_metrics(db: Session) -> schemas.FactoryMetrics:
    worker_metrics = compute_worker_metrics(db)
    
    total_productive_time = sum(w.total_active_time_s for w in worker_metrics)
    total_production_count = sum(w.total_units_produced for w in worker_metrics)
    
    avg_utilization = sum(w.utilization_percentage for w in worker_metrics) / len(worker_metrics) if worker_metrics else 0.0
    avg_uph = sum(w.units_per_hour for w in worker_metrics) / len(worker_metrics) if worker_metrics else 0.0
    
    return schemas.FactoryMetrics(
        total_productive_time_s=round(total_productive_time, 2),
        total_production_count=total_production_count,
        avg_production_rate_per_hour=round(avg_uph, 2),
        avg_utilization_percentage=round(avg_utilization, 2)
    )
