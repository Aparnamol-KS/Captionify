from flask_admin import AdminIndexView, expose, Admin
from flask import redirect, url_for, flash
from flask_login import current_user
from flask_admin.contrib.sqla import ModelView

# Restore default Flask-Admin index view but keep authentication
class MyAdminIndexView(AdminIndexView):
    @expose('/')
    def index(self):
        if not current_user.is_authenticated or not current_user.is_admin:
            flash("You must be an admin to access this page.", "danger")
            return redirect(url_for('main.login'))  # Redirect to login if not admin
        
        return super().index()  # Use default admin index template

    def is_accessible(self):
        return current_user.is_authenticated and current_user.is_admin

    def inaccessible_callback(self, name, **kwargs):
        flash("You do not have access to this page.", "danger")
        return redirect(url_for("main.login"))

# Restore default ModelView behavior but keep admin restriction
class AdminModelView(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.is_admin

    def inaccessible_callback(self, name, **kwargs):
        flash("You do not have access to this page.", "danger")
        return redirect(url_for("main.login"))

# Function to register Admin Views inside create_app()
def register_admin_views(admin, db):
    from app.models import User, Caption, PDFUpload, Summary 

    admin.add_view(AdminModelView(User, db.session))
    admin.add_view(AdminModelView(Caption, db.session))
    admin.add_view(AdminModelView(PDFUpload, db.session))
    admin.add_view(AdminModelView(Summary, db.session))
