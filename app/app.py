import os
from flask import Flask, render_template, url_for, flash, redirect, request
from werkzeug.utils import secure_filename

from Database.kinase_functions import *
from forms import *
from user_data_input_edited import *

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
                    return redirect(url_for('Data_Upload'))
                if InputFile and allowed_file(InputFile.filename):
                    filename = secure_filename(InputFile.filename)
                    uploads_dir = os.path.join(app.instance_path, 'Data_Upload')
                    if not os.path.exists(uploads_dir):
                        os.makedirs(uploads_dir)
                    InputFile.save(os.path.join(uploads_dir, secure_filename(InputFile.filename)))
                    flash ("Upload Successful", "info")
                    return redirect(url_for('Parameter', filename=filename ))
                else:
                    flash('Incorrect selected file', 'danger')
    return render_template('Data_Upload.html', title='Data Upload', form=form)


@app.route("/upload/Parameters/<filename>", methods = ['GET', 'POST'])
def Parameter(filename):
    form = Parameters()
    if request.method == "POST":
        if form.validate_on_submit():
            PValue = form.PValue.data
            Fold = form.Fold.data
            Coeff = form.Coefficience.data
            return redirect(url_for('Visualisation' ,filename=filename, PValue=PValue, Fold=Fold, Coeff=Coeff ))
        else:
            flash("P-Value Threshold must be between 0 - 0.05 and Coefficience of Variance Threshold must be a whole number between 0 to 100", "danger")
    return render_template('data_parameter.html', form=form)


@app.route("/upload/Parameters/<filename>/<PValue>/<Fold>/<Coeff>")
def Visualisation(filename, PValue, Fold, Coeff):
    VolcanoPlot1 = VolcanoPlot_Sub(filename)
    VolcanoPlot2 = VolcanoPlot(filename)
    Enrichment = EnrichmentPlot(filename)
    return render_template('data_analysis_results.html',filename=filename, PValue=PValue, Fold=Fold, Coeff=Coeff, VolcanoPlot1=VolcanoPlot1, VolcanoPlot2=VolcanoPlot2, Enrichment=Enrichment)   


@app.route("/HumanKinases", methods = ['GET', 'POST'])
def HumanKinases():
    form=Kinase() 
    search_kinase = form.search.data
    list_aliases = get_all_aliases() #this function returns a list of all kinase aliases

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
    Phospho_form = Phosphosite()
    Substrate_form = Substrate()
    chr_number = Phospho_form.chromosome_number.data

    if Substrate_form.validate_on_submit():
        substrate_input = Substrate_form.search.data
        return redirect(url_for('results_phosphosite',substrate_input=substrate_input) )
    return render_template('Phosphosite.html', title='Phosphosite Search',  Substrate_form=Substrate_form, Phospho_form=Phospho_form)

@app.route("/Phosphosite_result/<substrate_input>", methods= ['GET', 'POST'])
def results_phosphosite(substrate_input):
    substrate_info = get_phosphosite_meta_from_substrate(substrate_input)
    return render_template('results_phosphosite.html', substrate_info=substrate_info)

@app.route("/Inhibitors", methods = ['GET', 'POST'])
def Inhibitors():
    ALL_inhibitors = get_all_inhibitors_meta()
    return render_template('inhibitors.html', title='Inhibitors', ALL_inhibitors=ALL_inhibitors)

@app.route("/Inhibitors/<inhibitor>")
def Individual_Inhibitors(inhibitor):
    Individual_Inhibitor = get_inhibitor_meta_from_inhibitor(inhibitor)
    return render_template('Individual_inhibitor.html', title='Individual Inhibitors', Individual_Inhibitor=Individual_Inhibitor, inhibitor=inhibitor)


@app.route("/help")
def Help():
    return render_template('help.html', title='Help')


@app.route("/about")
def about():

    posts = [
    {
        'Name': 'Mohamed Golaid',
        'Description': 'A Msc Bioinformatics student, who loves coding',
    },
    {
        'Name': 'Han Ooi',
        'Description': 'A highly masculine Msc Bioinformatics bro, who loves pumping iron and coding as well',
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
