from flask import Flask, request, jsonify
import requests
import threading
from config import Config

app = Flask(__name__)


# -----------------------------------
# 🔁 ASYNC SENDER (BACKGROUND)
# -----------------------------------
def send_async(url, data):
    try:
        print(f"[ASYNC] Sending → {url}")
        response = requests.post(url, json=data, timeout=10)
        print(f"[ASYNC] Response → {response.status_code} | {response.text}")
    except Exception as e:
        print(f"[ASYNC ERROR] {str(e)}")


# -----------------------------------
# 📡 WEBHOOK RELAY
# -----------------------------------
@app.route("/webhook/tradingview/<int:security_id>/", methods=["POST"])
def relay(security_id):
    try:
        data = request.get_json()

        if not data:
            return jsonify({
                "status": "error",
                "message": "No JSON received"
            }), 400

        target_url = f"{Config.TARGET_BASE_URL}/webhook/tradingview/{security_id}/"

        print(f"[RELAY] Incoming → {data}")
        print(f"[RELAY] Forwarding → {target_url}")

        # 🔥 ASYNC CALL (NO BLOCKING)
        thread = threading.Thread(target=send_async, args=(target_url, data))
        thread.daemon = True
        thread.start()

        # ✅ INSTANT RESPONSE (IMPORTANT)
        return jsonify({
            "status": "received"
        }), 200

    except Exception as e:
        print(f"[RELAY ERROR] {str(e)}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


# -----------------------------------
# 🏠 HEALTH CHECK
# -----------------------------------
@app.route("/", methods=["GET"])
def home():
    return "🚀 Railway Webhook Relay Running"


# -----------------------------------
# 🚀 RUN
# -----------------------------------
if __name__ == "__main__":
    import os
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port)