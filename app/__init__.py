from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_migrate import Migrate
from config import Config  # Import Config from config.py
from flask_socketio import SocketIO

# Initialize extensions (but don't attach them to an app yet)
db = SQLAlchemy()
bcrypt = Bcrypt()
login_manager = LoginManager()
migrate = Migrate()
socketio = SocketIO(cors_allowed_origins="*", async_mode="threading")

# Flask-Login setup
login_manager.login_view = "main.login"
login_manager.login_message_category = "info"

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)  # Load config
   

    # Initialize extensions with the app
    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)  # Correctly initialize Flask-Migrate
    socketio.init_app(app)
    # Import models **inside app context** to avoid circular imports
    with app.app_context():
        from app import models  # Ensure models.py exists

    # Import and register blueprints
    from app.routes import main  
    app.register_blueprint(main)

    return app
