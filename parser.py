
import json
from datetime import datetime

def parse_alert(data):
    parsed = {
        "raw": data,
        "text": None,
        "chat_id": None,
        "type": "unknown",
        "timestamp": datetime.utcnow()
    }

    if isinstance(data, dict):
        parsed["text"] = data.get("text")
        parsed["chat_id"] = data.get("chat_id")
        parsed["type"] = "json"
        return parsed

    if isinstance(data, str):
        if "NEW ALERT" in data:
            parsed["type"] = "ignored"
            return parsed

        try:
            json_data = json.loads(data)
            parsed["text"] = json_data.get("text")
            parsed["chat_id"] = json_data.get("chat_id")
            parsed["type"] = "json_string"
            return parsed
        except:
            pass

        parsed["text"] = data.strip()
        parsed["type"] = "text"

    return parsed
