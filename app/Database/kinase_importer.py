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

from .db_setup import s
from .kinase_declarative import *

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
        substrate_match = s.query(SubstrateMeta).filter(SubstrateMeta.substrate_uniprot_number==row["SUB_ACC_ID"]).all()
        if substrate_match == []:
            obj = SubstrateMeta(substrate_gene_name=row["SUB_GENE"],
                                substrate_uniprot_number=row["SUB_ACC_ID"],
                                substrate_url=row["URL"])
            s.add(obj)
s.commit()

#Adding in the substrate name and the uniprot entry from Mo's dataset
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

"""
#creating a SubstrateMeta table            
with open(substrates) as f:
    reader = csv.DictReader(f)
    for row in reader:
        #deduplication
        #look in the SubstrateMeta table for existing entry with the same substrate name 
        substrate_match = s.query(SubstrateMeta).filter(SubstrateMeta.substrate_uniprot_number==row["SUB_ACC_ID"]).all() 
        #if there is no existing substrate entry, create a new SubstrateMeta instance 
        if substrate_match == []:
            obj = SubstrateMeta(substrate_name=row["SUBSTRATE"], 
                            substrate_gene_name=row["SUB_GENE"],
                            substrate_uniprot_entry=row["SUB_ENTRY_NAME"],
                            substrate_uniprot_number=row["SUB_ACC_ID"])
            s.add(obj)
s.commit()
    

#importing urls into the SubstrateMeta table
with open(phosphosites) as f:
    reader = csv.DictReader(f)
    for row in reader: #loop through each row in the csv
        substrate_meta_match = s.query(SubstrateMeta).filter(SubstrateMeta.substrate_uniprot_number==row["SUB_ACC_ID"]).all() #find the substrate obj that has the same uniprot number
        if substrate_meta_match == []: #if no such entry found
            continue      #skip to the next row
        substrate_meta = substrate_meta_match[-1] #get the substrate obj
        substrate_meta.substrate_url = row["URL"] #assign the missing url value
        s.add(substrate_meta)
s.commit()
"""

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
        #append the kinase_obj in the kinases column of the relationship table between phosphosite and kinase
        obj.kinases.append(kinase_meta) #if the phosphosite object already exits then this new row would be due to a different kinase 
        s.add(obj)
s.commit()       

"""
#creating a InhibitorMeta table
with open(inhibitors) as f:
    reader = csv.DictReader(f)
    for row in reader:
        #Look in the KinaseGeneName and get the obj that has the same gene name as that of the row, then get the KinaseGeneMeta obj that has the same gene name
        gene_match = s.query(KinaseGeneMeta).join(KinaseGeneName).filter(KinaseGeneMeta.gene_name==KinaseGeneName.gene_name).filter(KinaseGeneName.gene_alias==row["Target"]).all()
        #print(row["Target"])
        #if there is no such entry in the KinaseGeneMeta, it will return an empty list
        if gene_match == []:
            #print(row["Target"])
            continue #skip
        else:
            gene_meta = gene_match[-1] #if there's such an entry that's already existed, then it will return an obj; -1 or 0 will get the obj
        inhibitor_query = s.query(InhibitorMeta).filter(InhibitorMeta.inhibitor==row["Inhibitor"]).all() # check in the InhibitorMeta for the existence of InhibitorMeta obj with the same name
        if inhibitor_query != []: # if there is already a previously registered InhibitorMeta object, then get the latest obj (there really shouldn't be any duplication but sometimes databse can glitch)
            obj = inhibitor_query[-1]
        else: #create the InhibitorMeta object
            obj = InhibitorMeta(inhibitor_name=row["Inhibitor"],
                            molecular_weight=row["MW"],
                            empirical_formula=row["Emperical Formula"],
                            smiles = row[],
                            pub_chemid = row[],
                            inchi = row[],
                            images_url=row["Images"])
        gene_meta.inhibitors.append(obj) #append the InhibitorMeta object under the inhibitors virtual column in the respective KinaseGeneMeta obj
        s.add(obj)
s.commit()    
"""

