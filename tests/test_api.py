from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_health() -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_chat_schema_and_language() -> None:
    response = client.post("/api/v1/chat", json={"question": "임금 체불은 어떻게 해야 하나요?", "language": "ko"})
    assert response.status_code == 200
    body = response.json()
    assert body["language"] == "ko"
    assert "answer" in body
    assert body["retrieval"]["top_k"] == 0


def test_chat_rejects_blank_question() -> None:
    response = client.post("/api/v1/chat", json={"question": "   ", "language": "ko"})
    assert response.status_code == 422
