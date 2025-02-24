from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager

# Initialize extensions
db = SQLAlchemy()
bcrypt = Bcrypt()
login_manager = LoginManager()

# Flask-Login setup
login_manager.login_view = "main.login"  # Redirect to login if not authenticated
login_manager.login_message_category = "info"  # Flash message category

def create_app():
    app = Flask(__name__)

    # Secret key for session security
    app.config['SECRET_KEY'] = 'your_secret_key'

    # Database configuration
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  

    # Initialize extensions
    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)

    # Import models **after** app is initialized
    from app.models import User  

    # Import and register blueprints (routes)
    from app.routes import main
    app.register_blueprint(main)

    return app

