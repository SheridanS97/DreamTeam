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

#Please refer to Database_query_II for more information
#A list of functions is available on Database query II

#Intermediate kinase results page
def get_gene_alias_protein_name(kinase_input):
    """
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
    like_kin = "%{}%".format(kinase_input)
    tmp = []
    kinase_query = s.query(KinaseGeneMeta).join(KinaseGeneName).filter(or_(KinaseGeneName.gene_alias.like(like_kin), KinaseGeneMeta.uniprot_entry.like(like_kin),\
                                   KinaseGeneMeta.uniprot_number.like(like_kin), KinaseGeneMeta.protein_name.like(like_kin))).all()
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
    """
    Takes in a gene name as a string then output a dictionary.
    >> get_gene_metadata_from_gene("MAPK1")
    {'gene_name': 'MAPK1', 
    'kinase_family': 'CMGC Ser/Thr protein kinase family',
    'protein_name': 'Mitogen-activated protein kinase 1',
    'uniprot_entry': 'MK01_HUMAN',
    'uniprot_number': 'P28482'}
    """
    kinase_obj = s.query(KinaseGeneMeta).filter(KinaseGeneMeta.gene_name==kinase_str).one()
    return kinase_obj.to_dict()

#Function to return subcellular location of kinase
def get_subcellular_location_from_gene(kinase_gene):
    """
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
    results["Gene_Name"] = kinase_gene
    kinase_query = s.query(KinaseSubcellularLocation).join(KinaseGeneMeta).join(KinaseGeneName).\
    filter(KinaseGeneName.gene_alias==kinase_gene).filter(KinaseGeneMeta.gene_name==KinaseGeneName.gene_name).\
    filter(KinaseGeneMeta.gene_name==KinaseSubcellularLocation.gene_name).all()
    for row in kinase_query:
        tmp.append(row.subcellular_location)
    results["Subcellular_Locations"] = tmp
    return results

#Function to return the inhibitors from a kinase
def get_inhibitors_from_gene(kinase_gene):
    """
    Take a string and return a list of dictionaries.
    Returns empty list if there are no inhibitors.
    >> get_inhibitors_from_gene("SGK1")
    ['GSK650394A', 'SGK-Sanofi-14i','SGK1-Sanofi-14g', 'SGK1-Sanofi-14h', 'SGK1-Sanofi-14n']
    """
    results = []
    kinase_query = s.query(KinaseGeneMeta).join(KinaseGeneName).filter(KinaseGeneMeta.gene_name==KinaseGeneName.gene_name).\
    filter(KinaseGeneName.gene_alias==kinase_gene).all()
    if len(kinase_query) == 0:
        return []
    for inhibitor in kinase_query[-1].inhibitors:
        results.append(inhibitor.inhibitor)
    return results

#Function to return the meta details of the inhibitor from an inhibitor
def get_inhibitor_meta_from_inhibitor(inhibitor_name):
    """(str) --> dict
    Returns the meta data of the inhibitor.
    >> get_inhibitor_meta_from_inhibitor("PD 184352 (CI-1040)")
    {'inhibitor': 'PD 184352 (CI-1040)', 
    'molecular_weight': 478.66,
    'images_url': 'http://www.kinase-screen.mrc.ac.uk/system/files/compounds/jpg/pd-184352_5.jpg',
    'empirical_formula': 'C17H14ClF2IN2O2',
    'kinases': [{'gene_name': 'YES1', 'gene_alias': ['YES1', 'YES']},
    {'gene_name': 'MAPK3', 'gene_alias': ['MAPK3', 'ERK1', 'PRKM3']},
    {'gene_name': 'MAP2K1', 'gene_alias': ['MAP2K1', 'MEK1', 'PRKMK1']}]}
    """
    inhibitor_query = s.query(Inhibitor).filter(Inhibitor.inhibitor==inhibitor_name).one()
    return inhibitor_query.to_dict()
    
#Function to return substrates and phosphosites from a kinase
def get_substrates_phosphosites_from_gene(kinase_gene):
    """
    Takes in a gene name of a kinase and return a dictionary of dictionaries.
    In each dictionary (inner), the key is the substrate name; the value is a list of dictionary containing the metadata
    of phosphosites.
    Returns empty list if there are no substrates.
    >> get_substrates_phosphosites_from_gene("JAK2")
    {'ARHGEF1': [{'phosphosite': 'Y738', 'chromosome': 19, 'karyotype_band': 'q13.2', 'strand': 1, 'start_position': 41904999, 
    'end_position': 41905001, 'neighbouring_sequences': 'WDQEAQIyELVAQTV'}],...}
    >> get_substrates_phosphosites_from_gene("empty")
    []
    """
    tmp = {}
    kinase_obj = s.query(KinaseGeneMeta).join(KinaseGeneName).filter(KinaseGeneName.gene_alias==kinase_gene).\
    filter(KinaseGeneMeta.gene_name==KinaseGeneName.gene_name).all()
    if kinase_obj == []:
        return []
    kinase_obj = kinase_obj[-1]
    for phosphosite in kinase_obj.phosphosites:
        gene = phosphosite.substrate.substrate_name
        if gene in tmp:
            tmp[gene].append(phosphosite.to_dict())
        else:
            tmp[gene] = [phosphosite.to_dict()]
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
    {'kinase': 'CSNK2A1', 'substrate': 'RRN3_HUMAN', 'phosphosite': 'T200'}
    >> get_kinase_substrate_phosphosite("empty", "T200")
    []
    """
    tmp = {}
    sub_pho_query = s.query(PhosphositeMeta).join(SubstrateMeta).filter(PhosphositeMeta.phosphosite==pho).\
    filter(SubstrateMeta.substrate_id==PhosphositeMeta.substrate_meta_id).\
    filter(or_(SubstrateMeta.substrate_gene_name==sub, SubstrateMeta.substrate_name==sub,\
               SubstrateMeta.substrate_uniprot_entry==sub, SubstrateMeta.substrate_uniprot_number==sub)).all()
    if sub_pho_query == []:
        return []
    for phosphosite in sub_pho_query:
        for kinase in phosphosite.kinases:
            tmp["kinase"] = kinase.gene_name
            tmp["substrate"] = sub
            tmp["phosphosite"] = pho
    return tmp

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
    inhibitors = s.query(Inhibitor).all()
    for inhibitor in inhibitors:
        results.append(inhibitor.to_dict())
    return results

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
    kinase_query = s.query(KinaseGeneMeta).join(KinaseGeneName).filter(KinaseGeneMeta.gene_name==KinaseGeneName.gene_name).\
    filter(KinaseGeneName.gene_alias==kinase).all()
    if kinase_query == []:
        return []
    for inhibitor in kinase_query[-1].inhibitors:
        results.append(inhibitor.to_dict())
    return results

