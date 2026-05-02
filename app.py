from flask import Flask, request, jsonify
import requests
from config import Config
from utils import parse_message

app = Flask(__name__)

Config.validate()

@app.route("/", methods=["GET"])
def home():
    return {
        "status": "running",
        "service": "webhook-relay",
        "target": Config.TARGET_URL
    }

@app.route("/webhook", methods=["POST"])
def webhook():
    try:
        data = request.get_json()

        if not data or "message" not in data:
            return jsonify({"error": "Invalid payload"}), 400

        raw_message = data["message"]

        parsed = parse_message(raw_message)

        forward_payload = {
            "raw_message": raw_message,
            "parsed": parsed
        }

        headers = {
            "Content-Type": "application/json",
            "x-api-key": Config.API_KEY
        }

        response = requests.post(
            Config.TARGET_URL,
            json=forward_payload,
            headers=headers,
            timeout=Config.TIMEOUT
        )

        return jsonify({
            "status": "forwarded",
            "target_status": response.status_code,
            "parsed": parsed
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
