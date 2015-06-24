# routing.py
# All the routing functions

from session_setup import *
from helper import *
from authentication import *

from datetime import datetime


""" 
    showLogin 
    Create the randomized state id 
    Show the login page to the user 
"""
@app.route('/login')
def showLogin():
    state =''.join(random.choice(string.ascii_uppercase +    string.digits)
        for x in xrange(32))
    login_session['state'] = state
    #return "The current session state is %s" % login_session['state']
    return render_template('login.html', STATE=state)


""" 
    restaurantsPage
    Get the list of users and show them to the screen
    arguments:  restaurant_id (for that restaurant)
    returns:    render the "index.html" tempalte 
                    - pass: restaurant_list, top_menu_items, tag_list, user_info, 
"""
@app.route('/')
@app.route('/restaurants')
def restaurantsPage():
    print("inside restaurants page")
    user_info = None
    if request.method == 'POST':
        print("We are reading stuff from form")

    elif request.method == 'GET':
        restaurant_list = session.query(Restaurant).order_by("last_update desc").all()
        reviews_list={}
        tag_list = {}
        for restaurant in restaurant_list:
            print("Restaurant name: {0}".format(restaurant.name))
            reviews_list[restaurant.id] = session.query(Reviews).filter_by(restaurant_id = restaurant.id)
            tag_list[restaurant.id] = session.query(Tags).filter_by(restaurant_id = restaurant.id)
        top_menu_item_list = getTopMenuItems(restaurant_list)
        print("The top menu item list is: {}".format(top_menu_item_list))
    user_info = getUserIfExists(login_session)
    if user_info is not None:
    	print("User name: {}".format(user_info.name))
    	print("User email: {}".format(user_info.email))
    	print("User id: {}".format(user_info.id))
    
    print("This is the user_info: {}".format(user_info))
    return render_template('index.html', 
                            restaurant_list=restaurant_list, 
                            top_menu_items = top_menu_item_list, 
                            tag_list=tag_list, 
                            user_info =user_info)



""" 
    restaurantsEdit
    Let the user (authenticated) edit the restaurant info
    arguments:  restaurant_id (for that restaurant)
    returns:    if post - redirect to the restaurantsPage to get the (main) page
                if get -  render the "editrestaurant.html" template 
                            - pass: restaurant object, user_info, 
"""
@app.route('/restaurants/<int:restaurant_id>/edit', methods=['GET','POST'])
def restaurantsEdit(restaurant_id):
    # Don't let any unauthenticated users make changes - route them to the login page
    if handle_login(login_session) is False:
        return redirect('/login')

    restaurant = session.query(Restaurant).filter_by(id = restaurant_id).one()
    if request.method == 'POST':
        if len(request.form['address']) > 0:
            restaurant.address = request.form['address']
        if len(request.form['phone']) > 0:
            restaurant.phone = request.form['phone']
        if len(request.form['web']) > 0:
            restaurant.web = checkRestaurantURL(request.form['web'])
        if len(request.form['tag_line']) > 0:
            restaurant.tag_line = request.form['tag_line']
        if len(request.form['description']) > 0:
            restaurant.description = request.form['description']

        restaurant.last_update = datetime.utcnow()

        print("inside post for restaurants edit")
        session.add(restaurant)
        session.commit()
        return redirect(url_for('restaurantsPage'))
    else:
    	user_info = getUserIfExists(login_session)
        return render_template('editrestaurant.html', restaurant = restaurant, user_info=user_info)


""" 
    restaurantsDelete
    Let the user who created this restaurant delete it 
    arguments:  restaurant_id (for that restaurant)
    returns:    if post - redirect to the restaurantsPage to get the (main) page
                if get -  render the "deleterestaurant.html" template 
                            - pass: restaurant obj, user_info,
"""
@app.route('/restaurants/<int:restaurant_id>/delete', methods=['GET','POST'])
def restaurantsDelete(restaurant_id):
    # If the user isn't logged in, route him to the login page
    if handle_login(login_session) is False:
        return redirect('/login')

    restaurant = session.query(Restaurant).filter_by(id=restaurant_id).one()
    menu_items = session.query(MenuItem).filter_by(restaurant_id=restaurant_id).all()
    reviews = session.query(Reviews).filter_by(restaurant_id=restaurant_id).all()
    # CHANGING CODE HERE TO FIX DELETE RESTAURANT - RIGHT NOW ALL RESTAURANT ATTRIBUTES ARE NOT BEING DELETED - JUNE 19 @ 12pm
    if request.method == 'POST':
        session.delete(restaurant)
        session.commit()
        return redirect(url_for('restaurantsPage'))
    else:
    	user_info = getUserIfExists(login_session)
        return render_template('deleterestaurant.html', restaurant=restaurant, user_info = user_info)


