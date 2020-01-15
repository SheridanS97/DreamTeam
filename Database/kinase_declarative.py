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
    gene_id = Column(Integer, primary_key = True)
    protein_name = Column(String)
    uniprot_number = Column(String)
    uniprot_entry = Column(String)
    gene_symbol = Column(String)

class gene_names(Base):
    __tablename__ = 'gene_names'
    gene_id = Column(Integer, primary_key=True, ForeignKey(gene_meta.gene_id )
    gene_names = Column(String)

class genomic_location(Base):
    pass

class subcellular_location(Base):
    pass

class phosphosites(Base):
    pass

