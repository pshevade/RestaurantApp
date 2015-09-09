""" Flask Setup File. """
import os
from flask import Flask
from flask.ext.seasurf import SeaSurf

# # DATABASE information
# DATABASE_URI = os.environ('postgresql://localhost/restaurant_pg_test')


# Create a Flask app
app = Flask(__name__)
# app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://localhost/restaurant_pg_test'
app.config.from_pyfile('config.py')
# db = SQLAlchemy(app)


# Create the CSRF validation object
csrf = SeaSurf(app)

# Image upload information
UPLOAD_FOLDER = 'static/images/uploads/'
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'PNG', 'JPG', 'JPEG'])

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
