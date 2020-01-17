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
    gene_name = Column(String, ForeignKey('gene_meta.gene_name'))
    gene_alias = Column(String, primary_key=True)
    kinase_meta = relationship('gene_meta')

class subcellular_location(Base):
    __tablename__ = 'subcellular_location'
    subcellular_location_id = Column(Integer, primary_key = True)
    gene_name = Column(String, ForeignKey('gene_names.gene_alias'))
    subcellular_location = Column(String)
    kinase_meta = relationship('gene_names')

"""    
class kinase_substrate(Base):
    __tablename_ = 'kinase_substrate'
    ######might need a new primary_key
    kinase_gene_name = Column(String, ForeignKey('gene_names.gene_alias'),
                              primary_key=True)
    substrate_name = Column(String)
    kinase_meta = relationship('gene_names')
"""
    
class kinase_substrate_phosphosite(Base):
    __tablename__ = 'substrate_phosphosite'
    kinase_substrate_id = Column(Integer, primary_key = True)
    kinase_gene_name = Column(String, ForeignKey('gene_names.gene_alias'))
    substrate_name = Column(String)
    substrate_gene_name = Column(String)
    substrate_uniprot_entry = Column(String)
    substrate_uniprot_number = Column(Integer)
    phosphosite = Column(String)
    neighbouring_sequences = Column(String)
    kinase = relationship('gene_names')
    
class genomic_location(Base):
    __tablename__ = 'genomic_location'
    kinase_substrate_id = Column(Integer, 
                                 ForeignKey('kinase_substrate_phosphosite.kinase_substrate_id'))
    chromosome = Column(Integer)
    karyotype_band = Column(String)
    strand = Column(Integer)
    start_position = Column(Integer)
    end_position = Column(Integer)
    substrate = relationship('kinase_substrate_phosphosite')

class inhibitor(Base):
    __tablename__ = 'inhibitor'
    inhibitor = Column(String, primary_key = True)
    antagonizes_gene = Column(String, ForeignKey('gene_names.gene_alias'))
    molecular_weight = Column(Integer)
    images_url = Column(String)
    empirical_formula = Column(String)
    references = Column(String)
    kinase = relationship('gene_names')
    

#create an engine that stores the data in the local directory's kinase_database.db 
engine = create_engine('sqlite:///kinase_database.db')
#create all tables in the engine
Base.metadata.create_all(engine)