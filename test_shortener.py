import pytest
from shortener import app, url_store, reverse_store


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        url_store.clear()
        reverse_store.clear()
        yield client


def test_shorten_valid_url(client):
    resp = client.post("/shorten", json={"url": "https://example.com"})
    assert resp.status_code == 201
    data = resp.get_json()
    assert "short_code" in data
    assert len(data["short_code"]) == 6
    assert data["original_url"] == "https://example.com"


def test_shorten_deduplication(client):
    r1 = client.post("/shorten", json={"url": "https://example.com"})
    r2 = client.post("/shorten", json={"url": "https://example.com"})
    assert r1.get_json()["short_code"] == r2.get_json()["short_code"]


def test_shorten_missing_url(client):
    resp = client.post("/shorten", json={})
    assert resp.status_code == 400


def test_shorten_empty_url(client):
    resp = client.post("/shorten", json={"url": ""})
    assert resp.status_code == 400


def test_shorten_invalid_url(client):
    resp = client.post("/shorten", json={"url": "not-a-url"})
    assert resp.status_code == 400


def test_shorten_ftp_rejected(client):
    resp = client.post("/shorten", json={"url": "ftp://files.example.com"})
    assert resp.status_code == 400


def test_shorten_url_too_long(client):
    resp = client.post("/shorten", json={"url": "https://example.com/" + "a" * 2050})
    assert resp.status_code == 400


def test_redirect(client):
    r = client.post("/shorten", json={"url": "https://example.com"})
    code = r.get_json()["short_code"]
    resp = client.get(f"/{code}")
    assert resp.status_code == 302
    assert resp.headers["Location"] == "https://example.com"


def test_redirect_not_found(client):
    assert client.get("/nonexistent").status_code == 404


def test_redirect_invalid_code(client):
    assert client.get("/bad!code").status_code == 400


def test_stats(client):
    r = client.post("/shorten", json={"url": "https://example.com"})
    code = r.get_json()["short_code"]
    resp = client.get(f"/stats/{code}")
    assert resp.status_code == 200
    assert resp.get_json()["original_url"] == "https://example.com"


def test_stats_not_found(client):
    assert client.get("/stats/nope").status_code == 404


def test_health(client):
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.get_json()["status"] == "ok"


def test_no_json_body(client):
    resp = client.post("/shorten", data="not json")
    assert resp.status_code == 400
