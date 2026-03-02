import pytest
from fastapi.testclient import TestClient

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import app
from database import init_db

client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_db():
    init_db()

def test_seed_api():
    response = client.post("/api/seed")
    assert response.status_code == 200
    assert "generated successfully" in response.json()["message"]

def test_get_factory_metrics():
    response = client.get("/api/metrics/factory")
    assert response.status_code == 200
    data = response.json()
    assert "total_productive_time_s" in data
    assert "total_production_count" in data

def test_create_event():
    payload = {
        "timestamp": "2026-01-15T10:15:00Z",
        "worker_id": "W1",
        "workstation_id": "S1",
        "event_type": "working",
        "confidence": 0.95,
        "count": 0
    }
    response = client.post("/api/events", json=payload)
    assert response.status_code == 200
    assert response.json()["worker_id"] == "W1"
    
def test_get_worker_metrics():
    response = client.get("/api/metrics/workers")
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0 # assuming db is seeded
    assert "total_active_time_s" in data[0]
