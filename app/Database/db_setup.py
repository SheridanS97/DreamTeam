#calling library
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from .kinase_declarative import *

#create engine and bine the engine
engine = create_engine("sqlite:///kinase_database.db", connect_args={'check_same_thread': False}, convert_unicode=True)
Base.metadata.bind = engine

#create a session object
session = sessionmaker(bind=engine)
s = session()

