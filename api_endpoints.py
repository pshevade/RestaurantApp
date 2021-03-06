""" API endpoints.

THis file has the routing functions for all the API endpoints

"""
from flask import url_for, request, jsonify, redirect
from flask_setup import app, csrf
from authentication import login_session
from werkzeug.contrib.atom import AtomFeed
from session_setup import session
from database_setup import Restaurant, MenuItem, Reviews, User, RestaurantImages, UserVotes
from helper import handle_login


@csrf.exempt
@app.route('/restaurants/vote/<int:item_id>/<int:vote>', methods=['GET', 'POST'])
def vote_for_item(item_id, vote):
    """
    Vote for an item - allow only authenticated users to vote on items.

    arguments:  item_id (for that particular item), vote (1 for yes, 2 for no)
    returns:    increment/decrement the item's rating - and redirect to restaurant_menu
    """
    if handle_login(login_session) is False:
        return redirect('/login')

    user = session.query(User).filter_by(email=login_session['email']).first()
    item = session.query(MenuItem).filter_by(id=item_id).one()
    # check if user has voted on the item
    update_vote = False
    user_vote = session.query(UserVotes).filter_by(user_id=user.id, menu_id=item.id).first()
    if request.method == 'POST':
        if user_vote is not None:
            if user_vote.vote != vote:
                # we have to reset the vote first
                if vote == 1:
                    # We will add one to likes below when we update vote
                    item.dislikes -= 1
                elif vote == 2:
                    item.likes -= 1
                    # we will add to dislikes below when we update vote
                # Update the user's vote to the new vote
                user_vote.vote = vote
                update_vote = True
            elif user_vote.vote == vote:
                update_vote = False
        # If there is no user - vote record for this menu item, create one
        elif user_vote is None:
            user_vote = UserVotes(user_id=user.id, menu_id=item.id, vote=vote)
            update_vote = True
        # Update the vote
        if update_vote:
            if vote == 1:
                item.likes += 1
            elif vote == 2:
                item.dislikes += 1
            session.add(item)
            session.commit()
            session.add(user_vote)
            session.commit()
        else:
            pass

    return jsonify(Item=item.serialize)


@app.route('/restaurants/<int:restaurant_id>/reviews/JSON')
def restaurant_reviews_list_json(restaurant_id):
    """ Returns:    json object for all the reviews for that restaurant. """
    reviews_list = session.query(Reviews).filter_by(restaurant_id=restaurant_id).order_by("time desc")
    return jsonify(ReviewsList=[review.serialize for review in reviews_list])


@app.route('/restaurants/JSON')
def restaurant_list_json():
    """ Returns:    json object of details for all restaurants. """
    restaurant_list = session.query(Restaurant)
    return jsonify(RestaurantList=[restaurant.serialize for restaurant in restaurant_list])


@app.route('/restaurants/<int:restaurant_id>/JSON')
def restaurant_json(restaurant_id):
    """ Returns:    json object of details for that restaurant restaurants. """
    restaurant = session.query(Restaurant).filter_by(id=restaurant_id).first()
    return jsonify(Restaurant=restaurant.serialize)


@app.route('/restaurants/<int:restaurant_id>/menu/JSON')
def restaurant_menu_json(restaurant_id):
    """ Returns:    json object for all the menu items for that restaurant. """
    items = session.query(MenuItem).filter_by(restaurant_id=restaurant_id)
    return jsonify(MenuItems=[i.serialize for i in items])


@app.route('/restaurants/<int:restaurant_id>/<int:menu_id>/JSON')
def restaurant_menu_item_json(restaurant_id, menu_id):
    """ Returns:    json object for with the details of menu item for specific restaurant. """
    item = session.query(MenuItem).filter_by(id=menu_id).one()
    return jsonify(MenuItem=item.serialize)


@app.route('/restaurants/images/<int:restaurant_id>/JSON')
def restaurant_images_json(restaurant_id):
    """ Returns:    json object for with the details of the restaurant/meny images. """
    images_list = []
    restaurant_img_list = session.query(RestaurantImages).filter_by(restaurant_id=restaurant_id).all()
    for rest_img in restaurant_img_list:
        images_list.append(rest_img.image)
    menu_items = session.query(MenuItem).filter_by(restaurant_id=restaurant_id).all()
    for item in menu_items:
        images_list.append(item.image)
    return jsonify(RestaurantImagesList=[img.serialize for img in images_list])


@app.route('/restaurants/RSS')
def restaurant_list_rss():
    """
    Return the restaurant list RSS feed.

    arguments:
    returns:    RSS feed with the details of all restaurants
    """
    feed = AtomFeed("Restaurants", feed_url=request.url,
                    url=request.host_url,
                    subtitle="List of all restaurants")
    restaurant_list = session.query(Restaurant)
    for restaurant in restaurant_list:
        feed.add(restaurant.name,
                 restaurant.description,
                 content_type='html',
                 author=restaurant.user.name,
                 url=url_for('restaurant_menu', restaurant_id=restaurant.id),
                 id=restaurant.id,
                 updated=restaurant.last_update,
                 published=restaurant.last_update)
    return feed.get_response()
