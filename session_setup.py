""" SQL Alchemy Session setup. """

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base

# Create the SQLite database
engine = create_engine('sqlite:///myrestaurantmenu.db')
Base.metadata.bind = engine

# Create an sqlalchemy session
DBSession = sessionmaker(bind=engine)
session = DBSession()
