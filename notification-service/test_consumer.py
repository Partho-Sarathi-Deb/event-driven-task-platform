import pytest
import json
from consumer import process_message

def test_process_message_actual_producer_schema():
    # Matches exact JSON produced by task-service/main.py
    producer_payload = json.dumps({
        "event_type": "TASK_CREATED",
        "payload": {
            "id": 42,
            "title": "Fix Consumer Bugs",
            "description": "Nested payload verification"
        }
    }).encode("utf-8")
    
    result = process_message(producer_payload)
    
    assert result["event_type"] == "TASK_CREATED"
    assert result["task_id"] == 42
    assert "Fix Consumer Bugs" in result["message"]

def test_process_message_missing_id():
    invalid_payload = json.dumps({
        "event_type": "TASK_CREATED",
        "payload": {"title": "No ID field"}
    }).encode("utf-8")
    
    with pytest.raises(ValueError):
        process_message(invalid_payload)
