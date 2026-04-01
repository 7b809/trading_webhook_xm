from flask import Blueprint, request, jsonify
from app.services.mongo_service import save_alert
from app.services.telegram_service import send_telegram_message
from app.utils.parser import parse_description, convert_to_ist, format_message
from app.config import Config

webhook = Blueprint("webhook", __name__)

# ✅ HOME ROUTE (Health Check)
@webhook.route("/", methods=["GET"])
def home():
    return jsonify({
        "status": "running",
        "service": "Trading Webhook API",
        "message": "Webhook server is live 🚀"
    }), 200


# ✅ WEBHOOK ROUTE
@webhook.route("/webhook", methods=["POST"])
def handle_webhook():
    data = request.get_json()
    
    send_telegram_message(f"{data}")

    if not data:
        return jsonify({"error": "Invalid JSON"}), 400

    ticker = data.get("Ticker")
    name = data.get("Name")
    time = data.get("Time")
    description = data.get("Description")

    # ✅ MULTI STRATEGY FILTER
    allowed_names = [x.strip() for x in Config.FILTER_NAMES.split(",") if x.strip()]

    if not any(strategy in (name or "") for strategy in allowed_names):
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