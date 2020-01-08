from flask import Flask, render_template, url_for
app = Flask(__name__)

posts = [
    {
        'Name': 'Mohamed Golaid',
        'Surname': 'A Msc Bioinformatics student, who loves coding',
    },
    {
        'Name': 'Han Ooi',
        'Surname': 'A Msc Bioinformatics student, who loves coding as well',
    }
]


@app.route("/")
@app.route("/home")
def home():
    return render_template('home.html', title='Home')

@app.route("/Data_Upload")
def Data_Upload():
    return render_template('Data_Upload.html', title='Data_Upload')
    
@app.route("/about")
def about():
    return render_template('about.html', posts=posts)


if __name__ == '__main__':
    app.run(debug=True)
