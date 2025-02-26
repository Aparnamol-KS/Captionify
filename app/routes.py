from flask import Blueprint, render_template, flash, redirect, url_for, request
from app.forms import RegistrationForm, LoginForm
from app.models import User
from app import db
from flask_bcrypt import Bcrypt
from flask_login import login_user, logout_user, login_required

from flask import render_template
from flask_login import login_required, current_user

bcrypt = Bcrypt()  # Initialize bcrypt for password hashing

main = Blueprint('main', __name__)  # Define a Blueprint


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
        new_user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        flash('Account created successfully!', 'success')
        return redirect(url_for('main.login'))  # Redirect to login page after registration
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
            return redirect(url_for('main.index'))
        else:
            flash('Login failed. Check your email and password.', 'danger')
    return render_template("login.html", title='Login', form=form)


@main.route('/profile')
@login_required
def profile():
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

# Error Handlers
@main.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404

@main.errorhandler(500)
def internal_server_error(e):
    return render_template("500.html"), 500
