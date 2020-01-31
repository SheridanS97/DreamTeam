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
base_dir = home + "/Projects/Uni/BioInformaticsGroupPorject/DreamTeam/Data_mining/" #change base_dir to appropriate dir
protein_names_and_aliases = base_dir + "Protein_names_and_aliases/"
clean_human_kinase = protein_names_and_aliases + "clean_human_kinase.csv"
gene_aliases = protein_names_and_aliases + "meta_names.csv"
subcellular_location = base_dir + "Subcellular_location/Subcellular_location.csv"
substrates = base_dir + "Phosphosites/new_clean_human_kinase_substrates.csv"
inhibitors = base_dir + "Inhibitor/Final_inhibitors.csv"
phosphosites = base_dir + "Genomic_location_of_PS/Phosphosite_genomic_locations.csv"


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
            

#creating the KinaseSubcellularLocation table
with open(subcellular_location) as f:
    reader = csv.DictReader(f)
    for row in reader:
        gene_meta_match = s.query(KinaseGeneMeta).join(KinaseGeneName).filter(KinaseGeneMeta.gene_name==KinaseGeneName.gene_name).filter(KinaseGeneName.gene_alias==row["Gene Name"]).one()
        obj = KinaseSubcellularLocation(gene_name=row["Gene Name"], subcellular_location=row["Subcellular Location"])
        gene_meta_match.subcellular_locations.append(obj)
        s.add(obj)
s.commit()


#uncomment this during production
#creating a SubstrateMeta table            
with open(substrates) as f:
    reader = csv.DictReader(f)
    for row in reader:
        #deduplication
        substrate_match = s.query(SubstrateMeta).filter(SubstrateMeta.substrate_uniprot_number==row["SUB_ACC_ID"]).all() #
        if substrate_match == []:
            obj = SubstrateMeta(substrate_name=row["SUBSTRATE"], 
                            substrate_gene_name=row["SUB_GENE"],
                            substrate_uniprot_entry=row["SUB_ENTRY_NAME"],
                            substrate_uniprot_number=row["SUB_ACC_ID"])
            s.add(obj)
s.commit()
    

#creating a PhosphositeMeta table
with open(phosphosites) as f:
    reader = csv.DictReader(f)
    for row in reader:
        #get the kinase obj that matches the kinase for the row
        kinase_matches = s.query(KinaseGeneMeta).join(KinaseGeneName).filter(KinaseGeneMeta.gene_name==KinaseGeneName.gene_name).filter(KinaseGeneName.gene_alias == row["Kinase gene"]).all()
        if kinase_matches == []: #if the kinase name is not found in the alias or gene name of the database
            # print(row) #debug code to find out which line was it that was returning empty
            continue #skip that row
        else:
            kinase_meta = kinase_matches[-1] #otherwise get the obj; -1 because .all returns a list of memory address
        #get the substrate_object that matched the gene name of the substrate
        substrate_match_list = s.query(SubstrateMeta).filter(SubstrateMeta.substrate_gene_name==row["SUB_GENE"]).all()
        if substrate_match_list == []: #if there is no such substrate in the database, it will return an empty list
            continue #skip it if there's no such substrate
        else:
            substrate_match = substrate_match_list[-1] #if there's such substrate, we're betting on that there's no duplication of the substrate
        #deduplication
        query = s.query(PhosphositeMeta) # query the PhosphositeMeta table for the existence of phosphosite with the same substrate name as the substrate_object
        query = query.filter(PhosphositeMeta.substrate_meta_id==substrate_match.substrate_id)
        query = query.filter(PhosphositeMeta.phosphosite==row["PS"])
        phosphosite_match = query.all()
        if phosphosite_match != []: #if the phosphosite_obj is not empty, ie it already exists; retrieve it
            obj = phosphosite_match[-1]
        else:   #if it doesn't yet exist, create the obj as an instance of PhosphositeMeta
            obj = PhosphositeMeta(substrate_meta_id=substrate_match.substrate_id,
                                  phosphosite=row["PS"],
                                  chromosome=row["Chromosome"],
                                  karyotype_band=row["Karyotype band"],
                                  strand=row["Strand"],
                                  start_position=row["Start co"],
                                  end_position=row["End co"],
                                  neighbouring_sequences=row["Neighbouring amino acids +/-7"])
            substrate_match.phosphosites.append(obj) #append the phosphosite_obj to the phosphosites backref column in the corresponding substrate_obj
        obj.kinases.append(kinase_meta) #append the kinase_obj in the kinases column of the relationship table between phosphosite and kinase
        s.add(obj)
s.commit()       


#creating a Inhibitor table
with open(inhibitors) as f:
    reader = csv.DictReader(f)
    for row in reader:
        gene_match = s.query(KinaseGeneMeta).join(KinaseGeneName).filter(KinaseGeneMeta.gene_name==KinaseGeneName.gene_name).filter(KinaseGeneName.gene_alias==row["Target"]).all()
        #print(row["Target"])
        if gene_match == []:
            #print(row["Target"])
            continue
        else:
            gene_meta = gene_match[-1]
        inhibitor_query = s.query(Inhibitor).filter(Inhibitor.inhibitor==row["Inhibitor"]).all()
        if inhibitor_query != []:
            obj = inhibitor_query[-1]
        else:
            obj = Inhibitor(inhibitor=row["Inhibitor"],
                            molecular_weight=row["MW"],
                            empirical_formula=row["Emperical Formula"],
                            images_url=row["Images"])
        gene_meta.inhibitors.append(obj)
        s.add(obj)
s.commit()    