def test_health(client):
    """Test health check endpoint for status, uptime and version"""
    response = client.get("/health")
    assert response.status_code == 200

    data = response.json()
    assert data["status"] == "ok"
    assert "version" in data
    assert "uptime" in data
    assert isinstance(data["uptime"], float)
