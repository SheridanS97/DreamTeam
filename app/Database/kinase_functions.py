#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jan 24 16:40:24 2020

@author: zho30
"""

from sqlalchemy import or_, and_

from .db_setup import s
# calling the library
from .kinase_declarative import *  # please make sure kinase_declarative.py is in the same folder


#Please refer to Database_query_II for more information
#A list of functions is available on Database query II

#Intermediate kinase results page
#create a function to return a list of human kinases
def get_all_aliases():
    """
    Returns a list of all aliases.
    """
    all_aliases = [x[0] for x in s.query(KinaseGeneName.gene_alias).all()]
    return all_aliases
get_all_aliases()


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
        results["Gene_aliases"] = meta.to_dict()["gene_aliases"]
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
    >> get_inhibitors_from_gene("MAPK1")
    ['Ulixertinib']
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
        results.append(inhibitor.inhibitor_name)
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
    if pho == "None": #if phosphosite is None (str)
        return[]
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
    'inhibitor_name': 'Abemaciclib',
    'molecular_weight': 506.3,
    'smiles': 'CCN1CCN(CC1)Cc2ccc(nc2)Nc3ncc(c(n3)c4cc5c(c(c4)F)nc(n5C(C)C)C)F',
    'inchi': 'UZWDCWONPYILKI-UHFFFAOYSA-N',
    'images_url': ' http://www.icoa.fr/pkidb/static/img/mol/Abemaciclib.svg',
    'kinases': [{'gene_name': 'CDK4', 'gene_alias': ['CDK4']}],
    'inhibitor_aliases': ['Verzenio', 'Abemaciclib', 'LY-2835219'],
    'chembl_id': ' CHEMBL3301610'},...]
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
    >> get_inhibitor_meta_from_inhibitor("Afatinib")
    {'inhibitor_id': 6,
    'inhibitor_name': 'Afatinib',
    'molecular_weight': 485.2,
    'smiles': 'CN(C)C/C=C/C(=O)Nc1cc2c(cc1O[C@H]3CCOC3)ncnc2Nc4ccc(c(c4)Cl)F',
    'inchi': 'ULXXDDBFHOBEHA-CWDCEQMOSA-N',
    'images_url': ' http://www.icoa.fr/pkidb/static/img/mol/Afatinib.svg',
    'kinases': [{'gene_name': 'EGFR','gene_alias': ['EGFR', 'ERBB', 'ERBB1', 'HER1']},
    {'gene_name': 'ERBB2','gene_alias': ['ERBB2', 'HER2', 'MLN19', 'NEU', 'NGL']},
    {'gene_name': 'ERBB4', 'gene_alias': ['ERBB4', 'HER4']}],
    'inhibitor_aliases': ['Giotrif;Gilotrif', 'Afatinib', 'BIBW-2992'],
    'chembl_id': ' CHEMBL1173655'}
    """
    #search in InhibitorMeta through InhibitorName for entry that matches the name of the query
    inhibitor_query = s.query(InhibitorMeta).join(InhibitorName).filter(InhibitorMeta.inhibitor_name==InhibitorName.inhibitor_name).\
    filter(InhibitorName.inhibitor_alias==inhibitor_entry).one()
    return inhibitor_query.to_dict()

