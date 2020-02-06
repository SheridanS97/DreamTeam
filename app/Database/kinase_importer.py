#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Jan 19 14:13:37 2020

@author: han
"""

import csv
import json
# import the library
import os

from db_setup import s
from kinase_declarative import *

#setting the directories of the files
#these will need to be changed accordingly if one were to generate the database
home = os.path.expanduser("~")
base_dir = home + "/Projects/Uni/BioInformaticsGroupPorject/DreamTeam/Data_mining/" #change base_dir to appropriate dir
protein_names_and_aliases = base_dir + "Protein_names_and_aliases/"
clean_human_kinase = protein_names_and_aliases + "clean_human_kinase.csv"
gene_aliases = protein_names_and_aliases + "meta_names.csv"
subcellular_location = base_dir + "Subcellular_location/Subcellular_location.csv"
substrates = base_dir + "Phosphosites/new_clean_human_kinase_substrates.csv"
inhibitors = base_dir + "inhi/Complete_inhibitor.csv"
phosphosites = base_dir + "Genomic_locations_of_phosphosites/Final_Phosphosite_genomic_locations.csv"


#import the data into the database
#creating KinaseGeneMeta table
with open(clean_human_kinase, "r") as f:
    #used DictReader to read each row into a dictionary
    reader = csv.DictReader(f)
    for r in reader:
        #create the Kinase Gene Meta instance
        #protein name aren't added to the instance because its information is not within this csv
        obj = KinaseGeneMeta(uniprot_number=r["uniprot_number"], 
                             uniprot_entry=r["uniprot_identifier"],
                             gene_name = r["gene_name"],
                             kinase_family = r["family"])
        s.add(obj) #add the instance to the session
s.commit()  #commit the session into the database
        

#creating KinaseGeneName table
with open(gene_aliases) as f:
    reader = csv.DictReader(f)
    for r in reader:
        # Lookup matching KinaseGeneMeta object
        kinase_meta_matches = s.query(KinaseGeneMeta).filter(KinaseGeneMeta.gene_name == r['Gene_name']).all()
        if kinase_meta_matches == []:
            continue # If no match found go to next loop
        else:
            kinase_meta = kinase_meta_matches[-1] #we're betting that there's only one obj that returns within the list
        kinase_meta.protein_name = r["Protein_name"] # Append missing protein_name field to kinase_meta (KinaseGeneMeta) object
        gene_aliases = json.loads(r["Gene_aliases"].replace("'",'"')) # Convert string to list; othewise the thing returned is a string of list
        for alias in gene_aliases: 
            # start of deduplication
            existing_match = s.query(KinaseGeneName).filter(KinaseGeneName.gene_alias == alias).all()
            if existing_match != []:
                continue # If match found go to next loop
            # end of deduplication
            obj = KinaseGeneName(gene_alias=alias) # so if the alias has not been created yet; then create the new KinaseGeneName object
            kinase_meta.gene_aliases.append(obj) # Linking the new KinaseGeneName object to the relevant KinaseGeneMeta object
            s.add(obj) # Done creating KinaseGeneName object, so save
        s.add(kinase_meta) # Done editing KinaseGeneMeta, so save it
s.commit() # Write changes to DB
            

#creating the KinaseSubcellularLocation table
with open(subcellular_location) as f:
    reader = csv.DictReader(f)
    #for each row in the df
    for row in reader:
        #look for a matching KinaseGeneMeta object with the same name as given in csv; via KinaseGeneName to KinaseGeneMeta; just in case it was one of the aliases that was used
        gene_meta_match = s.query(KinaseGeneMeta).join(KinaseGeneName).filter(KinaseGeneMeta.gene_name==KinaseGeneName.gene_name).filter(KinaseGeneName.gene_alias==row["Gene Name"]).one()
        #create the KinaseSubcellularLocation object 
        obj = KinaseSubcellularLocation(gene_name=row["Gene Name"], subcellular_location=row["Subcellular Location"])
        #append the KinaseSubcellularLocation object to the matching KinaseGeneMeta obj
        gene_meta_match.subcellular_locations.append(obj)
        s.add(obj)
s.commit()

#create a SubstrateMeta table
with open(phosphosites) as f:
    reader = csv.DictReader(f)
    for row in reader:
        #look for a SubstrateMeta obj that has the same uniprot number
        substrate_match = s.query(SubstrateMeta).filter(SubstrateMeta.substrate_uniprot_number==row["SUB_ACC_ID"]).all()
        if substrate_match == []:
            obj = SubstrateMeta(substrate_gene_name=row["SUB_GENE"],
                                substrate_uniprot_number=row["SUB_ACC_ID"],
                                substrate_url=row["URL"])
            s.add(obj)
s.commit()

#Adding in the substrate name and the uniprot entry from Mo's dataset
#Filling the empty cells in SubstrateMeta
with open(substrates) as f:
    reader = csv.DictReader(f)
    for row in reader:
        substrates_meta_match = s.query(SubstrateMeta).filter(SubstrateMeta.substrate_uniprot_number==row["SUB_ACC_ID"]).all()
        if substrates_meta_match == []:
            continue
        substrate_meta = substrates_meta_match[-1]
        substrate_meta.substrate_name = row["SUBSTRATE"]
        substrate_meta.substrate_uniprot_entry = row["SUB_ENTRY_NAME"]
        s.add(substrate_meta)
s.commit()

#creating a PhosphositeMeta table
with open(phosphosites) as f:
    reader = csv.DictReader(f)
    for row in reader:
        #get the KinaseGeneMeta obj that matches the kinase name of the row
        kinase_matches = s.query(KinaseGeneMeta).filter(KinaseGeneMeta.uniprot_number == row["KIN_ACC_ID"]).all()
        if kinase_matches == []: #if the kinase name is not found in the alias or gene name of the database
            # print(row) #debug code to find out which line was it that was returning empty
            continue #skip that row
        else:
            kinase_meta = kinase_matches[-1] #otherwise get the obj; -1 because .all returns a list of memory address
        #get the substrate_object that matched the gene name of the substrate
        substrate_match_list = s.query(SubstrateMeta).filter(SubstrateMeta.substrate_uniprot_number==row["SUB_ACC_ID"]).all()
        if substrate_match_list == []: #if there is no such substrate in the database, it will return an empty list
            continue #skip it if there's no such substrate
        else:
            substrate_match = substrate_match_list[-1] #if there's such substrate, we're betting on that there's no duplication of the substrate
        #deduplication
        query = s.query(PhosphositeMeta) # query the PhosphositeMeta table for the existence of phosphosite with the same substrate name as the substrate_object
        query = query.filter(PhosphositeMeta.substrate_meta_id==substrate_match.substrate_id)
        query = query.filter(PhosphositeMeta.phosphosite==row["SUB_MOD_RSD"])
        phosphosite_match = query.all()
        if phosphosite_match != []: #if the phosphosite_obj is not empty, ie it already exists; retrieve it
            obj = phosphosite_match[-1]
        else:   #if it doesn't yet exist, create the obj as an instance of PhosphositeMeta
            obj = PhosphositeMeta(substrate_meta_id=substrate_match.substrate_id,
                                  phosphosite=row["SUB_MOD_RSD"],
                                  chromosome=row["Chromosome/scaffold name"],
                                  karyotype_band=row["Karyotype band"],
                                  strand=row["Strand"],
                                  start_position=row["Start co"],
                                  end_position=row["End co"],
                                  neighbouring_sequences=row["SITE_+/-7_AA"])
            substrate_match.phosphosites.append(obj) #append the phosphosite_obj to the phosphosites backref column in the corresponding substrate_obj
        obj.kinases.append(kinase_meta) #if the phosphosite object already exits then this new row would be due to a different kinase
        s.add(obj)
s.commit()

#creating an InhibitorMeta table
with open(inhibitors) as f:
    reader = csv.DictReader(f)
    for row in reader:
        #deduplication: looking for any obj with the name already
        inhibitor_meta_match = s.query(InhibitorMeta).filter(InhibitorMeta.inhibitor_name==row["Inhibitor"]).all()
        if inhibitor_meta_match != []:
            inhibitor_obj = inhibitor_meta_match[-1]
        else:
            chembl_id = row["ID"]
            if chembl_id == "None":  # a couple of rows had None for chembl id
                chembl_id = None
            inhibitor_obj = InhibitorMeta( inhibitor_name = row["Inhibitor"],
                                        molecular_weight = row["MW"],
                                        smiles = row["Smiles"],
                                        chembl_id = chembl_id,
                                        inchi = row["InChiKey"],
                                        images_url = row["Images"])
            s.add(inhibitor_obj)
s.commit()

#adding genes to InhibitorMeta
with open(inhibitors) as f:
    reader = csv.DictReader(f)
    for row in reader:
        #look for the InhibitorMeta that matches the name
        inhibitor_meta_match = s.query(InhibitorMeta).filter(InhibitorMeta.inhibitor_name == row["Inhibitor"]).all()
        if inhibitor_meta_match == []: #if not found just skip it
            continue
        inhibitor_obj = inhibitor_meta_match[-1] #take the obj from the list
        target_genes = row["Target"].replace(" ", "").split(",")  #remove the empty spaces after comma and split them by comma
        for gene in target_genes: #loop through the genes
            gene_match = s.query(KinaseGeneMeta).join(KinaseGeneName).filter(KinaseGeneMeta.gene_name==KinaseGeneName.gene_name).\
                            filter(KinaseGeneName.gene_alias==gene).all()
            if gene_match == []: #if the gene is not found in the database
                continue
            gene_obj = gene_match[-1]
            inhibitor_obj.kinases.append(gene_obj) #append the kinase genes to the inhibitor obj
        s.add(inhibitor_obj)
s.commit()


#creating a new InhibitorName table
with open(inhibitors) as f:
    reader = csv.DictReader(f)
    for row in reader:
        #look for an inhibitor obj with matching name
        inhibitor_match = s.query(InhibitorMeta).filter(InhibitorMeta.inhibitor_name==row["Inhibitor"]).all()
        if inhibitor_match == []: #if it doesn't exist skip it
            continue
        else:
            inhibitor_meta_obj = inhibitor_match[-1]
        inhibitor_alias_list = row["Synonyms"].split(",") #split the alias name into a list
        if row["Synonyms"] == "": #to catch those row with nothing
            inhibitor_alias_list.remove("") #remove the null, leaviing only an empty list
        if row["Inhibitor"] not in inhibitor_alias_list: # if the alias do not have self-referencing name
            inhibitor_alias_list.append(row["Inhibitor"]) #append its own name into the alias list
        for alias in inhibitor_alias_list:
            inhibitor_alias_match = s.query(InhibitorName).filter(InhibitorName.inhibitor_alias==alias).all() #check to see if the alias obj has been created
            if inhibitor_alias_match != []:
                continue
            else:
                inhibitor_name_obj = InhibitorName(inhibitor_alias = alias)
                inhibitor_meta_obj.inhibitor_aliases.append(inhibitor_name_obj)
                s.add(inhibitor_name_obj)
            s.add(inhibitor_meta_obj)
    s.commit()

