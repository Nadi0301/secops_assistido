import pytest
from fastapi.testclient import TestClient
from src.api.main import app
from src.core.database import init_db, get_db
from src.core.secops_core import run_unified_pipeline

client = TestClient(app)

def setup_module(module):
    init_db()

def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["status"] == "online"

def test_get_logs():
    response = client.get("/logs")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_unified_pipeline():
    results = run_unified_pipeline()
    assert "volumetric_anomalies" in results
    assert "multivariate_anomalies" in results
