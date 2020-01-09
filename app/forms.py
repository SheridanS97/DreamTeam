from flask_wtf import FlaskForm
from wtforms import validators
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Length, Email, EqualTo
from wtforms.fields.html5 import EmailField
from flask_wtf import Form
from wtforms import TextField, BooleanField
from wtforms.validators import Required

# use this python module for creating python forms and user input 
# import stringfields  so the user can input strings
# use validators in order to prevent the user from inputting details that we don't want e.g correct length of password

class RegistrationForm(FlaskForm):
	username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
	email = StringField('Email', validators=[DataRequired(), Email()])
	password = PasswordField('Password', validators=[DataRequired()])
	confirm_password = PasswordField('Confirm Password', validators=[DataRequired(),EqualTo('password')])
	submit = SubmitField('Register')


class LoginForm(FlaskForm):
	username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])		
	email = StringField('Email', validators=[DataRequired(), Email()])
	password = PasswordField('Password', validators=[DataRequired()])
	remember = BooleanField('Remember Me')
	submit = SubmitField('Login')