""" 
    restaurantsNew
    Create a new restaurant and add to database 
    arguments:  none 
    returns:    if post - redirect to the restaurantsPage to get the (main) page
                if get - render the "newrestaurant.html" template 
                            - pass: user_info
"""
@app.route('/restaurants/new', methods=['GET','POST'])
def restaurantsNew():
    if handle_login(login_session) is False:
        return redirect('/login')

    if request.method == 'POST':
        #print("INSIDE RESTAURANTNEW as POST - user is: {}".format(login_session['username']))
        print("inside post for restaurants news")
        newRestaurant = Restaurant( name=request.form['name'],
                                    address = request.form['address'],
                                    phone = request.form['phone'],
                                    web = checkRestaurantURL(request.form['web']),
                                    description = request.form['description'],
                                    last_update = datetime.utcnow(),
                                    user_id = login_session['user_id'])
        session.add(newRestaurant)
        session.commit()
        # new_rest_obj = session.query(Restaurant).filter_by
        tag_line = request.form['tag_line']
        tag_list = tag_line.split(',')
        for tag in tag_list:
            tag_obj = Tags(tag_name=tag, restaurant_id=newRestaurant.id)
            session.add(tag_obj)
            session.commit()

        return redirect(url_for('restaurantsPage'))
    else:
        #print("INSIDE RESTAURANTNEW as GET - user is: {}".format(login_session['username']))
        user_info = getUserIfExists(login_session)
        return render_template('newrestaurant.html', user_info = user_info)



""" 
    Menu Items CRUD - 
    The following methods are for CRUD operations for the MenuItems
"""

""" 
    restaurantMenu 
    Display the menu items for a particular restaurant
    arguments:  restaurant_id (for that particular restaurant) 
    returns:    render the "restaurantmenu.html" template 
                    - pass: restaurant obj, menu_list, user_info
"""
@app.route('/restaurants/<int:restaurant_id>/menu')
def restaurantMenu(restaurant_id):
    #return "This is the menu display page for restaurant {0}".format(restaurant_id)
    restaurant = session.query(Restaurant).filter_by(id=restaurant_id).one()
    #print("the menu for restaurant of id: {0}".format(restaurant.id))
    menu_list = session.query(MenuItem).filter_by(restaurant_id = restaurant_id).order_by("likes-dislikes desc")
    # .filter_by(course="Appetizers").all()
    # menu_list_entrees = session.query(MenuItem).filter_by(restaurant_id=restaurant_id).filter_by(course="Entree").all()
    # menu_list_desserts = session.query(MenuItem).filter_by(restaurant_id=restaurant_id).filter_by(course="Dessert").all()
    # menu_list
    user_info = getUserIfExists(login_session)
    return render_template('restaurantmenu.html', restaurant = restaurant, menu_list = menu_list, user_info = user_info)


""" 
    menuItemEdit 
    Edit the menu item details - only allow authenticated users to do so
    arguments:  restaurant_id (for that particular restaurant), menu_id (for that particular item) 
    returns:    if get - render the "editmenu.html" template 
                            - pass: restaurant obj, menu_item obj, user_info,
                if post - redirect to the restaurantMenu function to 
                            get the (main) page 
"""
@app.route('/restaurants/<int:restaurant_id>/<int:menu_id>/edit', methods=['GET', 'POST'])
def menuItemEdit(restaurant_id, menu_id):
    #return "This is the edit menu item page for restaurant {0} and item {1}".format(restaurant_id, menu_id)
    if handle_login(login_session) is False:
        return redirect('/login')

    print("IN menu item edit")
    restaurant = session.query(Restaurant).filter_by(id=restaurant_id).one()
    menu_item = session.query(MenuItem).filter_by(id=menu_id).one()
    if request.method == 'POST':
        # if len(request.form['name']) > 0:
        # 	menu_item.name = request.form['name']
        if len(request.form['price']) > 0:
        	menu_item.price = request.form['price']
        if len(request.form['description']) > 0:
        	menu_item.description = request.form['description']
        menu_item.course = request.form['course']
        return redirect(url_for('restaurantMenu', restaurant_id = restaurant_id))
    else:
    	user_info = getUserIfExists(login_session)
        return render_template('editmenu.html', restaurant = restaurant, menu_item = menu_item, user_info = user_info)


