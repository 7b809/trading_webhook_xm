def parse_message(message: str) -> dict:
    parts = message.split()
    data = {}

    if parts:
        data["signal"] = parts[0]

    for part in parts[1:]:
        if "=" in part:
            key, value = part.split("=", 1)
            data[key.lower()] = value

    return data
