from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


def test_health():
    """Test health check endpoint for status, uptime and version"""
    response = client.get("/health")
    assert response.status_code == 200

    data = response.json()
    assert data["status"] == "ok"
    assert "version" in data
    assert "uptime" in data
    assert isinstance(data["uptime"], float)
