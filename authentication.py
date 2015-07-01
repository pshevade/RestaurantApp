# Authentication with OAuth2
from session_setup import *
from helper import *

from flask import session as login_session
import random
import string

from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests

CLIENT_ID = json.loads(open('../client_secrets.json', 'r').read())['web']['client_id']


""" 
    gconnect 
    Connect to google and authenticate the user. 
    If the user doesn't exist in database, create the user. 
"""
@csrf.exempt
@app.route('/gconnect', methods=['POST'])
def gconnect():
    print("inside gconnect")
    # Validate state token
    if request.args.get('state') != login_session['state']:
        print("inside validating state token")
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        print("validated state token")
        return response
    else:
        print("request args get state %s"%request.args.get('state'))
        print(" was the same as login session's state %s"%login_session['state'])
    # Obtain authorization code
    code = request.data
    print(code)
    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('../client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
        print("upgraded authorization code")
    except FlowExchangeError:
        print("Failed to upgrade to authorization code")
        response = make_response(json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        print response
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        print("There was an error in accessing token info")
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        print("There was an error in verifying token was for intended user")
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        print("There was an error in verifying the token is valid for this app")
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print "Token's client ID does not match app's."
        response.headers['Content-Type'] = 'application/json'
        return response
    print ("got to this point")
    stored_credentials = login_session.get('credentials')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_credentials is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps('Current user is already connected.'),
                                 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['credentials'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']
    
    user_id = getUserID(login_session['email'])
    if user_id is None:
        print("Creating a new user id")
        user_id = createUser(login_session)
    print("THe user id is: {}".format(user_id))
    user = getUserInfo(user_id)

    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 250px; height: 250px;border-radius: 125px;-webkit-border-radius: 125x;-moz-border-radius: 125px;"> '
    flash("you are now logged in as %s" % login_session['username'])
    print "done!"
    revoke_access()
    return output


""" 
    revoke_access 
    Disconnect from Google - we don't need to be connected to them after we have authenticated and stored the user
"""
def revoke_access():
    credentials = login_session.get('credentials')
    if credentials is None:
        response = make_response(
            json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    access_token = credentials
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]

    if result['status'] == '200':
        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response
    else:
        # For whatever reason, the given token was invalid.
        response = make_response(
            json.dumps('Failed to revoke token for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response


""" 
    log_out 
    Log out the user, remove the details from our login_session. 
    The user object is still stored in the database.
"""
@csrf.include
@app.route('/log_out')
def log_out():
    del login_session['credentials']
    del login_session['gplus_id']
    del login_session['username']
    del login_session['email']
    del login_session['picture']

    return redirect(url_for('restaurantsPage'))
