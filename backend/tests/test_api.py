from fastapi.testclient import TestClient
from app.main import app
from app.utils.helpers import is_valid_youtube_url, format_duration

client = TestClient(app)


def test_root_endpoint():
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "online"
    assert "YouTube Downloader API" in data["service"]


def test_url_validation_helper():
    valid_urls = [
        "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
        "https://youtu.be/dQw4w9WgXcQ",
        "https://m.youtube.com/watch?v=dQw4w9WgXcQ",
        "https://www.youtube.com/shorts/dQw4w9WgXcQ",
        "https://music.youtube.com/watch?v=dQw4w9WgXcQ",
    ]
    invalid_urls = [
        "https://google.com",
        "https://vimeo.com/123456",
        "not_a_url",
        "",
        "https://youtube.com/invalid_path"
    ]
    for url in valid_urls:
        assert is_valid_youtube_url(url) is True, f"Deveria aceitar: {url}"

    for url in invalid_urls:
        assert is_valid_youtube_url(url) is False, f"Deveria rejeitar: {url}"


def test_format_duration_helper():
    assert format_duration(0) == "00:00"
    assert format_duration(65) == "01:05"
    assert format_duration(3665) == "01:01:05"
    assert format_duration(None) == "N/A"


def test_info_invalid_url():
    response = client.get("/api/info?url=https://google.com")
    assert response.status_code == 400
    data = response.json()
    assert "inválida" in data["detail"].lower()


def test_download_invalid_url():
    response = client.post("/api/download", json={"url": "https://invalid.com", "format": "mp4"})
    assert response.status_code == 400
    data = response.json()
    assert "inválida" in data["detail"].lower()
