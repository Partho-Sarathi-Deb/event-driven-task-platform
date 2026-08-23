import json
import pytest

# Example handler processing function from your consumer logic
def process_event_payload(body_bytes: bytes) -> dict:
    data = json.loads(body_bytes.decode("utf-8"))
    if "event_type" not in data or "payload" not in data:
        raise ValueError("Invalid event schema")
    return data

def test_process_valid_event():
    raw_message = b'{"event_type": "task_created", "payload": {"id": 1, "title": "Test Task"}}'
    result = process_event_payload(raw_message)
    
    assert result["event_type"] == "task_created"
    assert result["payload"]["id"] == 1

def test_process_invalid_event_schema():
    raw_message = b'{"invalid_key": "no_event_type"}'
    with pytest.raises(ValueError, match="Invalid event schema"):
        process_event_payload(raw_message)
