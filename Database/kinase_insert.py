#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Jan 19 14:13:37 2020

@author: han
"""

#import the library
import os
import csv
import json
from kinase_declarative import *
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

#create the engine
engine = create_engine("sqlite:///kinase_database.db")
Base.metadata.bind = engine

#create the session
session = sessionmaker()
s = session()
home = os.path.expanduser("~")
base_dir = home + "/Projects/Uni/BioInformaticsGroupPorject/DreamTeam/Data_mining/"
protein_names_and_aliases = base_dir + "Protein_names_and_aliases/"
clean_human_kinase = protein_names_and_aliases + "clean_human_kinase.csv"
gene_aliases = protein_names_and_aliases + "meta_names.csv"

#import the data into the database
#creating KinaseGeneMeta table
with open(clean_human_kinase, "r") as f:
    reader = csv.DictReader(f)
    for r in reader:
        obj = KinaseGeneMeta(uniprot_number=r["uniprot_number"], 
                             uniprot_entry=r["uniprot_identifier"],
                             gene_name = r["gene_name"],
                             kinase_family = r["family"])
        s.add(obj)
s.commit()
        
#creating KinaseGeneName table
with open(gene_aliases) as f:
    reader = csv.DictReader(f)
    for r in reader:
        # Lookup matching KinaseGeneMeta object
        kinase_meta_matches = s.query(KinaseGeneMeta).filter(KinaseGeneMeta.gene_name == r['Gene_name']).all()
        if kinase_meta_matches == []:
            continue # If no match found go to next loop
        else:
            kinase_meta = kinase_meta_matches[-1]
        kinase_meta.protein_name = r["Protein_name"] # Append missing protein_name field to kinase_meta (KinaseGeneMeta) object
        gene_aliases = json.loads(r["Gene_aliases"].replace("'",'"')) # Convert string to list
        for alias in gene_aliases:
            #obj = KinaseGeneName(gene_name=r['Gene_name'],
            #                     gene_alias=alias)
            
            # START OF DEDUPLICATION
            existing_match = s.query(KinaseGeneName).filter(KinaseGeneName.gene_alias == alias).all()
            if existing_match != []:
                continue # If match found go to next loop
            # END OF DEDUPLICATION
            obj = KinaseGeneName(gene_alias=alias) # Creating the new KinaseGeneName object
            kinase_meta.gene_aliases.append(obj) # Linking the new KinaseGeneName object to the relevant KinaseGeneMeta object
            s.add(obj) # Done creating KinaseGeneName object, so save
        s.add(kinase_meta) # Done editing KinaseGeneMeta, so save it
s.commit() # Write changes to DB
            
            
            