#creating an InhibitorMeta table
with open(inhibitors) as f:
    reader = csv.DictReader(f)
    for row in reader:
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
        target_genes = row["Target"].split(",")
        for gene in target_genes:
            gene_match = s.query(KinaseGeneMeta).join(KinaseGeneName).filter(KinaseGeneMeta.gene_name==KinaseGeneName.gene_name).\
                            filter(KinaseGeneName.gene_alias==gene).all()
            if gene_match == []:
                continue
            else:
                gene_obj = gene_match[-1]
            gene_obj.inhibitors.append(inhibitor_obj)
            s.add(gene_obj)
s.commit()


#creating a new InhibitorName table
with open(inhibitors) as f:
    reader = csv.DictReader(f)
    for row in reader:
        inhibitor_match = s.query(InhibitorMeta).filter(InhibitorMeta.inhibitor_name==row["Inhibitor"]).all()
        if inhibitor_match == []:
            continue
        else:
            inhibitor_meta_obj = inhibitor_match[-1]
        inhibitor_alias_list = row["Synonyms"].split(",")
        if row["Synonyms"] == "": #to catch those row with nothing
            inhibitor_alias_list.remove("")
        if row["Inhibitor"] not in inhibitor_alias_list: # if the alias do not have self-referencing name
            inhibitor_alias_list.append(row["Inhibitor"])
        for alias in inhibitor_alias_list:
            inhibitor_alias_match = s.query(InhibitorName).filter(InhibitorName.inhibitor_alias==alias).all()
            if inhibitor_alias_match != []:
                continue
            else:
                inhibitor_name_obj = InhibitorName(inhibitor_alias = alias)
                inhibitor_meta_obj.inhibitor_aliases.append(inhibitor_name_obj)
                s.add(inhibitor_name_obj)
            s.add(inhibitor_meta_obj)
    s.commit()





"""
#creating an InhibitorName table
with open(inhibitors) as f:
    reader = csv.DictReader(f)
    for row in reader:
        #check for the existence of the entry in InhibitorMeta with the same inhibitor name as the name in the csv
        inhibitor_meta_match = s.query(InhibitorMeta).filter(InhibitorMeta.inhibitor_name==row["Target"]).all()
        #if there is no such entry, it will return an empty list
        if inhibitor_meta_match == []: 
            continue  #skip it
        else:
            inhibitor_meta_obj = inhibitor_meta_match[-1] #teachnically, if there is already one, there should only be one but all returns a list;-1 or 0 will return the obj within the list
        inhibitor_aliases = row["Synonymns"].split(",") #the aliases will be in a string of list into multiple strings
        if row["Inhibitor"] not in inhibitor_aliases: #look for self-referencing alias; ie one of the name in the gene alias has to be itself
            inhibitor_name_obj = InhibitorName(gene_alias=row["Inhibitor"])
            inhibitor_meta_obj.inhibitor_aliases.append(inhibitor_name_obj)
            s.add(inhibitor_name_obj)
        for alias in inhibitor_aliases: #loop through each alias in the inhibitor_aliases
            inhibitor_alias_match = s.query(InhibitorName).filter(InhibitorName.inhibitor_alias==alias).all() #check for the previous records of such aliases
            if inhibitor_alias_match != []: #if it already exists; skip it
                continue
            inhibitor_name_obj = InhibitorName(gene_alias=alias) #otherwise, create it as an instance of InhibitorName
            inhibitor_meta_obj.inhibitor_aliases.append(inhibitor_name_obj) #append the alias in the inhibitor_alias virtual column of the InhibitorMeta obj row
            s.add(inhibitor_name_obj)
        s.add(inhibitor_meta_obj)
s.commit()
"""
    
    
    
    
    