from backend.app.core.scrubbing import scrub_payload
from backend.app.db.repository import SessionRepository


def test_scrubbing_removes_secrets_and_raw_content():
    raw = {
        "api_key": "AIzaSecret12345678901234567890",
        "answer": "Here is your token sk-secret98765432109876543210",
        "nested": {"authorization": "Bearer abc.def.ghi", "step": 1},
    }
    cleaned = scrub_payload(raw)
    assert "api_key" not in cleaned
    assert cleaned["answer"] == "[REDACTED]"
    assert "authorization" not in cleaned["nested"]
    assert cleaned["nested"]["step"] == 1


def test_session_creation_and_constant_time_token_auth():
    repo = SessionRepository()
    record, token = repo.create_session(label="auth-check")
    assert repo.get_session(record.session_id, token) is not None
    assert repo.get_session(record.session_id, "wrong-token") is None