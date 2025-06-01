from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_socketio import SocketIO
from config import Config  # Import Config from config.py
from flask_admin import Admin

# Initialize extensions (but don't attach them to an app yet)
db = SQLAlchemy()
bcrypt = Bcrypt()
login_manager = LoginManager()
migrate = Migrate()
socketio = SocketIO(cors_allowed_origins="*", async_mode="threading")

# Flask-Login setup
login_manager.login_view = "main.login"
login_manager.login_message_category = "info"

from flask_admin.contrib.sqla import ModelView
from flask_login import current_user
from flask import redirect, url_for, flash
from app.admin import MyAdminIndexView, register_admin_views  # Import custom admin view and function

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialize extensions
    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)
    socketio.init_app(app)

    with app.app_context():
        from app import models
        from app.routes import main  # Import blueprints

        # Setup Admin Panel
        admin = Admin(app, name="Admin Panel", template_mode="bootstrap4", index_view=MyAdminIndexView())

        # Register admin views (ensures only admin users can access models)
        register_admin_views(admin, db)

        # Register blueprints
        app.register_blueprint(main)

    return app
