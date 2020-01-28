from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, validators, TextField
from wtforms.validators import DataRequired, Length, Email, EqualTo, Required
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms.fields.html5 import EmailField
from flask_wtf import Form
from wtforms import SelectField

# use this python module for creating python forms and user input 
# import stringfields  so the user can input strings
# use validators in order to prevent the user from inputting details that we don't want e.g correct length of password



class Kinase(FlaskForm):		
	search = StringField('Enter a valid Kinase name', validators=[DataRequired()])
	submit = SubmitField('Search')


class Inhibitor(FlaskForm):		
	search = StringField('Enter a Inhibitor of a Kinase name', validators=[DataRequired()])
	submit = SubmitField('Search')


class FileForm(FlaskForm):
    file = FileField(validators=[FileRequired(), FileAllowed('csv', 'tsv')])
    submit = SubmitField('Submit')

class Phosphosite(FlaskForm):
	chromosome_number = SelectField('chromosome_number', choices=[('1', '2'),('3', '4')])
	karyotypes = SelectField('karyotypes', choices=[])
	submit = SubmitField('Search')