#Function to return the meta data of the inhibitors related to one gene
def get_inhibitor_meta_from_gene(kinase):
    """
    Take in a kinase gene name and return a list of dictionaries.
    Returns empty list if there is not inhibitor for the kinase.
    >> kinase = "MAPK1"
    >> get_inhibitor_meta_from_gene(kinase)
    [{'inhibitor_id': 172,
    'inhibitor_name': 'Ulixertinib',
    'molecular_weight': 432.1,
    'smiles': 'CC(C)Nc1cc(c(cn1)Cl)c2cc([nH]c2)C(=O)N[C@H](CO)c3cccc(c3)Cl',
    'inchi': 'KSERXGMCDHOLSS-LJQANCHMSA-N',
    'images_url': ' http://www.icoa.fr/pkidb/static/img/mol/Ulixertinib.svg',
    'kinases': [{'gene_name': 'MAPK1',
    'gene_alias': ['MAPK1', 'ERK2', 'PRKM1', 'PRKM2']}],
    'inhibitor_aliases': ['VRT752271VRT-752271BVD-523', 'Ulixertinib'],
    'chembl_id': ' CHEMBL3590106'}]
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

#Phosphosite search by genomic location
#Function to return a list of all the chromosomes
def get_all_chromosome(as_tuples=True):
    """
    Returns a list of all chromosome numbers.
    If a list of int are desired, set as_tuples=False.
    >> get_all_chromosome()
    [(1, 1),(2, 2),(3, 3),...(21, 21),(22, 22),('Y', 'Y'),('X', 'X')]
    """
    chromosome_query = [x[0] for x in s.query(PhosphositeMeta.chromosome).all()] #return the obj in the query
    if as_tuples: #if as_tuples==True by default, ie if you want tuples
        return [(x, x) for x in set(chromosome_query)]
    return list(set(chromosome_query)) #otherwise, return result in a list with no tuples in

#Function to get the karyotype band given the chromosome
def get_karyotype_through_chromosome(chromosome_number, as_tuples=True):
    """(str) --> list
    Returns a list of karyotype band given a chromosome number.
    If a list of int are desired, set as_tuples=False.
    >> get_karyotype_through_chromosome("2")
    [('p13.1', 'p13.1'),('p13.3', 'p13.3'),('p14', 'p14'),...]
    """
    phosphosite_obj = s.query(PhosphositeMeta.karyotype_band).filter(PhosphositeMeta.chromosome==chromosome_number).all()
    phosphosite_obj = list(set(x[0] for x in sorted(phosphosite_obj))) #removed duplications
    ordered_list = sorted(phosphosite_obj, key=lambda x: (not x.islower(),x)) #order them by alphabet
    if as_tuples: #ie if list of tuples is desired by default
        return [(x, x) for x in ordered_list]
    return ordered_list

# Function to return a list of phosphosites given the chromosome and karyotype
def get_location_through_chromosome_karyotype(chromosome_input, karyotype_input, as_tuples=True):
    """(str, str) --> list
    Returns a list of phosphosphosite location by taking in the chromosome number, karyotype number.
    Returns empty list if there is no location.
    If a list of int are desired, set as_tuples=False.
    >> get_location_through_chromosome_karyotype(2, "q35")
    [('214780979:214780977', '214780979:214780977'),('216160126:216160128', '216160126:216160128'),
    ('216160135:216160137', '216160135:216160137'),
    """
    results = []
    phosphosite_query = s.query(PhosphositeMeta).filter(PhosphositeMeta.chromosome==chromosome_input).\
    filter(PhosphositeMeta.karyotype_band==karyotype_input).all() #search for the phosphosites with the chro and karyo
    if phosphosite_query==[]: #if no match found
        return []
    for phosphosite in phosphosite_query: #loop through the results if any
        results.append("{}:{}".format(phosphosite.start_position, phosphosite.end_position)) #append the start and end co into a list
    results.sort()
    if as_tuples: #if list of tuples (default) is desired
        return [(x,x) for x in results]
    return results

#Function to return the substrate and phosphosite details when user look for chromosome number and/or karyotype and/or phosphosites
def get_sub_pho_from_chr_kar_loc(chromosome_input, karyotype_input=None):
    """
    Return a list of dict.
    Karyotype and phosphosite location are None by default in case a user only search for chromosome.
    >> get_sub_pho_from_chr_kar_loc(2,"q35",'216160126:216160128')
    [{'substrate gene': 'DES','substrate name': 'desmin',
    'substrate_url': 'https://genome.ucsc.edu/cgi-bin/hgTracks?db=hg38&lastVirtModeType=default&lastVirtModeExtraState=&virtModeType=default&virtMode=0&nonVirtPosition=&position=chr2%3A219418377%2D219426734&hgsid=796473843_RdusyHlWn1O3a5PrtgCz1VDHBQGv',
    'phosphosite': 'T76','phosphosite_location': '219418688:219418690','chromosome': 2,'karyotype': 'q35',
    'strand': 1,'neighbouring sequences': 'LRAsRLGttRtPssy','kinases': ['PRKACA', 'ROCK1']},
    """
    results = []
    if karyotype_input == None: #this means if user only search for chromosome number
        phosphosite_query = s.query(PhosphositeMeta).filter(PhosphositeMeta.chromosome==chromosome_input).all()
    else: #if user only for chromosome number and karyotype
        phosphosite_query = s.query(PhosphositeMeta).filter(and_(PhosphositeMeta.chromosome==chromosome_input,
                                                             PhosphositeMeta.karyotype_band==karyotype_input)).all()
    for phosphosite_obj in phosphosite_query:
        tmp={}
        tmp["substrate gene"]=phosphosite_obj.substrate.substrate_gene_name
        tmp["substrate name"]=phosphosite_obj.substrate.substrate_name
        tmp["substrate_url"]=phosphosite_obj.substrate.substrate_url
        tmp["phosphosite"]=phosphosite_obj.phosphosite
        tmp["phosphosite_location"]="{}:{}".format(phosphosite_obj.start_position, phosphosite_obj.end_position)
        tmp["chromosome"]=phosphosite_obj.chromosome
        tmp["karyotype"]=phosphosite_obj.karyotype_band
        tmp["strand"]=phosphosite_obj.strand
        tmp["neighbouring sequences"]=phosphosite_obj.neighbouring_sequences
        tmp["kinases"] =[]
        for kinase in phosphosite_obj.kinases:
            tmp["kinases"].append(kinase.gene_name)
        results.append(tmp)
    return results

#Substrate search
#Function to return a list of substrate name and substrate gene name
def get_all_substrates():
    """
    Return a list of all substrates names and substrate gene names
    """
    substrate_list = [x[0] for x in s.query(SubstrateMeta.substrate_name).all()]
    substrate_list.extend(x[0] for x in s.query(SubstrateMeta.substrate_gene_name).all())
    return list(set(substrate_list))


def get_all_substrates_complete():
    """
    Return a list of all substrates names and substrate gene names
    """
    substrate_list = [x[0] for x in s.query(SubstrateMeta.substrate_name).all()]
    substrate_list.extend(x[0] for x in s.query(SubstrateMeta.substrate_gene_name).all())
    substrate_list.extend(x[0] for x in s.query(SubstrateMeta.substrate_uniprot_entry).all())
    substrate_list.extend(x[0] for x in s.query(SubstrateMeta.substrate_uniprot_number).all())
    return list(set(substrate_list))

#Function to return the substrate metadata and its phosphosites' metadata from a substrate
def get_substrate_phosphosites_from_substrate(substrate_input):
    """(str) --> dict
    Returns a dictionary of substrate metadata and all the phosphosites metadata that belong to the substrate.
    Phosphosite will be in a list of dictionaries.
    Refer to Database_query_II for more information.
    >> get_substrate_phosphosites_from_substrate('PTPRA')
    {}
    >> get_substrate_phosphosites_from_substrate('HDAC5')
    {'substrate_id': 42, 'substrate_name': 'HDAC5', 'substrate_gene_name': 'HDAC5', 'substrate_uniprot_entry': 'HDAC5_HUMAN',
    'substrate_uniprot_number': 'Q9UQL6', 'phosphosites': [{'phosphosite_meta_id': 57, 'substrate_meta_id': 42,
    'phosphosite': 'S498', 'chromosome': 17, 'karyotype_band': 'q21.31', 'strand': -1, 'start_position': 44088494,
    'end_position': 44088492, 'neighbouring_sequences': 'RPLSRtQsSPLPQsP'},...],
    'substrate_url': 'https://genome.ucsc.edu/cgi-bin/hgTracks?db=hg38&lastVirtModeType=default&lastVirtModeExtraState=&virtModeType=default&virtMode=0&nonVirtPosition=&position=chr17%3A44076746%2D44123702&hgsid=796473843_RdusyHlWn1O3a5PrtgCz1VDHBQGv'}
    """
    #look for SubstrateMeta obj with the query
    substrate_query = s.query(SubstrateMeta).filter(or_(SubstrateMeta.substrate_gene_name==substrate_input, SubstrateMeta.substrate_name==substrate_input,\
                SubstrateMeta.substrate_uniprot_entry==substrate_input, SubstrateMeta.substrate_uniprot_number==substrate_input)).all()
    if substrate_query == []: #if no such obj was found, skip it
        return []
    for substrate in substrate_query:
        return substrate.to_dict()
    
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
    #look for the phosphosite object that matches the query
    phosphosite_query = s.query(PhosphositeMeta)\
    .filter(PhosphositeMeta.substrate_meta_id==SubstrateMeta.substrate_id)\
    .filter(or_(SubstrateMeta.substrate_gene_name==substrate_input, SubstrateMeta.substrate_name==substrate_input,\
                SubstrateMeta.substrate_uniprot_entry==substrate_input, SubstrateMeta.substrate_uniprot_number==substrate_input)).all()
    if phosphosite_query == []: #if query not found, return an empty list
        return []
    for row in phosphosite_query:
        results.append(row.to_dict())
    return results