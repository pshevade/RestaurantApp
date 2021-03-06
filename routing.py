""" routing.py.

    This file has the routing functions.
"""

import random
import string
from datetime import datetime

from flask import render_template, url_for, request, redirect, flash
from flask_setup import app, csrf
from session_setup import session

from authentication import login_session
from database_setup import Restaurant, Tags, RestaurantTags, MenuItem, RestaurantImages, Reviews
import helper


@app.route('/login')
def show_login():
    """ Create the randomized state id, redirect to login page. """
    # Generate a unique session token
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    # return "The current session state is %s" % login_session['state']
    return render_template('login.html', STATE=state)


@app.route('/')
@app.route('/restaurants')
def restaurants_page():
    """
    Get the list of users and show them to the screen.

    arguments:  restaurant_id (for that restaurant)
    returns:    render the "index.html" template
                pass: restaurant_list, top_menu_items,
                      tag_list, user_info,
    """
    print("inside restaurants page")
    tag_list = {}
    # Get restaurants list, sorted by last update date
    restaurant_list = session.query(Restaurant).order_by("last_update desc").all()
    # Get all tags associated with the restaurant
    for restaurant in restaurant_list:
        tag_pairs = session.query(RestaurantTags).filter_by(restaurant_id=restaurant.id).all()
        tag_list[restaurant.id] = []
        for pair in tag_pairs:
            tag_list[restaurant.id].append(session.query(Tags).filter_by(id=pair.tag_id).first())
    # Find the top menu item for each restaurant - based on customer voting
    top_menu_item_list = helper.get_top_menu_items(restaurant_list)
    # Get the user data, if user has logged in
    user_info = helper.get_user_if_exists(login_session)
    return render_template('index.html',
                           restaurant_list=restaurant_list,
                           top_menu_items=top_menu_item_list,
                           tag_list=tag_list,
                           user_info=user_info)


@app.route('/restaurants/<int:restaurant_id>/edit', methods=['GET', 'POST'])
def restaurants_edit(restaurant_id):
    """
    Let the user (authenticated) edit the restaurant info.
    arguments:  restaurant_id (for that restaurant)
    returns:    if post - redirect to the restaurants_page to main page
                if get -  render the "editrestaurant.html" template
                            - pass: restaurant object, user_info,
    """
    # If the user isn't logged in, send to the login page
    if helper.handle_login(login_session) is False:
        return redirect('/login')
    # Find the restaurant
    restaurant = session.query(Restaurant).filter_by(id=restaurant_id).one()
    if request.method == 'POST':
        # Only edit if the entry was re-written
        if len(request.form['address']) > 0:
            restaurant.address = request.form['address']
        if len(request.form['phone']) > 0:
            restaurant.phone = request.form['phone']
        if len(request.form['web']) > 0:
            restaurant.web = helper.check_restaurant_URL(request.form['web'])
        if len(request.form['tag_line']) > 0:
            tag_line = request.form['tag_line']
            tag_list = tag_line.split(',')
            helper.delete_restaurant_tag_pairs(restaurant.id)
            for tag in tag_list:
                helper.add_tag_if_not_exists(tag, restaurant.id)
        if len(request.form['description']) > 0:
            restaurant.description = request.form['description']

        restaurant.last_update = datetime.utcnow()

        session.add(restaurant)
        session.commit()
        flash("Restaurant {} edited!".format(restaurant.name))
        return redirect(url_for('restaurants_page'))
    else:
        # Get user info if the user is signed in to render edit form
        user_info = helper.get_user_if_exists(login_session)
        tag_rest_list = session.query(RestaurantTags).filter_by(restaurant_id=restaurant.id).all()
        tag_line = ''
        # Create a tag line - by compiling the string tag_name for each tag
        for pair in tag_rest_list:
            tag = session.query(Tags).filter_by(id=pair.tag_id).first()
            tag_line += tag.tag_name + ', '
        return render_template('editrestaurant.html',
                               restaurant=restaurant,
                               tag_line=tag_line,
                               user_info=user_info)


@csrf.include
@app.route('/restaurants/<int:restaurant_id>/delete', methods=['GET', 'POST'])
def restaurants_delete(restaurant_id):
    """
    Let the user who created this restaurant delete it.

    arguments:  restaurant_id (for that restaurant)
    returns:    if post - redirect to the restaurants_page
                if get -  render the "deleterestaurant.html" template
                            - pass: restaurant obj, user_info,
    """
    # If the user isn't logged in, send to the login page
    if helper.handle_login(login_session) is False:
        return redirect('/login')
    restaurant = session.query(Restaurant).filter_by(id=restaurant_id).one()
    # Delete all menu items, reviews, and images for the restaurant
    if request.method == 'POST':
        # Call the delete_restaurant function which deletes iteratively
        helper.delete_restaurant(restaurant.id)
        return redirect(url_for('restaurants_page'))
    else:
        user_info = helper.get_user_if_exists(login_session)
        return render_template('deleterestaurant.html',
                               restaurant=restaurant,
                               user_info=user_info)


