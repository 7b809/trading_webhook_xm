from flask import Flask
from api.routes import api, init_feed
from core.websocket_manager import init_socket

app = Flask(__name__)
app.register_blueprint(api, url_prefix='/api')

socketio = init_socket(app)

# ✅ Initialize feed runner with socket
init_feed(socketio)

@app.route('/')
def health():
    return {'status': 'running'}

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=8000)