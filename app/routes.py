from flask import Blueprint, render_template, flash, redirect, current_app, url_for, send_from_directory, request
from app.forms import RegistrationForm, LoginForm
from app.models import PDFUpload, User, Caption, Summary
from app import db, bcrypt
from flask_login import login_user, logout_user, login_required, current_user
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
import os
from app.utils import save_pdf_to_db, generate_pdf

main = Blueprint('main', __name__)  # Define Blueprint


# Home page
@main.route('/')
def home():
    return render_template("home.html")

# Registration page
@main.route('/registration', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        is_admin = True if form.username.data == "Aparna" else False

        new_user = User(username=form.username.data, email=form.email.data, password=hashed_password, is_admin=is_admin)
        db.session.add(new_user)
        db.session.commit()
        
        flash('Account created successfully!', 'success')
        return redirect(url_for('main.login'))  
    
    return render_template("register.html", title='Register', form=form)


# Login page
@main.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user)
            flash('Login successful!', 'success')
            return redirect(url_for('main.home'))
        else:
            flash('Login failed. Check your email and password.', 'danger')
    return render_template("login.html", title='Login', form=form)


@main.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    if request.method == 'POST':
        # Get form data
        name = request.form.get('name')
        email = request.form.get('email')
       
       # Update current user's details instead of creating a new user
        current_user.username = name
        current_user.email = email

        # Commit changes to the database
        db.session.commit()

        flash('Profile updated successfully!', 'success')
        return redirect(url_for('main.profile'))  # Reload the profile page

    return render_template("profile.html", user=current_user) 

# Logout route
@main.route('/logout')
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('main.home'))

# Index page
@main.route('/index')
def index():
    return render_template("index.html")

@main.route('/pdfs')
@login_required
def pdfs():
    pdf_files = PDFUpload.query.filter_by(user_id=current_user.id).all()  
    return render_template("pdfs.html", pdfs=pdf_files)


@main.route('/view_pdf/<int:pdf_id>')
@login_required
def view_pdf(pdf_id):
    pdf = PDFUpload.query.get_or_404(pdf_id)  # Fetch the PDF from the database
    
    # Ensure the correct directory where PDFs are stored
    pdf_directory = os.path.join(current_app.root_path, 'uploads')  
    
    # Check if file exists
    if not os.path.exists(os.path.join(pdf_directory, pdf.filename)):
        return "File not found", 404
    
    # Serve the PDF file
    return send_from_directory(pdf_directory, pdf.filename)


 

@main.route('/save_transcription', methods=['POST'])
@login_required
def save_transcription():
    transcription_text = request.form.get("transcription_text")  # Get text from form
    if not transcription_text:
        return "No transcription text provided!", 400
    pdf_id = save_pdf_to_db(transcription_text)
    return redirect(url_for("dashboard"))  # Redirect after saving


# Error Handlers
@main.app_errorhandler(404)  
def page_not_found(e):
    return render_template("404.html"), 404

@main.app_errorhandler(500)  
def internal_server_error(e):
    return render_template("500.html"), 500

# Restrict admin access only to admins
class AdminModelView(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated and getattr(current_user, 'is_admin', False)  # ✅ Safe check

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('main.login'))  # Redirect to login if not admin
