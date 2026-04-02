from flask import Flask, request, jsonify, render_template
from config import Config
from db import alerts_collection
from telegram import send_telegram_message
from parser import parse_alert
import pytz
from logger import logger
from datetime import datetime, timezone
import uuid

app = Flask(__name__)

IST = pytz.timezone("Asia/Kolkata")

@app.route("/")
def dashboard():
    alerts = list(alerts_collection.find().sort("created_at", -1).limit(50))
    for a in alerts:
        a["_id"] = str(a["_id"])
        a["ist_time"] = a["created_at"].astimezone(IST).strftime("%Y-%m-%d %H:%M:%S")
    return render_template("dashboard.html", alerts=alerts)


@app.route("/webhook", methods=["POST"])
def webhook():

    # ✅ Unique request tracking (no logic change)
    request_id = str(uuid.uuid4())[:8]

    data = request.get_json(silent=True)
    if not data:
        data = request.data.decode("utf-8")

    logger.info(f"[{request_id}] 📥 Incoming raw data: {data}")

    parsed = parse_alert(data)

    if parsed["type"] == "ignored":
        logger.info(f"[{request_id}] ⚠️ Ignored alert")
        return jsonify({"status": "ignored"})

    doc = {
        "text": parsed["text"],
        "chat_id": parsed["chat_id"],
        "type": parsed["type"],
        "raw": parsed["raw"],
        "created_at": datetime.now(timezone.utc)
    }

    # ✅ MongoDB save (same logic, just tracked)
    mongo_success = False
    try:
        result = alerts_collection.insert_one(doc)
        logger.info(f"[{request_id}] 💾 Saved to MongoDB ID: {result.inserted_id}")
        mongo_success = True
    except Exception as e:
        logger.error(f"[{request_id}] ❌ MongoDB Error: {e}")

    # ✅ Telegram send (same logic, with validation)
    if parsed["text"]:
        try:
            res = send_telegram_message(parsed["text"], parsed["chat_id"])

            # check response without changing flow
            if res and isinstance(res, dict) and res.get("ok"):
                logger.info(f"[{request_id}] 📤 Telegram sent: {parsed['text']}")
            else:
                logger.error(f"[{request_id}] ❌ Telegram failed: {res}")

        except Exception as e:
            logger.error(f"[{request_id}] ❌ Telegram Error: {e}")

    return jsonify({"status": "success"})


if __name__ == "__main__":
    # ✅ Prevent Windows socket crash (no logic change)
    app.run(port=Config.PORT, debug=True, use_reloader=False)