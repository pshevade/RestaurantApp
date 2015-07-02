# session_setup
# Import Flask and SQLAlchemy files and create the session object

import os
from flask import Flask, render_template, url_for, request, redirect, flash, jsonify
from flask.ext.seasurf import SeaSurf

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Restaurant, MenuItem, Tags, Reviews, User, Image, RestaurantImages
from werkzeug import secure_filename
from werkzeug.contrib.atom import AtomFeed

app = Flask(__name__)
csrf = SeaSurf(app)


UPLOAD_FOLDER = 'static/images/uploads/'
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'PNG', 'JPG', 'JPEG'])

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

engine = create_engine('sqlite:///myrestaurantmenu.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()
