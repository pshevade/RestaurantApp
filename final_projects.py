# final_projects.py
from session_setup import *
from helper import *
from routing import *
from authentication import *


if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host = '0.0.0.0', port = 5000)
