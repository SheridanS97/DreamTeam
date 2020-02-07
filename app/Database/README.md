README.md
Database_query.ipynb, Database_query_II.ipynb and Protocol IronFox MK II.ipynb all documents the trial and debug codes where the functions to query the kinase_database.db come from.

__init__.py is needed to make Database a module so that it can be imported.

kinase_declarative.py is the file where the classes for the objects are written

kinase_importer.py is the file the codes importing the dataset from csv into database are kept.

kinase_functions.py is the file where the functions to retrieve data from database are kept.

schema_for_kinase_db.pdf shows the design of the schema for the database.

Documentation.txt documents the ideas behind the schema design as well as the reason why SQLAlchemy is chosen.
