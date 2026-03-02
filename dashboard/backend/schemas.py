from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional

class EventCreate(BaseModel):
    timestamp: datetime
    worker_id: str
    workstation_id: str
    event_type: str
    confidence: float
    count: Optional[int] = 0

class EventResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    timestamp: datetime
    worker_id: str
    workstation_id: str
    event_type: str
    confidence: float
    count: int

class WorkerMetrics(BaseModel):
    worker_id: str
    name: str
    total_active_time_s: float
    total_idle_time_s: float
    utilization_percentage: float
    total_units_produced: int
    units_per_hour: float

class WorkstationMetrics(BaseModel):
    workstation_id: str
    name: str
    occupancy_time_s: float
    utilization_percentage: float
    total_units_produced: int
    throughput_rate_per_hour: float

class FactoryMetrics(BaseModel):
    total_productive_time_s: float
    total_production_count: int
    avg_production_rate_per_hour: float
    avg_utilization_percentage: float
