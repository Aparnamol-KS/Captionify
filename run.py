from app import create_app, db
from app import socketio

app = create_app()  # Create the Flask app

if __name__ == "__main__":
    with app.app_context():
        db.create_all()  # Ensure tables are created at startup
    socketio.run(app, host="0.0.0.0", port=5000, debug=True)
    