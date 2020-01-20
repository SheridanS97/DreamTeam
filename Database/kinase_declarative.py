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
class KinaseGeneMeta(Base):
    __tablename__ = 'kinase_gene_meta'
    protein_name = Column(String)
    uniprot_number = Column(Integer)
    uniprot_entry = Column(String)
    gene_name = Column(String, primary_key=True)
    kinase_family = Column(String)
    # gene_aliases <from backref in KinaseGeneName>


class KinaseGeneName(Base):
    __tablename__ = 'kinase_gene_names'
    gene_name = Column(String, ForeignKey('kinase_gene_meta.gene_name'))
    gene_alias = Column(String, primary_key=True)
    meta = relationship('KinaseGeneMeta', backref=backref('gene_aliases', uselist=True))
    substrates = relationship('SubstrateMeta', secondary='kinase_substrate_relations')


class KinaseSubcellularLocation(Base):
    __tablename__ = 'subcellular_location'
    subcellular_location_id = Column(Integer, primary_key = True)
    gene_name = Column(String, ForeignKey('kinase_gene_names.gene_alias'))
    subcellular_location = Column(String)
    kinase_meta = relationship('KinaseGeneName', backref=backref('subcellular_locations', uselist=True))
    

class SubstrateMeta(Base):
    __tablename__ = 'substrate_meta'
    substrate_id = Column(Integer, primary_key = True)
    substrate_name = Column(String)
    substrate_gene_name = Column(String)
    substrate_uniprot_entry = Column(String)
    substrate_uniprot_number = Column(Integer)
    kinases = relationship('KinaseGeneName', secondary='kinase_substrate_relations')
    
    
class KinaseSubstrateRelations(Base):
    #a many to many relationship table between substrates and kinases
    __tablename__ = 'kinase_substrate_relations'
    substrate_id = Column(Integer, ForeignKey('substrate_meta.substrate_id'), primary_key=True)
    kinase_gene_id = Column(String, ForeignKey('kinase_gene_names.gene_alias'), primary_key=True)
    
    
class PhosphositeMeta(Base):
    __tablename__ = 'phosphosite_meta'
    phosphosite_meta_id = Column(Integer, primary_key=True)
    substrate_meta_id = Column(Integer, ForeignKey('substrate_meta.substrate_id'))
    substrate = relationship("SubstrateMeta", backref=backref('phosphosites', uselist=True))
    chromosome = Column(Integer)
    karyotype_band = Column(String)
    strand = Column(Integer)
    start_position = Column(Integer)
    end_position = Column(Integer)
    neighbouring_sequences = Column(String)
    

class Inhibitor(Base):
    __tablename__ = 'inhibitor'
    inhibitor = Column(String, primary_key = True)
    antagonizes_gene = Column(String, ForeignKey('kinase_gene_names.gene_alias'))
    kinases = relationship('KinaseGeneName', backref=backref('inhibitors', uselist=True))
    molecular_weight = Column(Integer)
    images_url = Column(String)
    empirical_formula = Column(String)
    references = Column(String)

    

#create an engine that stores the data in the local directory's kinase_database.db 
engine = create_engine('sqlite:///kinase_database.db')

if __name__ == '__main__':
    #create all tables in the engine
    Base.metadata.create_all(engine)