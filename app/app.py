from flask import Flask, render_template, url_for, flash, redirect
from werkzeug.utils import secure_filename
from forms import Kinase, FileForm, Inhibitor
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms import validators, StringField, SubmitField
import os
#from wtforms_sqlalchemy.fields import QuerySelectField




app = Flask(__name__)
app.config['SECRET_KEY'] = '11d5c86229d773022cb61679343f8232'


@app.route("/")
@app.route("/home")
def home():
    return render_template('home.html', title= "Welcome to LhosphoView")


@app.route("/upload", methods=['GET', 'POST'])
def Data_Upload():
    form=FileForm()
    return render_template('Data_Upload.html', title='Data Upload', form=form)


@app.route("/HumanKinaseList", methods = ['GET', 'POST'])
def HumanKinaseList():
    form=Kinase() 
    if form.validate_on_submit():
        if form.search.data in 'oxo':
            return redirect(url_for('home'))
        else: 
            flash('Kinase not found. Please check and try again.', 'danger')
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
        'Name': 'Alisha Angdembe',
        'Description': 'A Msc Bioinformatics student, who loves coding as well',
    }, 


            ]

    return render_template('about.html', posts=posts, title = " About")



@app.route("/documentation")
def Documentation():
    return render_template('documentation.html', title='Documentation')


@app.route("/Phosphosite")
def Phosphosite():
#    form = ChoiceForm()
#    form.opts.query = Choice.query.filter(Choice.id > 1)
#    if form.validate_on_submit():
#        return '<html><h1>{}</h1></html>'.format(form.opts.data)
    return render_template('Phosphosite.html', title='Phosphosite Search')



@app.route("/Inhibitors", methods = ['GET', 'POST'])
def Inhibitors():
    form=Inhibitor()
    if form.validate_on_submit():
        if form.search.data in 'oxo':
            return redirect(url_for('results_inhibitor'))
        else: 
            flash('Inhibitor not found. Please check and try again.', 'danger')
    return render_template('Inhibitors.html', title='Inhibitors', form=form)

@app.route("/Inhibitors_one", methods = ['GET', 'POST'])
def Inhibitors_one():
    return render_template('Inhibitors_one.html', title='Inhibitors')




@app.route("/results_inhibitor")
def results_inhibitor():
    return render_template('results_inhibitor.html', title='Inhibitor results')




if __name__ == '__main__':
    app.run(debug=True)
