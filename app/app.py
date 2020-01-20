from flask import Flask, render_template, url_for, flash, redirect
from werkzeug.utils import secure_filename
from forms import LoginForm, FileForm, Inhibitor
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms import validators, StringField, SubmitField
import os


app = Flask(__name__)

app.config['SECRET_KEY'] = '5791628bb0b13ce0c676dfde280ba245'


@app.route("/")
@app.route("/home")
def home():
    return render_template('home.html', title= "Welcome to PhosphoView")


@app.route("/upload", methods=['GET', 'POST'])
def Data_Upload():
    form=FileForm()
    return render_template('Data_Upload.html', title='Data Upload', form=form)


@app.route("/HumanKinaseList")
def HumanKinaseList():
    form=LoginForm() 
    return render_template('ListHumanKinases.html', title='List of Human Kinases', form=form)
                                                       

@app.route("/about")
def about():

    posts = [
    {
        'Name': 'Mohamed Golaid',
        'Description': 'A Msc Bioinformatics student, who loves coding',
    },
    {
        'Name': 'Han Ooi',
        'Description': 'A Msc Bioinformatics student, who loves coding as well',
    },

    {
        'Name': 'Sheridan',
        'Description': 'A Msc Bioinformatics student, who loves coding as well',
    }, 
    {
        'Name': 'Anastastia',
        'Description': 'A Msc Bioinformatics student, who loves coding as well',
    }, 

    {
        'Name': 'Alisha Ang',
        'Description': 'A Msc Bioinformatics student, who loves coding as well',
    }, 


            ]

    return render_template('about.html', posts=posts, title = " About")

@app.route("/documentation")
def Documentation():
    return render_template('documentation.html', title='Documentation')

@app.route("/advancedSearch")
def AdvancedSearch():
    return render_template('advancedSearch.html', title='Advanced Search')

@app.route("/Inhibitors")
def Inhibitors():
    form=Inhibitor()
    return render_template('inhibitors.html', title='Inhibitors', form=form)



if __name__ == '__main__':
    app.run(debug=True)
