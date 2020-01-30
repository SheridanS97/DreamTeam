#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jan 24 16:40:24 2020

@author: zho30
"""

#calling the library
from kinase_declarative import * #please make sure kinase_declarative.py is in the same folder
from sqlalchemy import create_engine, or_, and_
from sqlalchemy.orm import sessionmaker
from pprint import pprint #don't really need this if running in script

#create engine and bine the engine
engine = create_engine("sqlite:///kinase_database.db")
Base.metadata.bind = engine

#create a session object
session = sessionmaker(bind=engine)
s = session()

#Please refer to Database_query_II for more information
#A list of functions is available on Database query II

#Intermediate kinase results page
def get_gene_alias_protein_name(kinase_input):
    """ (str) --> list of dictionary
    Returns a list of dictionary.
    In the dictionary, there are gene name and protein name.
    Returns empty list when no match is found.
    >> kin = "AKT"
    >> get_gene_alias_protein_name(kin)
    [{'Gene_Name': 'AKT1', 'Gene aliases': ['AKT1', 'PKB', 'RAC'], 'Protein_Name': 'RAC-alpha serine/threonine-protein kinase'}, 
    {'Gene_Name': 'AKT2', 'Gene aliases': ['AKT2'], 'Protein_Name': 'RAC-beta serine/threonine-protein kinase'}, 
    {'Gene_Name': 'AKT3', 'Gene aliases': ['AKT3', 'PKBG'], 'Protein_Name': 'RAC-gamma serine/threonine-protein kinase'}]
    >> get_gene_alias_protein_name("Q9Y243")
    [{'Gene_Name': 'AKT3', 'Gene aliases': ['AKT3', 'PKBG'], 'Protein_Name': 'RAC-gamma serine/threonine-protein kinase'}]
    """
    like_kin = "%{}%".format(kinase_input) #changing the user input so that it's usable with like
    tmp = []
    #query KinaseGeneMeta and KinaseGeneName for entry that resembled the user input
    kinase_query = s.query(KinaseGeneMeta).join(KinaseGeneName).filter(or_(KinaseGeneName.gene_alias.like(like_kin), KinaseGeneMeta.uniprot_entry.like(like_kin),\
                                   KinaseGeneMeta.uniprot_number.like(like_kin), KinaseGeneMeta.protein_name.like(like_kin))).all()
    #put the results of the object into a dictionary
    for meta in kinase_query:
        results = {}
        results["Gene_Name"] = meta.to_dict()["gene_name"]
        results["Gene aliases"] = meta.to_dict()["gene_aliases"]
        results["Protein_Name"] = meta.to_dict()["protein_name"]
        tmp.append(results)
    return tmp

#Individual kinase page
#Function to return gene name, family, protein name, uniprot entry, uniprot number.
def get_gene_metadata_from_gene(kinase_str):
    """ (str) --> dict
    Takes in a gene name as a string then output a dictionary.
    Raises error if wrong or invalid gene name is given.
    >> get_gene_metadata_from_gene("MAPK1")
    {'gene_name': 'MAPK1', 
    'kinase_family': 'CMGC Ser/Thr protein kinase family',
    'protein_name': 'Mitogen-activated protein kinase 1',
    'uniprot_entry': 'MK01_HUMAN',
    'uniprot_number': 'P28482'}
    """
    #query gene_name in KinaseGeneMeta for user input
    kinase_obj = s.query(KinaseGeneMeta).filter(KinaseGeneMeta.gene_name==kinase_str).one()
    return kinase_obj.to_dict()

#Function to return subcellular location of kinase
def get_subcellular_location_from_gene(kinase_gene):
    """ (str) --> dict
    Returns a list of dictionary.
    The dictionary has the gene as the key and the subcellular location in the list.
    >> get_subcellular_location_from_gene('MAPK1')
    {'Gene_Name': 'MAPK1', 'Subcellular_Locations': ['Cytoplasm', 'Cytoskeleton', 'Membrane', 'Nucleus', 'Caveola', 
    'Microtubule Organizing Center', 'Spindle', 'Plasma Membrane', 'Mitotic Spindle', 'Focal Adhesion', 'Cytosol', 
    'Golgi Apparatus', 'Late Endosome', 'Early Endosome', 'Mitochondrion', 'Azurophil Granule Lumen', 'Nucleoplasm', 
    'Extracellular Region', 'Cell', 'Pseudopodium', 'Perikaryon', 'Protein-Containing Complex', 'Dendrite Cytoplasm', 
    'Axon', 'Postsynaptic Density']}
    """
    tmp = []
    results = {}
    results["Gene_Name"] = kinase_gene #initialise the dictionary with the gene name of the user input
    #query KinaseSubcellularLocation through KinaseGeneMeta via KinaseGeneName
    kinase_query = s.query(KinaseSubcellularLocation).join(KinaseGeneMeta).join(KinaseGeneName).\
    filter(KinaseGeneName.gene_alias==kinase_gene).filter(KinaseGeneMeta.gene_name==KinaseGeneName.gene_name).\
    filter(KinaseGeneMeta.gene_name==KinaseSubcellularLocation.gene_name).all()
    #.all returns a list of obj, use for loop 
    for row in kinase_query: #loop through all the obj representation in kinase_query
        tmp.append(row.subcellular_location) #append all the subcellular location to tmp
    results["Subcellular_Locations"] = tmp
    return results

#Function to return the inhibitors from a kinase
def get_inhibitors_from_gene(kinase_gene):
    """ (str) --> list
    Take a string and return a list of dictionaries.
    Returns empty list if there are no inhibitors.
    >> get_inhibitors_from_gene("SGK1")
    ['GSK650394A', 'SGK-Sanofi-14i','SGK1-Sanofi-14g', 'SGK1-Sanofi-14h', 'SGK1-Sanofi-14n']
    """
    results = []
    #query KinaseGeneMeta through KinaseGeneName
    kinase_query = s.query(KinaseGeneMeta).join(KinaseGeneName).filter(KinaseGeneMeta.gene_name==KinaseGeneName.gene_name).\
    filter(KinaseGeneName.gene_alias==kinase_gene).all()
    #.all() returns a list, if a gene does not have an inhibitor, it'll return an empty list
    if len(kinase_query) == 0:
        return []
    #if .all() has an inhibitor, it should only be one entry with that gene name, thus [-1]
    for inhibitor in kinase_query[-1].inhibitors:
        results.append(inhibitor.inhibitor)
    return results
    
#Function to return substrates and phosphosites from a kinase
def get_substrates_phosphosites_from_gene(kinase_gene):
    """ (str) --> dict
    Takes in a gene name of a kinase and return a dictionary of dictionaries.
    In each dictionary (inner), the key is the substrate name; the value is a list of dictionary containing the metadata
    of phosphosites.
    Returns empty dict if there are no substrates or no kinase_gene found.
    >> get_substrates_phosphosites_from_gene("JAK2")
    {'ARHGEF1': [{'phosphosite': 'Y738', 'chromosome': 19, 'karyotype_band': 'q13.2', 'strand': 1, 'start_position': 41904999, 
    'end_position': 41905001, 'neighbouring_sequences': 'WDQEAQIyELVAQTV'}],...}
    >> get_substrates_phosphosites_from_gene("empty")
    {}
    """
    tmp = {}
    #query KinaseGeneMeta for the kinase object using the user input via KinaseGeneName
    kinase_obj = s.query(KinaseGeneMeta).join(KinaseGeneName).filter(KinaseGeneName.gene_alias==kinase_gene).\
    filter(KinaseGeneMeta.gene_name==KinaseGeneName.gene_name).all()
    #.all returns a list, if an user input does not have an entry in the KinaseGeneMeta, a empty dict will be returned
    if kinase_obj == []:
        return {}
    kinase_obj = kinase_obj[-1]
    #loop through the phosphosite object in the list of phosphosites in a kinase_obj
    for phosphosite in kinase_obj.phosphosites:
        gene = phosphosite.substrate.substrate_name #get the substrate name of the phosphosite
        if gene in tmp: #if substrate has already been recorded
            tmp[gene].append(phosphosite.to_dict()) #just append the phosphosite detail to the values of the substrate .
        else: #if the substrate has not been recorded before
            tmp[gene] = [phosphosite.to_dict()] #create a new entry in the dictionary
    return tmp

#Function to return a dictionary of kinase, substrate, phosphosite
#For Sheridan's part
def get_kinase_substrate_phosphosite(sub, pho):
    """(str, str) --> dictionary
    Take in two parameters: a substrate and a phosphosite number.
    Substrate is either the substrate name, substrate gene name, substrate uniprot entry name, 
    substrate uniprot entry number.
    Return a dictionary.
    Returns empty list if there are no match found.
    Each dictionary contains the kinase, substrate and phosphosite.
    >> get_kinase_substrate_phosphosite("RRN3_HUMAN", "T200")
    {'kinase': ['MAPK9'], 'substrate': 'RRN3_HUMAN', 'phosphosite': 'T200'}
    >> get_kinase_substrate_phosphosite("empty", "T200")
    []
    >> get_kinase_substrate_phosphosite("Q9UQL6", "S498")
    {'kinase': ['CAMK1', 'CAMK2A', 'CAMK4', 'PRKAA1', 'PRKAA2', 'PRKD1', 'PRKD2', 'PRKD3'], 
    'substrate': 'Q9UQL6', 
    'phosphosite': 'S498'}
    """
    tmp = {}
    #get the PhosphositeMeta obj that has the Subtrate obj and the same phosphosite
    sub_pho_query = s.query(PhosphositeMeta).join(SubstrateMeta).filter(PhosphositeMeta.phosphosite==pho).\
    filter(SubstrateMeta.substrate_id==PhosphositeMeta.substrate_meta_id).\
    filter(or_(SubstrateMeta.substrate_gene_name==sub, SubstrateMeta.substrate_name==sub,\
               SubstrateMeta.substrate_uniprot_entry==sub, SubstrateMeta.substrate_uniprot_number==sub)).all()
    #if  there are no entry in database an empty list will be returned
    if sub_pho_query == []:
        return []
    #loop through the phosphosite obj
    for phosphosite in sub_pho_query:
        kinase_list = []
        #loop through the kinases asociated with the phosphosite
        for kinase in phosphosite.kinases:
            #append the gene name of the kinase into a list
            kinase_list.append(kinase.gene_name)
        tmp["kinase"] = kinase_list
        tmp["substrate"] = sub
        tmp["phosphosite"] = pho
    return tmp

#INHIBITOR PAGE
#Function to return ALL the meta details of ALL inhibitor
def get_all_inhibitors_meta():
    """
    Return all the meta details of every inhibitor in a list of dictionary.
    >> get_all_inhibitors_meta()
    [{'inhibitor_id': 1,
    'inhibitor': 'GSK650394A',
    'molecular_weight': 382.45,
    'images_url': 'http://www.kinase-screen.mrc.ac.uk/system/files/compounds/jpg/gsk-50394_5.jpg',
    'empirical_formula': 'C25H22N2O2',
    'kinases': [{'gene_name': 'SGK1', 'gene_alias': ['SGK1', 'SGK']}]},...]
    """
    results = []
    inhibitors = s.query(InhibitorMeta).all() #query for all the inhibitors meta within the inhibitor_meta table
    for inhibitor in inhibitors:  #loop through the inhibitor object in the list
        results.append(inhibitor.to_dict()) #append the meta detail of each inhibitor as a dictionary to the list
    return results

#Function to return the meta details of the inhibitor from an inhibitor
def get_inhibitor_meta_from_inhibitor(inhibitor_entry):
    """(str) --> dict
    Returns the meta data of the inhibitor.
    The inhibitor can be the actual name or the alias of the inhibitor. 
    Raises an error if the entry is not found. 
    >> get_inhibitor_meta_from_inhibitor("PD 184352 (CI-1040)")
    {'inhibitor': 'PD 184352 (CI-1040)', 
    'molecular_weight': 478.66,
    'images_url': 'http://www.kinase-screen.mrc.ac.uk/system/files/compounds/jpg/pd-184352_5.jpg',
    'empirical_formula': 'C17H14ClF2IN2O2',
    'kinases': [{'gene_name': 'YES1', 'gene_alias': ['YES1', 'YES']},
    {'gene_name': 'MAPK3', 'gene_alias': ['MAPK3', 'ERK1', 'PRKM3']},
    {'gene_name': 'MAP2K1', 'gene_alias': ['MAP2K1', 'MEK1', 'PRKMK1']}]}
    """
    #search in InhibitorMeta through InhibitorName for entry that matches the name of the query
    inhibitor_query = s.query(InhibitorMeta).join(InhibitorName).filter(InhibitorMeta.inhibitor_name==InhibitorName.inhibitor_name).\
    filter(InhibitorName.inhibitor_alias==inhibitor_entry).one()
    return inhibitor_query.to_dict()

#Additional functions which might come in handy later
#Function to return the meta details of an inhibitor associated with a kinase
#This function might not be needed
def get_inhibitor_meta_from_gene(kinase):
    """
    Take in a kinase gene name and return a list of dictionaries.
    Returns empty list if there is not inhibitor for the kinase.
    >> kinase = "SGK1"
    >> get_inhibitor_meta_from_gene(kinase)
    [{'inhibitor_id': 1,
    'inhibitor': 'GSK650394A',
    'molecular_weight': 382.45,
    'images_url': 'http://www.kinase-screen.mrc.ac.uk/system/files/compounds/jpg/gsk-50394_5.jpg',
    'empirical_formula': 'C25H22N2O2',
    'kinases': [{'gene_name': 'SGK1', 'gene_alias': ['SGK1', 'SGK']}]},...]
    """
    results = []
    #query for the kinase object using either the gene name, gene alias, uniprot number or uniprot entry name
    kinase_query = s.query(KinaseGeneMeta).join(KinaseGeneName).filter(KinaseGeneMeta.gene_name==KinaseGeneName.gene_name).\
    filter(or_(KinaseGeneName.gene_alias==kinase, KinaseGeneMeta.uniprot_number==kinase,\
               KinaseGeneMeta.uniprot_entry==kinase)).all()
    #if no entry was found, an empty list will be returned
    if kinase_query == []:
        return []
    #loop through the list of inhibitors stored with the KinaseGeneMeta obj
    for inhibitor in kinase_query[-1].inhibitors:
        results.append(inhibitor.to_dict())
    return results

#Function to return the phosphosite meta data from a substrate
def get_phosphosite_meta_from_substrate(substrate_input):
    """
    Returns a list of dictionaries.
    Each dictionary contains the meta details of the phosphosite for the same substrate.
    Returns empty list if no data was found for the substrate.
    >> get_phosphosite_meta_from_substrate("P50895")
    [{'phosphosite_meta_id': 128,
    'substrate_meta_id': 232,
    'phosphosite': 'S598',
    'chromosome': 19,
    'karyotype_band': 'q13.32',
    'strand': 1,
    'start_position': 44820733,
    'end_position': 44820735,
    'neighbouring_sequences': 'GEPGLsHsGsEQPEQ'},...]
    """
    results = []
    phosphosite_query = s.query(PhosphositeMeta)\
    .filter(PhosphositeMeta.substrate_meta_id==SubstrateMeta.substrate_id)\
    .filter(or_(SubstrateMeta.substrate_gene_name==substrate_input, SubstrateMeta.substrate_name==substrate_input,\
                SubstrateMeta.substrate_uniprot_entry==substrate_input, SubstrateMeta.substrate_uniprot_number==substrate_input)).all()
    if phosphosite_query == []:
        return []
    for row in phosphosite_query:
        results.append(row.to_dict())
    return results