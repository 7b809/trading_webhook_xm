from flask import Blueprint, request, jsonify
from core.dhan_feed_runner import DhanLiveFeed

api = Blueprint('api', __name__)

feed_runner = None

def init_feed(socketio):
    global feed_runner
    feed_runner = DhanLiveFeed(socketio)

# ✅ Start or Add Instruments
@api.route('/feed/start', methods=['POST'])
def start_feed():
    data = request.json
    instruments = data.get("instruments", [])

    result = feed_runner.start(instruments)
    return jsonify(result)

# ✅ Add Instruments dynamically
@api.route('/feed/add', methods=['POST'])
def add_feed():
    data = request.json
    instruments = data.get("instruments", [])

    result = feed_runner.add_instruments(instruments)
    return jsonify(result)

# ✅ Remove Instruments
@api.route('/feed/remove', methods=['POST'])
def remove_feed():
    data = request.json
    instruments = data.get("instruments", [])

    result = feed_runner.remove_instruments(instruments)
    return jsonify(result)

# ✅ NEW: user subscription API
@api.route('/feed/subscribe', methods=['POST'])
def subscribe_user():
    data = request.json
    user_id = data.get("user_id")
    instruments = data.get("instruments", [])

    result = feed_runner.subscribe_user(user_id, instruments)
    return jsonify(result)