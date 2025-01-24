from flask import Flask, render_template, flash
from flask_wtf import FlaskForm
from wtforms import StringField,SubmitField
from wtforms.validators import DataRequired
#create flask instance
app= Flask(__name__)
#create a route decorator

#create form class

app.config['SECRET_KEY'] = "my super secret key that on one is supposed to know"

#home page
@app.route('/')

def home():
    return render_template("home.html")
#index page
@app.route('/index')

def index():
    return render_template("index.html")

#login page
@app.route('/login')

def login():
    return render_template("login.html")


#invalid url
@app.errorhandler(404)
def page_not_found(e):
	return render_template("404.html"),404

#internal server error
@app.errorhandler(500)
def page_not_found(e):
	return render_template("500.html"),500

@app.route('/profile')

def profile():
      return render_template('profile.html')
