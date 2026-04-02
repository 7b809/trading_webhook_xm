from flask import Flask, request, jsonify, render_template
from config import Config
from db import alerts_collection, db
from telegram import send_telegram_message
from parser import parse_alert
import pytz
from logger import logger
from datetime import datetime, timezone
import uuid

app = Flask(__name__)

IST = pytz.timezone("Asia/Kolkata")


# ✅ UPDATED DASHBOARD (unchanged logic)
@app.route("/")
def dashboard():

    collection_name = request.args.get("collection", "alerts")
    limit = int(request.args.get("limit", 50))

    collection = db[collection_name] if collection_name != "alerts" else alerts_collection

    alerts = list(collection.find().sort("created_at", -1).limit(limit))

    for a in alerts:
        a["_id"] = str(a["_id"])
        a["ist_time"] = a["created_at"].astimezone(IST).strftime("%Y-%m-%d %H:%M:%S")

    return render_template(
        "dashboard.html",
        alerts=alerts,
        current_collection=collection_name,
        limit=limit,
        collections=Config.WEBHOOK_MAP
    )


# ✅ OLD ROUTE (ONLY added default message logic)
@app.route("/webhook", methods=["POST"])
def webhook():

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

    try:
        result = alerts_collection.insert_one(doc)
        logger.info(f"[{request_id}] 💾 Saved to MongoDB ID: {result.inserted_id}")
    except Exception as e:
        logger.error(f"[{request_id}] ❌ MongoDB Error: {e}")

    # ✅ DEFAULT MESSAGE HANDLING (NEW)
    message_text = parsed["text"] if parsed.get("text") else f"⚠️ Alert received but unable to process.\nTime: {datetime.now(IST).strftime('%Y-%m-%d %H:%M:%S')}"

    try:
        res = send_telegram_message(message_text, parsed.get("chat_id"))

        if res and isinstance(res, dict) and res.get("ok"):
            logger.info(f"[{request_id}] 📤 Telegram sent: {message_text}")
        else:
            logger.error(f"[{request_id}] ❌ Telegram failed: {res}")

    except Exception as e:
        logger.error(f"[{request_id}] ❌ Telegram Error: {e}")

    return jsonify({"status": "success"})


# ✅ NEW ROUTE (FIXED + DEFAULT MESSAGE)
@app.route("/webhook/<int:webhook_id>", methods=["POST"])
def webhook_dynamic(webhook_id):

    request_id = str(uuid.uuid4())[:8]

    collection_name = Config.WEBHOOK_MAP.get(webhook_id)

    # ✅ FIX: validate before use
    if not collection_name:
        logger.error(f"[{request_id}] ❌ Invalid webhook ID: {webhook_id}")
        return jsonify({"error": "Invalid webhook ID"}), 400

    collection = db[collection_name]

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

    try:
        result = collection.insert_one(doc)
        logger.info(f"[{request_id}] 💾 Saved to {collection_name}: {result.inserted_id}")
    except Exception as e:
        logger.error(f"[{request_id}] ❌ MongoDB Error: {e}")

    # ✅ DEFAULT MESSAGE HANDLING (NEW)
    message_text = parsed["text"] if parsed.get("text") else f"⚠️ Alert received but unable to process.\nTime: {datetime.now(IST).strftime('%Y-%m-%d %H:%M:%S')}"

    try:
        res = send_telegram_message(message_text, parsed.get("chat_id"))

        if res and isinstance(res, dict) and res.get("ok"):
            logger.info(f"[{request_id}] 📤 Telegram sent: {message_text}")
        else:
            logger.error(f"[{request_id}] ❌ Telegram failed: {res}")

    except Exception as e:
        logger.error(f"[{request_id}] ❌ Telegram Error: {e}")

    return jsonify({"status": "success"})