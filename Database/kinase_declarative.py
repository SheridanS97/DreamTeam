#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jan 15 17:01:24 2020

@author: zho30
"""

#import library
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship, backref
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine

#create a base object
Base = declarative_base()

#setting up the class for the table
class gene_meta(Base):
    __tablename__ = 'gene_meta'
    protein_name = Column(String)
    uniprot_number = Column(Integer)
    uniprot_entry = Column(String)
    gene_name = Column(String, primary_key=True)
    kinase_family = Column(String)

class gene_names(Base):
    __tablename__ = 'gene_names'
    gene_name = Column(String, ForeignKey(gene_meta.gene_name))
    gene_aliases = Column(String, primary_key=True)

class subcellular_location(Base):
    gene_name = Column(String, primary_key=True, 
                       ForeignKey(gene_meta.gene_name),
                       primary_key=True)
    subcellular_location = Column(String)
    
class kinase_substrate(Base):
    __tablename_ = 'kinase_substrate'
    kinase_gene_name = Column(String, ForeignKey(gene_meta.gene_name),
                              primary_key=True)
    substrate_name = Column(String)
    
class substrate_phosphosite(Base):
    __tablename__ = 'substrate_phosphosite'
    #there no unique values in this table, an index generated will have to be the primary_key
    substrate_phosphosite_id = Column(Integer, primary_key=True)
    substrate_name = Column(String, ForeignKey(kinase_substrate.substrate_name))
    substrate_gene_name = Column(String)
    substrate_uniprot_entry = Column(String)
    substrate_uniprot_number = Column(Integer)
    phosphosite = Column(String)
    neighbouring_sequences = Column(String)
    
class genomic_location(Base):
    __tablename__ = 'genomic_location'
    substrate_gene_name = Column(String, 
                                 ForeignKey(substrate_phosphosite.substrate_gene_name))
    phosphosite = Column(String, ForeignKey(substrate_phosphosite.phosphosite))
    chromosome = Column(Integer)
    karyotype_band = Column(String)
    strand = Column(Integer)
    start_position = Column(Integer)
    end_position = Column(Integer)

class inhibitor(Base):
    __tablename__ = 'inhibitor'
    inhibitor = Column(String, primary_key = True)
    antagonizes_gene = Column(String, ForeignKey(gene_meta.gene_name))
    molecular_weight = Column(Integer)
    images_url = Column(String)
    empirical_formula = Column(String)
    references = Column(String)
    




#create an engine that stores the data in the local directory's kinase_database.db 
engine = create_engine('sqlite:///kinase_database.db')
#create all tables in the engine
Base.metadata.create_all(engine)