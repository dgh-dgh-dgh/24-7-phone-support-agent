from fastapi.testclient import TestClient

from app.main import app, spoken_time

client = TestClient(app)


def test_health():
    assert client.get("/health").json() == {"status": "ok"}


def test_city_match_is_case_insensitive(monkeypatch):
    monkeypatch.delenv("WEBHOOK_SECRET", raising=False)
    body = client.get("/screenings", params={"city": "austin"}).json()
    assert body["count"] == 2
    assert body["summary"].startswith("There are 2 screenings in austin")


def test_no_match_returns_spoken_message(monkeypatch):
    monkeypatch.delenv("WEBHOOK_SECRET", raising=False)
    body = client.get("/screenings", params={"city": "Valencia"}).json()
    assert body["count"] == 0
    assert "couldn't find" in body["summary"]


def test_missing_city_is_rejected():
    assert client.get("/screenings").status_code == 422


def test_secret_required_when_configured(monkeypatch):
    monkeypatch.setenv("WEBHOOK_SECRET", "s3cret")
    assert client.get("/screenings", params={"city": "Austin"}).status_code == 401
    ok = client.get("/screenings", params={"city": "Austin"}, headers={"X-Api-Key": "s3cret"})
    assert ok.status_code == 200


def test_spoken_time():
    assert spoken_time("2026-12-04T19:30") == "Friday, December 4 at 7:30 PM"