@csrf.include
@app.route('/restaurants/new', methods=['GET', 'POST'])
def restaurants_new():
    """
    Create a new restaurant and add to database.

    arguments:  none
    returns:    if post - redirect to the restaurants_page
                if get - render the "newrestaurant.html" template
                            - pass: user_info
    """
    # If the user isn't logged in, send to the login page
    if helper.handle_login(login_session) is False:
        return redirect('/login')

    if request.method == 'POST':
        if len(request.form['name']) > 0:
            new_restaurant = Restaurant(name=request.form['name'],
                                        address=request.form['address'],
                                        phone=request.form['phone'],
                                        web=helper.check_restaurant_URL(request.form['web']),
                                        description=request.form['description'],
                                        user_id=login_session['user_id'])
            session.add(new_restaurant)
            session.commit()
            flash("New restaurant created - {}".format(new_restaurant.name))
            tag_line = request.form['tag_line']
            tag_list = tag_line.split(',')
            for tag in tag_list:
                helper.add_tag_if_not_exists(tag, new_restaurant.id)
            return redirect(url_for('restaurants_page'))
        else:
            flash("Incorrect Restaurant details - Please include a name!")

    user_info = helper.get_user_if_exists(login_session)
    return render_template('newrestaurant.html', user_info=user_info)


"""
Menu Items CRUD.

The following methods are for CRUD operations for the MenuItems
"""


@app.route('/restaurants/<int:restaurant_id>/menu')
def restaurant_menu(restaurant_id):
    """
    Display the menu items for a particular restaurant.

    arguments:  restaurant_id (for that particular restaurant)
    returns:    render the "restaurantmenu.html" template
                    - pass: restaurant obj, menu_list, user_info
    """
    restaurant = session.query(Restaurant).filter_by(id=restaurant_id).one()
    menu_list = session.query(MenuItem).filter_by(restaurant_id=restaurant_id).order_by("likes-dislikes desc")
    user_info = helper.get_user_if_exists(login_session)
    return render_template('restaurantmenu.html',
                           restaurant=restaurant,
                           menu_list=menu_list,
                           user_info=user_info)


@app.route('/restaurants/<int:restaurant_id>/<int:menu_id>/edit', methods=['GET', 'POST'])
def menu_item_edit(restaurant_id, menu_id):
    """
    Edit the menu item details - only allow authenticated users to do so.

    arguments:  restaurant_id (for that particular restaurant),
                menu_id (for that particular item)
    returns:    if get - render the "editmenu.html" template
                            - pass: restaurant obj, menu_item obj, user_info,
                if post - redirect to the restaurant_menu function to
                            get the (main) page
    """
    # If the user isn't logged in, send to the login page
    if helper.handle_login(login_session) is False:
        return redirect('/login')

    restaurant = session.query(Restaurant).filter_by(id=restaurant_id).one()
    menu_item = session.query(MenuItem).filter_by(id=menu_id).one()
    if request.method == 'POST':
        if len(request.form['price']) > 0:
            if '$' in request.form['price']:
                menu_item.price = request.form['price']
            else:
                menu_item.price = '$' + request.form['price']
        if len(request.form['description']) > 0:
            menu_item.description = request.form['description']
        if 'course' in request.form:
            menu_item.course = request.form['course']
        if 'file' in request.files:
            img_id = helper.create_new_image_if_not_exists(file=request.files['file'],
                                                           title=request.form['img_name'])
            if img_id != -1:
                menu_item.image_id = img_id
        session.add(menu_item)
        session.commit()
        flash("Menu item {} edited!".format(menu_item.name))
        return redirect(url_for('restaurant_menu', restaurant_id=restaurant_id))
    else:
        user_info = helper.get_user_if_exists(login_session)
        return render_template('editmenu.html',
                               restaurant=restaurant,
                               menu_item=menu_item,
                               user_info=user_info)


