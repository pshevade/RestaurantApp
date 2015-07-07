# routing.py
# All the routing functions
import random
import string
from datetime import datetime

from flask import render_template, url_for, request, redirect
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
        print("Restaurant name: {0}".format(restaurant.name))
        tag_pairs = session.query(RestaurantTags).filter_by(restaurant_id=restaurant.id).all()
        tag_list[restaurant.id] = []
        for pair in tag_pairs:
            tag_list[restaurant.id].append(session.query(Tags).filter_by(id=pair.tag_id).first())
            print(tag_list)
    # Find the top menu item for each restaurant - based on customer voting
    top_menu_item_list = helper.get_top_menu_items(restaurant_list)
    print("The top menu item list is: {}".format(top_menu_item_list))
    # Get the user data, if user has logged in
    user_info = helper.get_user_if_exists(login_session)
    if user_info is not None:
        print("User name: {}".format(user_info.name))
        print("User email: {}".format(user_info.email))
        print("User id: {}".format(user_info.id))

    print("This is the user_info: {}".format(user_info))
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
    restaurant = session.query(Restaurant).filter_by(id=restaurant_id).one()
    if request.method == 'POST':
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

        print("inside post for restaurants edit")
        session.add(restaurant)
        session.commit()
        return redirect(url_for('restaurants_page'))
    else:
        # Get user info if the user is signed in to render edit form
        user_info = helper.get_user_if_exists(login_session)
        tag_rest_list = session.query(RestaurantTags).filter_by(restaurant_id=restaurant.id).all()
        tag_line = ''
        for pair in tag_rest_list:
            tag = session.query(Tags).filter_by(id=pair.tag_id).first()
            print("the growing tag line is:")
            print("the tag is {}".format(tag.tag_name))
            tag_line += tag.tag_name + ', '
            print(tag_line)
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
    print("inside restaurant delete")
    restaurant = session.query(Restaurant).filter_by(id=restaurant_id).one()
    # Delete all menu items, reviews, and images for the restaurant
    if request.method == 'POST':
        print("Post, so going to delete restaurant")
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
    if helper.handle_login(login_session) is False:
        return redirect('/login')

    if request.method == 'POST':
        print("inside post for restaurants news")
        new_restaurant = Restaurant(name=request.form['name'],
                                    address=request.form['address'],
                                    phone=request.form['phone'],
                                    web=helper.check_restaurant_URL(request.form['web']),
                                    description=request.form['description'],
                                    user_id=login_session['user_id'])
        session.add(new_restaurant)
        session.commit()
        # new_rest_obj = session.query(Restaurant).filter_by
        tag_line = request.form['tag_line']
        tag_list = tag_line.split(',')
        for tag in tag_list:
            helper.add_tag_if_not_exists(tag, new_restaurant.id)

        return redirect(url_for('restaurants_page'))
    else:
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
    if helper.handle_login(login_session) is False:
        return redirect('/login')

    print("IN menu item edit")
    restaurant = session.query(Restaurant).filter_by(id=restaurant_id).one()
    menu_item = session.query(MenuItem).filter_by(id=menu_id).one()
    if request.method == 'POST':
        print("Inside request method = post")
        # if len(request.form['name']) > 0:
        # 	menu_item.name = request.form['name']
        if len(request.form['price']) > 0:
            if '$' in request.form['price']:
                menu_item.price = request.form['price']
            else:
                menu_item.price = '$' + request.form['price']
        else:
            print("Item price is not changed")
        if len(request.form['description']) > 0:
            menu_item.description = request.form['description']
        else:
            print("Description is not changed")
        if 'course' in request.form:
            menu_item.course = request.form['course']
        else:
            print("Course is not changed")
        if 'file' in request.files:
            img_id = helper.create_new_image_if_not_exists(file=request.files['file'],
                                                           title=request.form['img_name'])
            if img_id != -1:
                menu_item.image_id = img_id
        session.add(menu_item)
        session.commit()
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
    if helper.handle_login(login_session) is False:
        return redirect('/login')

    restaurant = session.query(Restaurant).filter_by(id=restaurant_id).one()
    img_id = 0
    if request.method == 'POST':
        print("inside post for restaurants news")
        # if 'file' in request.files:
        #     print("image file exists")
        #     img_id = helper.create_new_image_if_not_exists(file = request.files['file'], title = request.form['img_name'])
        # if img_id != -1:
        print("Inside request method = post")
        # if len(request.form['name']) > 0:
        #   menu_item.name = request.form['name']
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
        else:
            print("Error, incorrect file: {}".format(request.files['file']))

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

    print("Inside add_new_review")
    if helper.handle_login(login_session) is False:
        return redirect('/login')

    if request.method == 'POST':
        print("inside post for restaurants new review")
        print(request)
        post = request.get_json()
        print("THe post is: {0}".format(post))
        # print("THe author is: {0}".format(param))
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

        print("The new review object looks like: ")
        # print(login_session['username'])
        print(new_review.review)
        print(new_review.stars)
        print(new_review.restaurant_id)
        session.add(new_review)
        session.commit()

    return redirect(url_for('restaurants_page'))


@app.route('/restaurant/<int:item_id>/<int:vote>')
def vote_for_item(item_id, vote):
    """
    Vote for an item - allow only authenticated users to vote on items.

    TODO : implement such that one user can do one vote for one item.
    arguments:  item_id (for that particular item), vote (1 for yes, 2 for no)
    returns:    increment/decrement the item's rating - and redirect to restaurant_menu
    """
    if helper.handle_login(login_session) is False:
        return redirect('/login')

    item = session.query(MenuItem).filter_by(id=item_id).one()

    if vote == 1:
        item.likes += 1
    elif vote == 2:
        item.dislikes += 1
    session.add(item)
    session.commit()
    return redirect(url_for('restaurant_menu', restaurant_id=item.restaurant_id))


@app.route('/restaurants/<int:restaurant_id>/image', methods=['GET', 'POST'])
def new_restaurant_image_pair(restaurant_id):
    """
    Return the specified menu item for that specified restaurant.

    arguments:  restaurant_id (for that particular restaurant)
    returns:    template for restaurants page
    """
    print("Inside upload_file ")
    # Don't proceed unless the user is logged in
    if helper.handle_login(login_session) is False:
        return redirect('/login')
    print("User logged in")

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
        else:
            print("Error, incorrect file: {}".format(request.files['file']))
    return redirect(url_for('restaurants_page'))


# @app.route('/restaurants/<int:restaurant_id>/<int:img_id>/delete', methods=['GET', 'POST'])
# def delete_image_file(restaurant_id, img_id):
#     if helper.handle_login(login_session) is False:
#         return redirect('/login')

#     image = session.query(Image).filter_by(id=img_id).first()
#     restaurant_img_pair = session.query(RestaurantImages).filter_by(image_id=img_id).first()

#     if request.method == 'POST':
#         session.delete(image)
#         session.delete(restaurant_img_pair)

#     return redirect(url_for('restaurants_page'))
    # else:
    #     user_info = helper.get_user_if_exists(login_session)
    #     return render_template('deletemenu.html', restaurant = restaurant, menu_item = menu_item, user_info = user_info)
