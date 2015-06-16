# final_projects.py
from flask import Flask, render_template, url_for, request, redirect, flash, jsonify
app = Flask(__name__)

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Restaurant, MenuItem, Tags, Reviews, User

#NEW IMPORTS FOR AUTHENTICATION
from flask import session as login_session
import random
import string

from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests

CLIENT_ID = json.loads(open('client_secrets.json', 'r').read())['web']['client_id']

engine = create_engine('sqlite:///myrestaurantmenu.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


   
@app.route('/login')
def showLogin():
    state =''.join(random.choice(string.ascii_uppercase + string.digits)
        for x in xrange(32))
    login_session['state'] = state
    #return "The current session state is %s" % login_session['state']
    return render_template('login.html', STATE=state)


@app.route('/')
@app.route('/restaurants')
def restaurantsPage():
    print("inside restaurants page")
    #return "This is the main restaurants page
    user_info = None
    if request.method == 'POST':
        print("We are reading stuff from form")

    elif request.method == 'GET':
        restaurant_list = session.query(Restaurant)
        reviews_list={}
        tag_list = {}
        for restaurant in restaurant_list:
            print("Restaurant name: {0}".format(restaurant.name))
            reviews_list[restaurant.id] = session.query(Reviews).filter_by(restaurant_id = restaurant.id)
            tag_list[restaurant.id] = session.query(Tags).filter_by(restaurant_id = restaurant.id)
            #for tags in tag_list[restaurant.id]:
            #    print("tag list is for restaurant {0}: {1}".format(restaurant.id, tags.tag_name))
        top_menu_item_list = getTopMenuItems(restaurant_list)
    if 'username' in login_session:
        user_info = session.query(User).filter_by(email=login_session['email']).first()



    print("This is the user_info: {}".format(user_info))
    return render_template('index.html', 
                        restaurant_list=restaurant_list, 
                        top_menu_items = top_menu_item_list, 
                        tag_list=tag_list, 
                        reviews_list =reviews_list,
                        user_info =user_info)
    
    
@app.route('/restaurant/<int:item_id>/<int:vote>')
def voteForItem(item_id, vote):
    if 'username' not in login_session:
        return redirect('/login')

    item = session.query(MenuItem).filter_by(id=item_id).one()

    if vote == 1:
        item.likes += 1
    elif vote == 2:
        item.dislikes += 1
    session.add(item)
    session.commit()
    return redirect(url_for('restaurantMenu', restaurant_id=item.restaurant_id))


@app.route('/restaurants/<int:restaurant_id>/edit', methods=['GET','POST'])
def restaurantsEdit(restaurant_id):
    #return "This is the edit restaurants page for restaurant {0}".format(restaurant_id)
    if 'username' not in login_session:
        return redirect('/login')

    restaurant = session.query(Restaurant).filter_by(id = restaurant_id).one()
    if request.method == 'POST':
        if len(request.form['address']) > 0:
            restaurant.address = request.form['address']
        if len(request.form['phone']) > 0:
            restaurant.phone = request.form['phone']
        if len(request.form['web']) > 0:
            restaurant.web = request.form['web']
        if len(request.form['tag_line']) > 0:
            restaurant.tag_line = request.form['tag_line']
        if len(request.form['description']) > 0:
            restaurant.description = request.form['description']

        print("inside post for restaurants edit")
        session.add(restaurant)
        session.commit()
        return redirect(url_for('restaurantsPage'))
    else:
        return render_template('editrestaurant.html', restaurant = restaurant)

@app.route('/restaurants/<int:restaurant_id>/addnewreview', methods=['GET', 'POST'])
def addNewReview(restaurant_id):
    #restaurant = session.query(Restaurant).filter_by(id = restaurant_id).one()
    if 'username' not in login_session:
        return redirect('/login')

    if request.method == 'POST':
        print("inside post for restaurants new review")
        print(request)
        post = request.get_json()
        print("THe post is: {0}".format(post))
        #print("THe author is: {0}".format(param))
        newreview = Reviews(reviewer_name=login_session['username'],
                            review=post.get('review'),
                            stars=post.get('stars'),
                            restaurant_id=restaurant_id)
        print("The new review object looks like: ")
        print(login_session['username'])
        print(newreview.review)
        print(newreview.stars)
        print(newreview.restaurant_id)
        session.add(newreview)
        session.commit()
    else:
        print("The restaurant name is to add new review is: {0}".format(restaurant.name))
    print("Moving out of addnewreview")
    return redirect(url_for('restaurantsPage'))

    #return render_template('editrestaurant.html', restaurant = restaurant)


@app.route('/restaurants/<int:restaurant_id>/reviews/JSON')
def restaurantReviewsListJSON(restaurant_id):
    print("in review jsons for restaurant: {0}".format(restaurant_id))
    reviews_list = session.query(Reviews).filter_by(restaurant_id=restaurant_id)
    return jsonify(ReviewsList=[review.serialize for review in reviews_list])



@app.route('/restaurants/<int:restaurant_id>/delete', methods=['GET','POST'])
def restaurantsDelete(restaurant_id):
    #return "This is the edit restaurants page for restaurant {0}".format(restaurant_id)
    if 'username' not in login_session:
        return redirect('/login')

    restaurant = session.query(Restaurant).filter_by(id=restaurant_id).one()
    if request.method == 'POST':
        session.delete(restaurant)
        session.commit()
        return redirect(url_for('restaurantsPage'))
    else:
        return render_template('deleterestaurant.html', restaurant=restaurant)


@app.route('/restaurants/new', methods=['GET','POST'])
def restaurantsNew():
    #return "This is the Create new restaurant page"
    if 'username' not in login_session:
        return redirect('/login')

    if request.method == 'POST':
        print("inside post for restaurants news")
        newRestaurant = Restaurant( name=request.form['name'],
                                    address = request.form['address'],
                                    phone = request.form['phone'],
                                    web = request.form['web'],
                                    tag_line = request.form['tag_line'],
                                    description = request.form['description']
                                    )
        session.add(newRestaurant)
        session.commit()
        return redirect(url_for('restaurantsPage'))
    else:
        return render_template('newrestaurant.html')


@app.route('/restaurants/<int:restaurant_id>/menu')
def restaurantMenu(restaurant_id):
    #return "This is the menu display page for restaurant {0}".format(restaurant_id)
    restaurant = session.query(Restaurant).filter_by(id=restaurant_id).one()
    #print("the menu for restaurant of id: {0}".format(restaurant.id))
    menu_list = session.query(MenuItem).filter_by(restaurant_id = restaurant_id)
    return render_template('restaurantmenu.html', restaurant = restaurant, menu_list = menu_list)


@app.route('/restaurants/JSON')
def restaurantListJSON():
    restaurant_list = session.query(Restaurant)
    return jsonify(RestaurantList=[restaurant.serialize for restaurant in restaurant_list])


@app.route('/restaurants/<int:restaurant_id>/JSON')
def restaurantMenuJSON(restaurant_id):
    restaurant = session.query(Restaurant).filter_by(id=restaurant_id).one()
    items = session.query(MenuItem).filter_by(restaurant_id = restaurant_id)
    return jsonify(MenuItems=[i.serialize for i in items])


@app.route('/restaurants/<int:restaurant_id>/<int:menu_id>/JSON')
def restaurantMenuItemJSON(restaurant_id, menu_id):
    item = session.query(MenuItem).filter_by(id=menu_id).one()
    return jsonify(MenuItem=item.serialize)

@app.route('/restaurants/<int:restaurant_id>/<int:menu_id>/edit', methods=['GET', 'POST'])
def menuItemEdit(restaurant_id, menu_id):
    #return "This is the edit menu item page for restaurant {0} and item {1}".format(restaurant_id, menu_id)
    if 'username' not in login_session:
        return redirect('/login')

    restaurant = session.query(Restaurant).filter_by(id=restaurant_id).one()
    menu_item = session.query(MenuItem).filter_by(id=menu_id).one()
    if request.method == 'POST':
        menu_item.name = request.form['name']
        menu_item.price = request.form['price']
        menu_item.description = request.form['description']
        menu_item.course = request.form['course']
        return redirect(url_for('restaurantMenu', restaurant_id = restaurant_id))
    else:
        return render_template('editmenu.html', restaurant = restaurant, menu_item = menu_item)


@app.route('/restaurants/<int:restaurant_id>/<int:menu_id>/delete', methods=['GET', 'POST'])
def menuItemDelete(restaurant_id, menu_id):
    #return "This is the Delete menu item page for restaurant {0} and item {1}".format(restaurant_id, menu_id)
    if 'username' not in login_session:
        return redirect('/login')

    restaurant = session.query(Restaurant).filter_by(id=restaurant_id).one()
    menu_item = session.query(MenuItem).filter_by(id=menu_id).one()
    if request.method == 'POST':
        session.delete(menu_item)
        return redirect(url_for('restaurantMenu', restaurant_id = restaurant_id))
    else:
        return render_template('deletemenu.html', restaurant = restaurant, menu_item = menu_item)


@app.route('/restaurants/<int:restaurant_id>/new', methods=['GET', 'POST'])
def menuItemNew(restaurant_id):
    #return "This is the new menu item page for restaurant {0}".format(restaurant_id)
    if 'username' not in login_session:
        return redirect('/login')

    if request.method == 'POST':
        print("inside post for restaurants news")

        newItem = MenuItem(name = request.form['name'], description = request.form['description'], price = request.form['price'], course = request.form['course'], likes=0, dislikes=0, restaurant_id = restaurant_id)
        session.add(newItem)
        session.commit()
        return redirect(url_for('restaurantMenu', restaurant_id = restaurant_id))
    else:
        return render_template('newmenuitem.html', restaurant_id = restaurant_id)


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
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
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
    
    user_obj = createUserIfNotExists(name=data['name'], email=data['email'], picture=data['picture'])

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
    flash("you are now logged in as %s" % login_session['username'])
    print "done!"
    return output

def createUserIfNotExists(name, email, picture):
    user_exists = session.query(User).filter_by(name=name).first()
    if user_exists is not None:
        return user_exists
    else:
        new_user = User(name=name, email=email, picture=picture)
        session.add(new_user)
        session.commit()
        return new_user


@app.route('/gdisconnect')
def gdisconnect():
        # Only disconnect a connected user.
    credentials = login_session.get('credentials')
    if credentials is None:
        response = make_response(
            json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    access_token = credentials.access_token
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]

    if result['status'] == '200':
        # Reset the user's sesson.
        del login_session['credentials']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']

        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response
    else:
        # For whatever reason, the given token was invalid.
        response = make_response(
            json.dumps('Failed to revoke token for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response


if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host = '0.0.0.0', port = 5000)
