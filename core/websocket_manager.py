from flask_socketio import SocketIO, join_room

socketio = SocketIO(cors_allowed_origins='*', async_mode='threading')

def init_socket(app):
    socketio.init_app(app)

    # ✅ NEW: join room handler
    @socketio.on("join")
    def handle_join(data):
        user_id = data.get("user_id")
        if user_id:
            join_room(user_id)

    return socketio