@csrf.include
@app.route('/restaurants/<int:restaurant_id>/<int:menu_id>/delete', methods=['GET', 'POST'])
def menu_item_delete(restaurant_id, menu_id):
    """
    menu_item_delete
    Delete the menu item details - only allow the user who created it to do so
    arguments:  restaurant_id (for that particular restaurant), menu_id (for that particular item)
    returns:    if get - render the "deletemenu.html" template
                            - pass: restaurant obj, menu_item obj, user_info,
                if post - redirect to the restaurant_menu function to get the (main) page
    """
    # If the user isn't logged in, send to the login page
    if helper.handle_login(login_session) is False:
        return redirect('/login')

    if request.method == 'POST':
        helper.delete_menu_item(menu_id)
        return redirect(url_for('restaurant_menu', restaurant_id=restaurant_id))
    else:
        restaurant = session.query(Restaurant).filter_by(id=restaurant_id).first()
        menu_item = session.query(MenuItem).filter_by(id=menu_id).first()
        user_info = helper.get_user_if_exists(login_session)
        return render_template('deletemenu.html',
                               restaurant=restaurant,
                               menu_item=menu_item,
                               user_info=user_info)


@csrf.include
@app.route('/restaurants/<int:restaurant_id>/new/', methods=['GET', 'POST'])
def menu_item_new(restaurant_id):
    """
    Create a new menu item - only allow authenticated users to do so.

    arguments:  restaurant_id (for that particular restaurant)
    returns:    if get - render the "newmenuitem.html" template
                            - pass: restaurant obj, user_info,
                if post - redirect to the restaurant_menu function to
                            get the (main) page
    """
    # If the user isn't logged in, send to the login page
    if helper.handle_login(login_session) is False:
        return redirect('/login')

    restaurant = session.query(Restaurant).filter_by(id=restaurant_id).one()
    img_id = 0
    if request.method == 'POST':
        if 'file' in request.files:
            print("File found")
            img_id = helper.create_new_image_if_not_exists(file=request.files['file'],
                                                           title=request.form['img_name'])
            new_item = MenuItem(name=request.form['name'],
                                description=request.form['description'],
                                price=request.form['price'],
                                course=request.form['course'],
                                likes=0,
                                dislikes=0,
                                restaurant_id=restaurant_id,
                                user_id=login_session['user_id'],
                                image_id=img_id)
            session.add(new_item)
            session.commit()
            flash("New Menu Item {} created!".format(new_item.name))
        return redirect(url_for('restaurant_menu', restaurant_id=restaurant_id))
    else:
        user_info = helper.get_user_if_exists(login_session)
        return render_template('newmenuitem.html', restaurant=restaurant, user_info=user_info)


""" Reviews """


@csrf.exempt
@app.route('/restaurants/<int:restaurant_id>/addnewreview', methods=['GET', 'POST'])
def add_new_review(restaurant_id):
    """
    Create a new review - allow anonymous reviews
    arguments:  restaurant_id (for that particular restaurant), menu_id (for that particular item)
    returns:    if post - Create the review in the database and redirect to the
                            restaurant_menu function to get the (main) page
    """
    # If the user isn't logged in, send to the login page
    if helper.handle_login(login_session) is False:
        return redirect('/login')

    if request.method == 'POST':
        post = request.get_json()
        if 'username' not in login_session:
            new_review = Reviews(reviewer_name='anonymous',
                                 review=post.get('review'),
                                 stars=post.get('stars'),
                                 restaurant_id=restaurant_id,
                                 time=datetime.utcnow())
        else:
            new_review = Reviews(reviewer_name=login_session['username'],
                                 review=post.get('review'),
                                 stars=post.get('stars'),
                                 restaurant_id=restaurant_id,
                                 time=datetime.utcnow())
        session.add(new_review)
        session.commit()

    return redirect(url_for('restaurants_page'))


@app.route('/restaurants/<int:restaurant_id>/image', methods=['GET', 'POST'])
def new_restaurant_image_pair(restaurant_id):
    """
    Return the specified menu item for that specified restaurant.

    arguments:  restaurant_id (for that particular restaurant)
    returns:    template for restaurants page
    """
    # Don't proceed unless the user is logged in
    if helper.handle_login(login_session) is False:
        return redirect('/login')

    if request.method == 'POST':
        # Create an entry in the database for the image, and save the file
        # If image exists, img_id will be the id of the existing image
        img_id = helper.create_new_image_if_not_exists(file=request.files['file'],
                                                       title=request.form['img_name'])
        # If image creation wasn't a problem, (img_id will be -1 if there was a problem)
        if img_id != -1:
            # If the restaurant_image pair exists, find it
            rest_img_exists = session.query(RestaurantImages).filter_by(image_id=img_id).first()
            # If the restaurant-image pair doesn't exist, create it
            # Also check that the restaurant-image pair that we found is for a different restaurant
            if rest_img_exists is None or restaurant_id != rest_img_exists.restaurant_id:
                rest_img = RestaurantImages(restaurant_id=restaurant_id,
                                            image_id=img_id)
                session.add(rest_img)
                session.commit()
    return redirect(url_for('restaurants_page'))
