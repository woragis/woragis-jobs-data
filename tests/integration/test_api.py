"""
Integration tests for API endpoints
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app


@pytest.mark.integration
def test_health_check():
    """Test health check endpoint"""
    client = TestClient(app)
    response = client.get("/healthz")
    
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

