import pytest
from httpx import AsyncClient, ASGITransport
import tempfile
import os

from app.main import app
import app.models as models

@pytest.fixture(autouse=True)
def setup_test_db(monkeypatch):
    """Create a temporary SQLite database for test isolation."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp_file:
        test_db_path = tmp_file.name

    monkeypatch.setattr(models, "DB_PATH", test_db_path)
    models.init_db()

    yield test_db_path

    if os.path.exists(test_db_path):
        os.remove(test_db_path)

@pytest.mark.anyio
async def test_health_check():
    """Verify container readiness / healthz endpoint."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/healthz")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "guestbook-app"

@pytest.mark.anyio
async def test_render_homepage():
    """Verify GET / renders homepage HTML."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/")
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]
        assert "Guestbook" in response.text
        # Security headers
        assert response.headers.get("x-content-type-options") == "nosniff"
        assert response.headers.get("x-frame-options") == "DENY"

@pytest.mark.anyio
async def test_submit_valid_entry():
    """Verify POST /entries records entry and redirects."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post(
            "/entries",
            data={
                "name": "Alice Developer",
                "email": "alice@example.com",
                "message": "Hello from Cloud Run test!"
            },
            follow_redirects=False
        )
        assert response.status_code == 303
        assert response.headers["location"] == "/?success=true"

        # Check API returns the created entry
        api_response = await client.get("/api/v1/entries")
        assert api_response.status_code == 200
        entries = api_response.json()
        assert len(entries) == 1
        assert entries[0]["name"] == "Alice Developer"
        assert entries[0]["message"] == "Hello from Cloud Run test!"

@pytest.mark.anyio
async def test_xss_sanitization():
    """Verify malicious script tags are escaped."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        malicious_name = "<script>alert('xss')</script>"
        malicious_message = "<img src=x onerror=alert('hack')>"

        await client.post(
            "/entries",
            data={
                "name": malicious_name,
                "email": "security@example.com",
                "message": malicious_message
            },
            follow_redirects=False
        )

        api_res = await client.get("/api/v1/entries")
        entries = api_res.json()
        assert len(entries) == 1
        assert "<script>" not in entries[0]["name"]
        assert "&lt;script&gt;" in entries[0]["name"]
        assert "<img" not in entries[0]["message"]
        assert "&lt;img" in entries[0]["message"]

@pytest.mark.anyio
async def test_invalid_email_validation():
    """Verify invalid email returns HTTP 422 with validation error."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post(
            "/entries",
            data={
                "name": "Bob",
                "email": "not-an-email",
                "message": "Test message"
            },
            follow_redirects=False
        )
        assert response.status_code == 422
        assert "Validation Error" in response.text

@pytest.mark.anyio
async def test_empty_fields_validation():
    """Verify missing / empty required fields return HTTP 422."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post(
            "/entries",
            data={
                "name": "",
                "email": "valid@example.com",
                "message": ""
            },
            follow_redirects=False
        )
        assert response.status_code == 422
