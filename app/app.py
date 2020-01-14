from flask import Flask, render_template, url_for, flash, redirect
from forms import LoginForm
from flask_wtf import FlaskForm
from wtforms import validators, StringField, SubmitField

app = Flask(__name__)

app.config['SECRET_KEY'] = '5791628bb0b13ce0c676dfde280ba245'


@app.route("/")
@app.route("/home")
def home():
    return render_template('home.html', title= "Welcome to PhosphoView")


@app.route("/upload")
def Data_Upload():
    return render_template('dataUpload.html', title='Data Upload')


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

@app.route("/inhibitors")
def Inhibitors():
    return render_template('inhibitors.html', title='Inhibitors')

@app.route("/login")
def login():
    form = LoginForm()
    return render_template('login.html', title='Login', form=form)

@app.route("/register")
def register():
    form = RegistrationForm()
    return render_template('register.html', title='Register', form=form)

if __name__ == '__main__':
    app.run(debug=True)