""" 
    menuItemDelete 
    Delete the menu item details - only allow the user who created it to do so
    arguments:  restaurant_id (for that particular restaurant), menu_id (for that particular item) 
    returns:    if get - render the "deletemenu.html" template 
                            - pass: restaurant obj, menu_item obj, user_info,
                if post - redirect to the restaurantMenu function to get the (main) page 
"""
@app.route('/restaurants/<int:restaurant_id>/<int:menu_id>/delete', methods=['GET', 'POST'])
def menuItemDelete(restaurant_id, menu_id):
    #return "This is the Delete menu item page for restaurant {0} and item {1}".format(restaurant_id, menu_id)
    if handle_login(login_session) is False:
        return redirect('/login')

    restaurant = session.query(Restaurant).filter_by(id=restaurant_id).one()
    menu_item = session.query(MenuItem).filter_by(id=menu_id).one()
    if request.method == 'POST':
        session.delete(menu_item)
        return redirect(url_for('restaurantMenu', restaurant_id = restaurant_id))
    else:
    	user_info = getUserIfExists(login_session)
        return render_template('deletemenu.html', restaurant = restaurant, menu_item = menu_item, user_info = user_info)


""" 
    menuItemNew 
    Create a new menu item - only allow authenticated users to do so
    arguments:  restaurant_id (for that particular restaurant) 
    returns:    if get - render the "newmenuitem.html" template 
                            - pass: restaurant obj, user_info,
                if post - redirect to the restaurantMenu function to 
                            get the (main) page 
"""
@app.route('/restaurants/<int:restaurant_id>/new', methods=['GET', 'POST'])
def menuItemNew(restaurant_id):
    #return "This is the new menu item page for restaurant {0}".format(restaurant_id)
    if handle_login(login_session) is False:
        return redirect('/login')

    restaurant = session.query(Restaurant).filter_by(id=restaurant_id).one()
    
    if request.method == 'POST':
        print("inside post for restaurants news")

        newItem = MenuItem( name = request.form['name'], 
                            description = request.form['description'], 
                            price = request.form['price'], 
                            course = request.form['course'], 
                            likes=0, 
                            dislikes=0, 
                            restaurant_id = restaurant_id,
                            user_id = login_session['user_id'])
        session.add(newItem)
        session.commit()
        return redirect(url_for('restaurantMenu', restaurant_id = restaurant_id))
    else:
    	user_info = getUserIfExists(login_session)
        return render_template('newmenuitem.html', restaurant = restaurant, user_info=user_info)


""" Reviews """

""" 
    addNewReview 
    Create a new review - allow anonymous reviews
    arguments:  restaurant_id (for that particular restaurant), menu_id (for that particular item) 
    returns:    if post - Create the review in the database and redirect to the 
                            restaurantMenu function to get the (main) page 
"""
@app.route('/restaurants/<int:restaurant_id>/addnewreview', methods=['GET', 'POST'])
def addNewReview(restaurant_id):
    #restaurant = session.query(Restaurant).filter_by(id = restaurant_id).one()
    # if 'username' not in login_session:
    #     return redirect('/login')
    print("Inside addNewReview")
    if handle_login(login_session) is False:
        return redirect('/login')   

    if request.method == 'POST':
        print("inside post for restaurants new review")
        print(request)
        post = request.get_json()
        print("THe post is: {0}".format(post))
        #print("THe author is: {0}".format(param))
        if 'username' not in login_session:
            newreview = Reviews(reviewer_name='anonymous',
                            review=post.get('review'),
                            stars=post.get('stars'),
                            restaurant_id=restaurant_id,
                            time=datetime.utcnow())
        else:
            newreview = Reviews(reviewer_name=login_session['username'],
                            review=post.get('review'),
                            stars=post.get('stars'),
                            restaurant_id=restaurant_id,
                            time=datetime.utcnow())
        
        print("The new review object looks like: ")
        # print(login_session['username'])
        print(newreview.review)
        print(newreview.stars)
        print(newreview.restaurant_id)
        session.add(newreview)
        session.commit()
    else:
        print("The restaurant name is to add new review is: {0}".format(restaurant.name))
    print("Moving out of addnewreview")
    return redirect(url_for('restaurantsPage'))


""" 
    voteForItem 
    Vote for an item - allow only authenticated users to vote on items
    TODO : implement such that one user can do one vote for one item.
    arguments:  item_id (for that particular item), vote (1 for yes, 2 for no) 
    returns:    increment/decrement the item's rating - and redirect to restaurantMenu 
"""
@app.route('/restaurant/<int:item_id>/<int:vote>')
def voteForItem(item_id, vote):
    if handle_login(login_session) is False:
        return redirect('/login')

    item = session.query(MenuItem).filter_by(id=item_id).one()

    if vote == 1:
        item.likes += 1
    elif vote == 2:
        item.dislikes += 1
    session.add(item)
    session.commit()
    return redirect(url_for('restaurantMenu', restaurant_id=item.restaurant_id))



