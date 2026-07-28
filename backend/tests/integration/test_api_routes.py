"""
Integration tests for FastAPI REST API routes using TestClient with lifespan.
"""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from src.main import app


@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c


def test_root_endpoint(client: TestClient) -> None:
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["app"] == "DevForge"
    assert data["status"] == "online"


def test_list_packages_endpoint(client: TestClient) -> None:
    response = client.get("/api/v1/packages")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 4  # python, git, vscode, nodejs


def test_get_package_detail_endpoint(client: TestClient) -> None:
    response = client.get("/api/v1/packages/python")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == "python"
    assert data["name"] == "Python"
    assert data["category"] == "language"


def test_system_info_endpoint(client: TestClient) -> None:
    response = client.get("/api/v1/system/info")
    assert response.status_code == 200
    data = response.json()
    assert "os_name" in data
    assert "architecture" in data


def test_system_health_endpoint(client: TestClient) -> None:
    response = client.get("/api/v1/system/health")
    assert response.status_code == 200
    data = response.json()
    assert "score" in data
    assert "status" in data


def test_environment_stacks_endpoint(client: TestClient) -> None:
    response = client.get("/api/v1/environments/stacks")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 3
