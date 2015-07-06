""" Flask Setup File. """

from flask import Flask
from flask.ext.seasurf import SeaSurf

# Create a Flask app
app = Flask(__name__)

# Create the CSRF validation object
csrf = SeaSurf(app)

# Image upload information
UPLOAD_FOLDER = 'static/images/uploads/'
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'PNG', 'JPG', 'JPEG'])

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
