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
        "service": "webhook-relay"
    }

@app.route("/webhook", methods=["POST"])
@app.route("/webhook/", methods=["POST"])  # handle trailing slash too
def webhook():
    try:
        data = request.get_json()

        if not data:
            return jsonify({"error": "Invalid payload"}), 400

        headers = {
            "Content-Type": "application/json",
            "x-api-key": Config.API_KEY
        }

        response = requests.post(
            Config.TARGET_URL,
            json=data,  # 🔥 forward EXACTLY as received
            headers=headers,
            timeout=Config.TIMEOUT
        )

        return jsonify({
            "status": "forwarded",
            "target_status": response.status_code
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
