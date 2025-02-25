from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from config import Config  # Ensure you have a Config class in config.py

# Initialize extensions
db = SQLAlchemy()
bcrypt = Bcrypt()
login_manager = LoginManager()

# Flask-Login setup
login_manager.login_view = "main.login"  # Redirect to login if not authenticated
login_manager.login_message_category = "info"  # Flash message category

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)  # Load config from a separate file

    # Initialize extensions
    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)

    # Import models **inside app context** to avoid circular imports
    with app.app_context():
        from app import models  # Ensure models.py exists and includes User

    # Import and register blueprints (routes)
    from app.routes import main  
    app.register_blueprint(main)

    return app
