"""The request contract the B2C chat widget was getting wrong."""


def test_plant_chat_returns_answer_with_provenance(client):
    """The documented shape returns 200 and reports what was retrieved."""
    response = client.post(
        "/api/plants/1/chat",
        json={"messages": [{"role": "user", "content": "Why are my tomato leaves yellowing?"}]},
    )

    assert response.status_code == 200, response.text
    body = response.json()

    assert body["role"] == "assistant"
    assert body["text"]

    provenance = body["provenance"]
    assert provenance["subQuestions"] == [
        "What causes yellowing leaves?",
        "What causes brown spots?",
    ]
    assert provenance["recordCount"] >= 1
    assert provenance["graphAvailable"] is True

    # Tags describe what actually ran, rather than being hardcoded.
    assert "Knowledge Graph" in body["tags"]
    assert "Query Decomposition" in body["tags"]


def test_legacy_text_payload_is_rejected(client):
    """`{"text": ...}` is what CognitiveAssistant used to send; it is invalid."""
    response = client.post("/api/b2c/chat", json={"text": "hello"})

    assert response.status_code == 422


def test_empty_messages_rejected(client):
    response = client.post("/api/b2c/chat", json={"messages": []})

    assert response.status_code == 422


def test_blank_message_rejected(client):
    response = client.post(
        "/api/b2c/chat",
        json={"messages": [{"role": "user", "content": "   "}]},
    )

    assert response.status_code == 422


def test_b2b_chat_endpoint_exists(client):
    """The B2B surface has a real endpoint; it used to be a setTimeout mock."""
    response = client.post(
        "/api/b2b/chat",
        json={"messages": [{"role": "user", "content": "Carbon uptake this quarter?"}]},
    )

    assert response.status_code == 200, response.text
    assert response.json()["text"]


def test_user_casing_reaches_the_model(client, stub_llm):
    """The endpoint used to lower-case the question before the model saw it."""
    client.post(
        "/api/b2c/chat",
        json={"messages": [{"role": "user", "content": "Is Septoria affecting my Roma tomatoes?"}]},
    )

    assert any("Septoria" in prompt for prompt in stub_llm.prompts)
    assert any("Roma" in prompt for prompt in stub_llm.prompts)
