from flask import Flask, request, jsonify
import requests
from config import Config

app = Flask(__name__)


@app.route("/webhook/tradingview/<int:security_id>/", methods=["POST"])
def relay(security_id):
    try:
        data = request.get_json()

        if not data:
            return jsonify({"status": "error", "message": "No JSON received"}), 400

        target_url = f"{Config.TARGET_BASE_URL}/webhook/tradingview/{security_id}/"

        print(f"[RELAY] Forwarding → {target_url}")
        print(f"[RELAY] Payload → {data}")

        response = requests.post(
            target_url,
            json=data,
            timeout=5
        )

        return jsonify({
            "status": "forwarded",
            "target_status": response.status_code,
            "target_response": response.text
        })

    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


@app.route("/", methods=["GET"])
def home():
    return "🚀 Railway Webhook Relay Running"


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
