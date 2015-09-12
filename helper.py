""" helper.py.

    This file has the functions necessary to carry out processing
    but not related to routing directly
"""

from session_setup import session
from flask import flash
from flask_setup import ALLOWED_EXTENSIONS, app, UPLOAD_FOLDER
from database_setup import User, Restaurant, MenuItem, \
    Image, Tags, RestaurantTags, Reviews, RestaurantImages, UserVotes
from urlparse import urlparse
from werkzeug import secure_filename
from authentication import login_session
import os
import string


def get_top_menu_items(restaurant_list):
    """
    Return the most voted item for each restaurant.

    arguments:  restaurant_list (list of all restaurants)
    returns:    get the menu item list for each restaurant, find the score
                for each item, return the top voted item for each restaurant
    """
    top_items_list = {}
    score = 0
    appended = 0
    for restaurant in restaurant_list:
        menu_list = session.query(MenuItem).filter_by(restaurant_id=restaurant.id)
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


def create_user(login_session):
    """
    create a user object in the database & store the username, email, picture.

    arguments:  login_session object
    returns:    the user id for the newly created user.
    """
    new_user = User(name=login_session['username'],
                    email=login_session['email'],
                    picture=login_session['picture'])
    session.add(new_user)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id


def get_user_info(user_id):
    """
    return the user's object from the database, else return none.

    arguments:  user id
    returns:    Find the user in the database and return the first instance of
                that user id
    """
    user = session.query(User).filter_by(id=user_id).first()
    return user


def get_user_id(email):
    """
    Find the user id based on the email.

    arguments:  the user's email
    returns:    return the user id or None if not found
    """
    try:
        user = session.query(User).filter_by(email=email).first()
        return user.id
    except:
        return None


def get_user_if_exists(login_session):
    """
    return the user's info (call the get_user_info fn) if user exists.

    arguments:  login_session object
    returns:    return the user's info if the user exists, else return none
    """
    user_info = None
    if 'username' in login_session:
        user_ID = get_user_id(login_session['email'])
        user_info = get_user_info(user_ID)

    return user_info


def handle_login(login_session):
    """
    Check if the user's email is in the login_session.

    arguments:  login_session
    returns:    True is the user's email is in the login_session
    """
    # To debug, comment out the next if statement
    if 'email' not in login_session:
        return False
    return True


def check_restaurant_URL(link):
    """
    Check if the restaurant URL has a valid scheme.

    Else add the "http://"
    arguemnts:  link - the url
    returns:    updated link
    """
    link_url_obj = urlparse(link)
    if link_url_obj.scheme is '':
        link = 'http://' + link
    return link


def allowed_file(filename):
    """ Check if file type is in the allowed list """
    return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


def create_new_image_if_not_exists(file, title):
    """
    create a new image if it doesn't already exist.

    arguemnts:  file object, title of the image
    returns:    image id, either a new id or existing image id (-1 if error)
    """
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        image_path = os.path.join(UPLOAD_FOLDER, filename)
        image_exists = session.query(Image).filter_by(image_path=file_path).first()
        if image_exists is None:
            newimage = Image(image_title=title,
                             image_path=image_path,
                             upload_by=login_session['user_id'])
            session.add(newimage)
            session.commit()
            img_id = newimage.id
        else:
            img_id = image_exists.id
    else:
        img_id = None
    return img_id


def delete_restaurant(restaurant_id):
    """
    Delete a restaurant entry.

    Cascade through and remove all related entries first, including the
    images, menu_items, revies, tags.
    """
    print("In delete restaurant")
    try:
        restaurant = session.query(Restaurant).filter_by(id=restaurant_id).first()
        name = restaurant.name
        menu_items = session.query(MenuItem).filter_by(restaurant_id=restaurant_id).all()
        for item in menu_items:
            delete_menu_item(item.id)
        images_list = session.query(RestaurantImages).filter_by(restaurant_id=restaurant_id).all()
        for image in images_list:
            delete_image(image.id)
            session.delete(image)
            session.commit()
        reviews_list = session.query(Reviews).filter_by(restaurant_id=restaurant.id).all()
        for review in reviews_list:
            delete_review(review.id)
        tag_list = session.query(RestaurantTags).filter_by(restaurant_id=restaurant_id).all()
        for tag_pair in tag_list:
            delete_tag(tag_pair.tag_id)
            session.delete(tag_pair)
            session.commit()
        session.delete(restaurant)
        session.commit()
        flash("Restaurant {} deleted!".format(name))
        return 1
    except:
        return 0


def delete_tag(tag_id):
    """ Delete a tag from the database, if exists. """
    try:
        tag = session.query(Tags).filter_by(id=tag_id).first()
        session.delete(tag)
        session.commit()
        return 1
    except:
        return 0


def delete_review(review_id):
    """ Delete a review from the database, if exists. """
    # Find the review
    try:
        review = session.query(Reviews).filter_by(id=review_id).first()
        session.delete(review)
        session.commit()
        return 1
    except:
        return 0


def delete_menu_item(menu_id):
    """ Delete a menu from the database, if exists. """
    try:
        menu_item = session.query(MenuItem).filter_by(id=menu_id).first()
        name = menu_item.name
        item_votes = session.query(UserVotes).filter_by(menu_id=menu_item.id).all()
        # Delete associated images
        delete_image(menu_item.image_id)
        # Delete menu item
        for vote in item_votes:
            session.delete(vote)
            session.commit()
        session.delete(menu_item)
        session.commit()
        flash("Menu item {} deleted".format(name))
        return 1
    except:
        return 0


def delete_image(image_id):
    """ Delete the image from the database, if exists. """
    try:
        # Find image to delete
        image = session.query(Image).filter_by(id=image_id).first()
        session.delete(image)
        session.commit()
        return 1
    except:
        return 0


def delete_restaurant_tag_pairs(rid):
    """ Find restaurant_tag_pairs for a restaurant and delete """
    pairs = session.query(RestaurantTags).filter_by(restaurant_id=rid).all()
    for pair in pairs:
        session.delete(pair)
        session.commit()


def add_tag_if_not_exists(tag, rid):
    """
    Check if tag and restaurant pair exists, or else create.

    arguments:  tag - string, rid - restaurant id
    """

    tag = string.strip(tag)    # remove the leading white spaces
    if len(tag) > 0:
        tag_obj = session.query(Tags).filter_by(tag_name=tag).first()
        if tag_obj is None:
            tag_obj = Tags(tag_name=tag)
            session.add(tag_obj)
            session.commit()
            restaurant_tag_pair = RestaurantTags(tag_id=tag_obj.id, restaurant_id=rid)
        else:
            # IF tag exists, see if the tag and restaurant pair exists.
            restaurant_tag_pair = session.query(RestaurantTags).filter_by(restaurant_id=rid, tag_id=tag_obj.id).first()
            if restaurant_tag_pair is None:
                # If the pair doesnt exist, create the pair
                restaurant_tag_pair = RestaurantTags(tag_id=tag_obj.id, restaurant_id=rid)
        session.add(restaurant_tag_pair)
        session.commit()