""" API JSON Calls """

""" 
    restaurantReviewsListJSON 
    Return the reviews for one restaurant 
    arguments:  restaurant_id (for that particular restaurant)
    returns:    json object for all the reviews for that restaurant
"""
@app.route('/restaurants/<int:restaurant_id>/reviews/JSON')
def restaurantReviewsListJSON(restaurant_id):
    print("in review jsons for restaurant: {0}".format(restaurant_id))
    reviews_list = session.query(Reviews).filter_by(restaurant_id=restaurant_id).order_by("time desc")
    return jsonify(ReviewsList=[review.serialize for review in reviews_list])


""" 
    restaurantListJSON 
    Return the details for all restaurants 
    arguments:  none
    returns:    json object of details for all restaurants
"""
@app.route('/restaurants/JSON')
def restaurantListJSON():
    restaurant_list = session.query(Restaurant)
    return jsonify(RestaurantList=[restaurant.serialize for restaurant in restaurant_list])


""" 
    restaurantMenuJSON 
    Return the menu items for one restaurant
    arguments:  restaurant_id (for that particular restaurant)
    returns:    json object for all the items for that restaurant
"""
@app.route('/restaurants/<int:restaurant_id>/JSON')
def restaurantMenuJSON(restaurant_id):
    restaurant = session.query(Restaurant).filter_by(id=restaurant_id).one()
    items = session.query(MenuItem).filter_by(restaurant_id = restaurant_id)
    return jsonify(MenuItems=[i.serialize for i in items])


""" 
    restaurantMenuItemJSON 
    Return the specified menu item for that specified restaurant 
    arguments:  restaurant_id (for that particular restaurant)
    returns:    json object for with the details of that menu item for that restaurant
"""
@app.route('/restaurants/<int:restaurant_id>/<int:menu_id>/JSON')
def restaurantMenuItemJSON(restaurant_id, menu_id):
    item = session.query(MenuItem).filter_by(id=menu_id).one()
    return jsonify(MenuItem=item.serialize)


@app.route('/restaurants/images/<int:restaurant_id>/JSON')
def restaurantImagesJSON(restaurant_id):
    images_list = []
    print("in review jsons for restaurant: {0}".format(restaurant_id))
    restaurant_img_list = session.query(RestaurantImages).filter_by(restaurant_id=restaurant_id).all()
    for rest_img in restaurant_img_list:
        images_list.append(rest_img.image)
    return jsonify(RestaurantImagesList=[img.serialize for img in images_list])

@app.route('/restaurant/<int:restaurant_id>/image', methods=['GET', 'POST'])
def uploadFile(restaurant_id):
    print("Inside upload_file ")
    if handle_login(login_session) is False:
        return redirect('/login')
    print("User logged in")

    if request.method == 'POST':
        print("upload_file - POST method")
        file = request.files['file']
        if file and allowed_file(file.filename):
            print("upload_file - filename is ok")
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            print("The uploaded file path is: {}", file_path)
            file.save(file_path)
            image_exists = session.query(Image).filter_by(image_path=file_path).first()
            if image_exists is None:
                newimage = Image(image_path=file_path,
                                 upload_by=login_session['user_id'])
                session.add(newimage)
                session.commit()
                img_id = newimage.id
            else:
                img_id = image_exists.id
            rest_img_exists = session.query(RestaurantImages).filter_by(image_id = img_id).first()
            if rest_img_exists is None or restaurant_id != rest_img_exists.restaurant_id:
                rest_img = RestaurantImages(restaurant_id=restaurant_id,
                                            image_id = img_id)
                session.add(rest_img)
                session.commit()

    return redirect(url_for('restaurantsPage'))


@app.route('/restaurant/<int:restaurant_id>/<int:img_id>/delete', methods=['GET', 'POST'])
def deleteFile(restaurant_id, img_id):
    if handle_login(login_session) is False:
        return redirect('/login')

    image = session.query(Image).filter_by(id=img_id).first()
    restaurant_img_pair = session.query(RestaurantImages).filter_by(image_id=img_id).first()

    if request.method == 'POST':
        session.delete(image)
        session.delete(restaurant_img_pair)
    
    return redirect(url_for('restaurantsPage'))
    # else:
    #     user_info = getUserIfExists(login_session)
    #     return render_template('deletemenu.html', restaurant = restaurant, menu_item = menu_item, user_info = user_info)
