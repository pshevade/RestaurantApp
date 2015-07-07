""" Main file to run the restaurant menu app. """

from flask_setup import app
import database_setup
import routing
import helper
import session_setup
import authentication
import api_endpoints


if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
