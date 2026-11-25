from backend.app.schemas import ChatRequest, ChatResponse, HealthResponse, SessionCreateResponse


def test_chat_request_bounds_and_api_key_excluded():
    req = ChatRequest(
        session_id="sess_123",
        message="Check auth middleware",
        api_key="AIza-secret-test-key",
    )
    dumped = req.model_dump()
    assert "api_key" not in dumped
    assert req.items == []


def test_contract_models_instantiate():
    sess = SessionCreateResponse(session_id="s1", session_token="tok_abc")
    health = HealthResponse(
        status="ok",
        env="development",
        main_provider="ollama",
        main_model="gpt-oss:20b",
        persistence="unavailable",
    )
    assert sess.session_id == "s1"
    assert health.status == "ok"