#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jan 24 16:40:24 2020

@author: zho30
"""

#calling the library
from kinase_declarative import * #please make sure kinase_declarative.py is in the same folder
from sqlalchemy import create_engine, or_
from sqlalchemy.orm import sessionmaker
from pprint import pprint #don't really need this if running in script

#Please refer to Database_query_II for more information
#Intermediate kinase results page
def get_gene_protein_name(kinase_input):
    """
    Returns a list of dictionary.
    In the dictionary, there are gene name and protein name.
    Returns empty list when no match is found.
    >> kin = "AKT"
    >> get_gene_protein_name(kin)
    [{'Gene Name': 'AKT', 'Protein Name': 'RAC-alpha serine/threonine-protein kinase'}, 
    {'Gene Name': 'AKT', 'Protein Name': 'RAC-beta serine/threonine-protein kinase'}, 
    {'Gene Name': 'AKT', 'Protein Name': 'RAC-gamma serine/threonine-protein kinase'}]
    """
    like_kin = "%{}%".format(kinase_input)
    tmp = []
    kinase_query = s.query(KinaseGeneMeta).join(KinaseGeneName).filter(or_(KinaseGeneName.gene_alias.like(like_kin), KinaseGeneMeta.uniprot_entry.like(like_kin),\
                                   KinaseGeneMeta.uniprot_number.like(like_kin), KinaseGeneMeta.protein_name.like(like_kin))).all()
    for row in kinase_query:
        results = {}
        results["Gene_Name"] = row.to_dict()["gene_name"]
        results["Protein_Name"] = row.to_dict()["protein_name"]
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
    kinase_query = s.query(KinaseSubcellularLocation).join(KinaseGeneName).filter(KinaseGeneName.gene_alias==kinase_gene).all()
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
    kinase_query = s.query(KinaseGeneName).filter(KinaseGeneName.gene_alias==kinase).one()
    for inhibitor in kinase_query.inhibitors:
        results.append(inhibitor.inhibitor)
    return results

#Function to return substrates and phosphosites from a kinase
def get_substrates_phosphosites_from_gene(kinase_gene):
    """
    Takes in a gene name of a kinase and return a dictionary of dictionaries.
    In each dictionary (inner), the key is the substrate name; the value is a list of dictionary containing the metadata
    of phosphosites.
    >> get_substrates_phosphosites_from_gene("JAK2")
    {'ARHGEF1': [{'phosphosite': 'Y738', 'chromosome': 19, 'karyotype_band': 'q13.2', 'strand': 1, 'start_position': 41904999, 
    'end_position': 41905001, 'neighbouring_sequences': 'WDQEAQIyELVAQTV'}],...}
    """
    tmp = {}
    kinase_gene = "JAK2"
    kinase_obj = s.query(KinaseGeneName).filter(KinaseGeneName.gene_alias==kinase_gene).one()
    for phosphosite in kinase_obj.phosphosites:
        gene = phosphosite.substrate.substrate_name
        if gene in tmp:
            tmp[gene].append(phosphosite.to_dict())
        else:
            tmp[gene] = [phosphosite.to_dict()]
    return tmp