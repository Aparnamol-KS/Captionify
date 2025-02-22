from flask import Flask, render_template,flash, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from forms import RegistrationForm, LoginForm
from datetime import datetime

# Create Flask instance
app = Flask(__name__)
# Secret key for session security
app.config['SECRET_KEY'] = 'your_secret_key'
# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
db = SQLAlchemy(app)

# User model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
    password = db.Column(db.String(60), nullable=False)
    posts=db.relationship('Post', backref='author', lazy=True)

    def __repr__(self):
        return f"User('{self.username}','{self.email}',{self.image_file})"
    
class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title=db.Column(db.String(100),nullable=False)
    date_posted=db.Column(db.DateTime,nullable=False, default=datetime.utcnow()) 
    content=db.Column(db.Text, nullable=False)
    user_id= db.Column(db.Integer, db.ForeignKey('user.id'))
    def __repr__(self):
        return f"Post('{self.title}','{self.date_posted}')"  

# Home page
@app.route('/')
def home():
    return render_template("home.html")

# Registration page
@app.route('/registration', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        flash(f'Account created successfully')
        return redirect(url_for('index'))
    return render_template("register.html", title='Register', form=form)

# Login page
@app.route('/login')
def login():
    form = LoginForm()
    if form.validate_on_submit():
        return redirect(url_for('index'))
    return render_template("login.html", title='Login', form=form)

# Index page
@app.route('/index')
def index():
    return render_template("index.html")

# Profile page
@app.route('/profile')
def profile():
    return render_template("profile.html")

# Invalid URL (404 error)
@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404

# Internal server error (500 error)
@app.errorhandler(500)
def internal_server_error(e):
    return render_template("500.html"), 500

if __name__ == "__main__":
    app.run(debug=True)
