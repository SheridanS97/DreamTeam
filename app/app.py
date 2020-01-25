from flask import Flask, render_template, url_for, flash, redirect
from werkzeug.utils import secure_filename
from forms import Kinase, FileForm, Inhibitor
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms import validators, StringField, SubmitField
import os
from db_setup import s
from kinase_declarative import * 
from sqlalchemy import create_engine, or_, and_


app = Flask(__name__)
app.config['SECRET_KEY'] = '11d5c86229d773022cb61679343f8232'


@app.route("/")
@app.route("/home")
def home():
    return render_template('home.html', title= "Welcome to LhosphoView")


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

                def get_gene_protein_name(kinase_input):
                    like_kin = "%{}%".format(kinase_input)
                    tmp = []
                    kinase_query = s.query(KinaseGeneMeta).join(KinaseGeneName).filter(or_(KinaseGeneName.gene_alias.like(like_kin), KinaseGeneMeta.uniprot_entry.like(like_kin),\
                                                   KinaseGeneMeta.uniprot_number.like(like_kin), KinaseGeneMeta.protein_name.like(like_kin))).all()
                    for row in kinase_query:
                        results = {}
                        results["Gene_Name"] = row.to_dict()["gene_name"]
                        results["Protein_Name"] = row.to_dict()["protein_name"]
                        tmp.append(results)
                    return tmp
                
                dictionary = get_gene_protein_name(search_kinase)
                return render_template('results_kinases.html', search_kinase=search_kinase, dictionary=dictionary)

        else:
            flash('Kinase not found. Please check and try again.', 'danger')
    
    return render_template('HumanKinases.html', title='List of Human Kinases', form=form)
      

@app.route("/Phosphosite")
def Phosphosite():
    return render_template('Phosphosite.html', title='Phosphosite Search')


@app.route("/Inhibitors", methods = ['GET', 'POST'])
def Inhibitors():
    return render_template('Inhibitors.html', title='Inhibitors')


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
