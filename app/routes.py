from flask import Blueprint, request, jsonify
from app.services.mongo_service import save_alert
from app.services.telegram_service import send_telegram_message
from app.utils.parser import parse_description, convert_to_ist, format_message
from app.config import Config

webhook = Blueprint("webhook", __name__)

@webhook.route("/webhook", methods=["POST"])
def handle_webhook():
    data = request.get_json()

    if not data:
        return jsonify({"error": "Invalid JSON"}), 400

    ticker = data.get("Ticker")
    name = data.get("Name")
    time = data.get("Time")
    description = data.get("Description")

    if ticker != Config.FILTER_TICKER or Config.FILTER_NAME not in name:
        return jsonify({"status": "ignored"}), 200

    parsed = parse_description(description)
    ist_time = convert_to_ist(time)

    alert_data = {
        "alert_id": data.get("Alert ID"),
        "ticker": ticker,
        "name": name,
        "time_utc": time,
        "time_ist": ist_time,
        "parsed": parsed
    }

    save_alert(alert_data)

    message = format_message(parsed, ticker)
    message += f"\n🕒 Time: {ist_time}"

    send_telegram_message(message)

    return jsonify({"status": "processed"}), 200
