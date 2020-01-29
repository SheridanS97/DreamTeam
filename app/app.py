from flask import Flask, render_template, url_for, flash, redirect, request
from werkzeug.utils import secure_filename
from forms import *
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms import validators, StringField, SubmitField
import os
from sqlalchemy import create_engine, or_, and_
from kinase_functions import *
from db_setup import s 

app = Flask(__name__)
app.config['SECRET_KEY'] = '11d5c86229d773022cb61679343f8232'


@app.route("/")
@app.route("/home")
def home():
    return render_template('home.html', title= "Welcome to PhosphoView")


ALLOWED_EXTENSIONS = {'tsv', 'csv'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route("/upload", methods=['GET', 'POST'])
def Data_Upload():
    form=FileForm()
    if request.method == "POST":
            if request.files:
                InputFile = request.files["InputFile"]
                if InputFile.filename == '':
                    flash('No selected file', 'danger')
                if InputFile and allowed_file(InputFile.filename):
                    uploads_dir = os.path.join(app.instance_path, 'Data_Upload')
                    if not os.path.exists(uploads_dir):
                        os.makedirs(uploads_dir)
                    InputFile.save(os.path.join(uploads_dir, secure_filename(InputFile.filename)))
                    return redirect(url_for('home'))
    return render_template('Data_Upload.html', title='Data Upload', form=form)



@app.route("/HumanKinases", methods = ['GET', 'POST'])
def HumanKinases():
    form=Kinase() 
    search_kinase = form.search.data
    GeneName = s.query(KinaseGeneName).all()
    list_aliases = []
    
    for gene in GeneName:
        gene_aliases = gene.gene_alias
        list_aliases.append(gene_aliases)

    if form.validate_on_submit():
        for x in range(len(list_aliases)):
            if search_kinase.upper() in list_aliases[x]:
                return redirect(url_for('results_kinases', search_kinase=search_kinase))

        else:
            flash('Kinase not found. Please check and try again.', 'danger')
    
    return render_template('HumanKinases.html', title='List of Human Kinases', form=form)
      

@app.route("/HumanKinases/results_kinases/<search_kinase>")
def results_kinases(search_kinase):
    dictionary = get_gene_alias_protein_name(search_kinase)
    return render_template('results_kinases.html', dictionary=dictionary, search_kinase=search_kinase)


@app.route("/HumanKinases/results_kinases/<search_kinase>/<gene>")
def Individual_kinase(search_kinase,gene):
    Information = get_gene_metadata_from_gene(gene)
    subcellular_location = (get_subcellular_location_from_gene(gene))
    substrate_phosphosites = get_substrates_phosphosites_from_gene(gene)
    Inhibitor = get_inhibitors_from_gene(gene)
    return render_template('Individual_kinase.html', title='Individual Kinase Page', Inhibitor= Inhibitor, gene = gene, Information = Information, subcellular_location= subcellular_location, substrate_phosphosites=substrate_phosphosites)


@app.route("/Phosphosite", methods= ['GET', 'POST'])
def Phosphosites():
    form = Phosphosite()
    return render_template('Phosphosite.html', title='Phosphosite Search', form=form)


@app.route("/Inhibitors", methods = ['GET', 'POST'])
def Inhibitors():
    ALL_inhibitors = get_all_inhibitors_meta()
    return render_template('Inhibitors.html', title='Inhibitors', ALL_inhibitors=ALL_inhibitors)

@app.route("/Inhibitors/final")
def Individual_Inhibitors():
    inhibitor = "GSK650394A"
    Individual_Inhibitor = get_inhibitor_meta_from_inhibitor(inhibitor)
    return render_template('Individual_inhibitor.html', title='Individual Inhibitors', Individual_Inhibitor=Individual_Inhibitor)


@app.route("/documentation")
def Documentation():
    return render_template('documentation.html', title='Documentation')


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




if __name__ == '__main__':
    app.run(debug=True)
