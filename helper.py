# helper.py
from session_setup import *


""" 
    getTopMenuItems
    Return the most voted item for each restaurant 
    arguments:  restaurant_list (list of all restaurants)
    returns:    get the menu item list for each restaurant, find the score for each item, 
                return the top voted item for each restaurant 
"""
def getTopMenuItems(restaurant_list):
    top_items_list = {}
    score = 0
    appended = 0
    for restaurant in restaurant_list:
        menu_list = session.query(MenuItem).filter_by(restaurant_id = restaurant.id)
        for item in menu_list:
            if item.likes - item.dislikes > score:
                top_items_list[restaurant.name] = item.name
                score = item.likes - item.dislikes
                appended = 1
            if appended == 0:
                top_items_list[restaurant.name] = ""
        appended = 0
        score = 0

    return top_items_list


""" 
    createUser
    create a user object in the database - store the username, email, and picture
    arguments:  login_session object
    returns:    the user id for the newly created user. 
"""
def createUser(login_session):
    newUser = User(name=login_session['username'], email=login_session['email'], picture=login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id


""" 
    getUserInfo
    return the user's object from the database, else return none
    arguments:  user id
    returns:    Find the user in the database and return the first instance of that user id 
"""
def getUserInfo(user_id):
    user = session.query(User).filter_by(id=user_id).first()
    return user


""" 
    getUserID
    Find the user id based on the email 
    arguments:  the user's email
    returns:    return the user id or None if not found 
"""
def getUserID(email):
    try:
        user = session.query(User).filter_by(email=email).first()
        return user.id
    except:
        return None


""" 
    getUserIfExists
    return the user's info (call the getUserInfo function) if the user exists, else none
    arguments:  login_session object
    returns:    return the user's info if the user exists, else return none 
"""
def getUserIfExists(login_session):
    user_info = None
    if 'username' in login_session:
        user_ID = getUserID(login_session['email'])
        user_info = getUserInfo(user_ID)

    return user_info


""" 
    handle_login
    Check if the user's email is in the login_session
    arguments:  login_session
    returns:    True is the user's email is in the login_session
"""
def handle_login(login_session):
    # To debug, comment out the next if statement
    if 'email' not in login_session:
        return False
    return True