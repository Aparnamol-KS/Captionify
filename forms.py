from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField,BooleanField
from wtforms.validators import DataRequired,Length,Email, EqualTo

class RegistrationForm(FlaskForm):
    username=StringField('Username', validators=[DataRequired(),Length(min=2, max=20)])
    email=StringField('Email', validators=[DataRequired(), Email()])
    password=StringField('Password', validators=[DataRequired()])
    confirm_password=StringField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit= SubmitField('Sign_up')

class LoginForm(FlaskForm):
    email=StringField('Email', validators=[DataRequired(), Email()])
    password=StringField('Password', validators=[DataRequired()])
    remember=BooleanField('Remember me')
    submit= SubmitField('Login')    