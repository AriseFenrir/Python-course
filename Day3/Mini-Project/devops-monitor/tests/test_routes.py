"""Route tests for the FastAPI application."""

import pytest
from fastapi.testclient import TestClient

from api.main import app, servers

client = TestClient(app)

API_KEY = "dev-secret-key"


@pytest.fixture(autouse=True)
def clear_servers():
    """Clear the server store before each test."""
    servers.clear()
    yield
    servers.clear()


def test_health_returns_ok():
    """GET /health should return 200 with status ok."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_metrics_returns_cpu_percent():
    """GET /metrics should return 200 and include cpu_percent."""
    response = client.get("/metrics")
    assert response.status_code == 200
    assert "cpu_percent" in response.json()


def test_post_servers_without_key_returns_403():
    """POST /servers without API key should return 403."""
    response = client.post(
        "/servers", json={"name": "test", "host": "localhost", "port": 8080}
    )
    assert response.status_code == 403


def test_post_servers_with_key_returns_201():
    """POST /servers with valid API key should return 201."""
    response = client.post(
        "/servers",
        json={"name": "test-server", "host": "localhost", "port": 8080},
        headers={"X-API-Key": API_KEY},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "test-server"
    assert data["host"] == "localhost"
    assert data["port"] == 8080
    assert data["status"] == "unknown"
    assert "id" in data


def test_created_server_appears_in_list():
    """A server created via POST should appear in GET /servers."""
    client.post(
        "/servers",
        json={"name": "listed-server", "host": "10.0.0.1", "port": 3000},
        headers={"X-API-Key": API_KEY},
    )
    response = client.get("/servers")
    assert response.status_code == 200
    server_names = [s["name"] for s in response.json()]
    assert "listed-server" in server_names


def test_get_nonexistent_server_returns_404():
    """GET /servers/{nonexistent_id} should return 404."""
    response = client.get("/servers/nonexistent-id-12345")
    assert response.status_code == 404


def test_delete_server_requires_api_key():
    """DELETE /servers/{id} without API key should return 403."""
    # First create a server
    resp = client.post(
        "/servers",
        json={"name": "to-delete", "host": "localhost", "port": 9090},
        headers={"X-API-Key": API_KEY},
    )
    server_id = resp.json()["id"]
    # Try deleting without key
    response = client.delete(f"/servers/{server_id}")
    assert response.status_code == 403


def test_delete_server_with_key():
    """DELETE /servers/{id} with valid key should return 204."""
    resp = client.post(
        "/servers",
        json={"name": "to-delete", "host": "localhost", "port": 9090},
        headers={"X-API-Key": API_KEY},
    )
    server_id = resp.json()["id"]
    response = client.delete(
        f"/servers/{server_id}", headers={"X-API-Key": API_KEY}
    )
    assert response.status_code == 204


def test_filter_servers_by_status():
    """GET /servers?status=UP should filter results."""
    response = client.get("/servers?status=UP")
    assert response.status_code == 200
    assert response.json() == []


def test_post_server_invalid_port():
    """POST /servers with invalid port should return 422."""
    response = client.post(
        "/servers",
        json={"name": "bad-port", "host": "localhost", "port": 99999},
        headers={"X-API-Key": API_KEY},
    )
    assert response.status_code == 422
