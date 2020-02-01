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
    phosphosites = relationship('PhosphositeMeta', secondary='kinase_phosphosite_relations')
    inhibitors = relationship("Inhibitor", secondary="kinase_inhibitor_relations" )
    # gene_aliases <from backref in KinaseGeneName>
    
    #create a function to return the object as dictionary
    def to_dict(self):
        """
        Returns the KinaseGeneMeta object as a dictionary.
        """
        output = {
               "protein_name": self.protein_name,
               "uniprot_number": self.uniprot_number,
               "uniprot_entry":self.uniprot_entry,
               "gene_name": self.gene_name,
               "kinase_family": self.kinase_family,
               "gene_aliases": [alias.gene_alias for alias in self.gene_aliases]
                }
        return output
    

class KinaseGeneName(Base):
    __tablename__ = 'kinase_gene_names'
    gene_name = Column(String, ForeignKey('kinase_gene_meta.gene_name'))
    gene_alias = Column(String, primary_key=True)
    meta = relationship('KinaseGeneMeta', backref=backref('gene_aliases', uselist=True))
    
    def to_dict(self):
        """
        Returns the KinaseGeneName as a dictionary:
        """
        output = {
                "gene_name" : self.gene_name,
                "gene_alias" : self.gene_alias
                }
        return output


class KinaseSubcellularLocation(Base):
    __tablename__ = 'subcellular_location'
    subcellular_location_id = Column(Integer, primary_key = True)
    gene_name = Column(String, ForeignKey('kinase_gene_meta.gene_name'))
    subcellular_location = Column(String)
    kinase_meta = relationship('KinaseGeneMeta', backref=backref('subcellular_locations', uselist=True))
    
    def to_dict(self):
        """
        Return the KinaseSubcellularLocation as a dictionary.
        """
        output = {
                "subcellular_location_id": self.subcellular_location_id,
                "gene_name": self.gene_name,
                "subcellular_location": self.subcellular_location
                }
        return output


class SubstrateMeta(Base):
    __tablename__ = 'substrate_meta'
    substrate_id = Column(Integer, primary_key = True)
    substrate_name = Column(String)
    substrate_gene_name = Column(String)
    substrate_uniprot_entry = Column(String)
    substrate_uniprot_number = Column(Integer)
    
    def to_dict(self):
        """
        Return SubstrateMeta as a dictionary.
        """
        output = {
                "substrate_id": self.substrate_id,
                "substrate_name": self.substrate_name,
                "substrate_gene_name": self.substrate_gene_name,
                "substrate_uniprot_entry": self.substrate_uniprot_entry,
                "substrate_uniprot_number": self.substrate_uniprot_number,
                "phosphosites": [phosphosite.to_dict() for phosphosite in self.phosphosites]
                }
        return output
    
class KinasePhosphositeRelations(Base):
    # a many to many relationship table between substrates and kinases
    __tablename__ = "kinase_phosphosite_relations"
    phosphosite_id = Column(Integer, ForeignKey('phosphosite_meta.phosphosite_meta_id'), primary_key=True)
    kinase_gene_id = Column(String, ForeignKey('kinase_gene_meta.gene_name'), primary_key=True)
    
    
class PhosphositeMeta(Base):
    __tablename__ = 'phosphosite_meta'
    phosphosite_meta_id = Column(Integer, primary_key=True)
    substrate_meta_id = Column(Integer, ForeignKey('substrate_meta.substrate_id'))
    substrate = relationship("SubstrateMeta", backref=backref('phosphosites', uselist=True))
    phosphosite = Column(String)
    chromosome = Column(Integer)
    karyotype_band = Column(String)
    strand = Column(Integer)
    start_position = Column(Integer)
    end_position = Column(Integer)
    neighbouring_sequences = Column(String)
    kinases = relationship('KinaseGeneMeta', secondary='kinase_phosphosite_relations')
    
    def to_dict(self):
        """
        Return PhosphositeMeta as a dictionary.
        """
        output = {
                "phosphosite_meta_id": self.phosphosite_meta_id,
                "substrate_meta_id": self.substrate_meta_id,
                "phosphosite": self.phosphosite,
                "chromosome": self.chromosome,
                "karyotype_band": self.karyotype_band,
                "strand": self.strand,
                "start_position": self.start_position,
                "end_position": self.end_position,
                "neighbouring_sequences": self.neighbouring_sequences,
                }
        return output


class KinaseInhibitorRelations(Base):
    # a many to many relationship table between kinase and the inhibitors
    __tablename__ = "kinase_inhibitor_relations"
    kinase_gene_name = Column(String, ForeignKey("kinase_gene_meta.gene_name"), primary_key=True)
    inhibitor_id = Column(Integer, ForeignKey("inhibitor.inhibitor_id"), primary_key=True)
    
    
class Inhibitor(Base):
    __tablename__ = 'inhibitor'
    inhibitor_id = Column(Integer, primary_key=True)
    inhibitor_name = Column(String)
    molecular_weight = Column(Integer)
    smiles = Column(String)
    pubchem_id = Column(Integer)
    inchi = Column(String)
    images_url = Column(String)
    empirical_formula = Column(String)
    kinases = relationship('KinaseGeneMeta', secondary="kinase_inhibitor_relations")
    
    def to_dict(self):
        """
        Return Inhibitor as a dictionary.
        """
        output = {
                #"inhibitor_id": self.inhibitor_id,
                "inhibitor": self.inhibitor,
                "molecular_weight": self.molecular_weight,
                "images_url": self.images_url,
                "empirical_formula": self.empirical_formula,
                "kinases": self.get_kinase_list()
                }
        return output
    
    def get_kinase_list(self):
        """
        Return a list of dictionary.
        The dictionary contains the gene name and its gene aliases.
        """
        results = []
        for kinase_obj in self.kinases:
            tmp ={}
            tmp_list = []
            tmp["gene_name"] = kinase_obj.gene_name
            for alias_obj in kinase_obj.gene_aliases:
                tmp_list.append(alias_obj.gene_alias)
            tmp["gene_alias"] = tmp_list
            results.append(tmp)
        return results
    
    """
    def get_kinases_list(self):
        raw_kinases = [kinase.to_dict() for kinase in self.kinases]
        kinases = {}
        for kin in raw_kinases:
            if kin["gene_name"] in kinases:
                kinases[kin["gene_name"]].append(kin["gene_alias"])
            else:
                kinases[kin["gene_name"]] = [kin["gene_alias"]]
        return kinases
    """   
        

#create an engine that stores the data in the local directory's kinase_database.db 
engine = create_engine('sqlite:///kinase_database.db')

if __name__ == '__main__':
    #create all tables in the engine
    Base.metadata.create_all(engine)