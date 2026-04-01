import json
from datetime import datetime
import pytz

IST = pytz.timezone("Asia/Kolkata")

def parse_description(desc):
    try:
        return json.loads(desc)
    except:
        return {}

def convert_to_ist(utc_time_str):
    dt = datetime.fromisoformat(utc_time_str.replace("Z", "+00:00"))
    return dt.astimezone(IST).strftime("%Y-%m-%d %H:%M:%S")

def format_message(parsed_data, ticker):
    text = parsed_data.get("text", "No message")

    return f"""
📊 *Trade Alert*

📌 *Symbol*: {ticker}

{text}
"""
