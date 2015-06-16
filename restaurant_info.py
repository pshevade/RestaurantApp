# final_projects.py
from flask import Flask, render_template, url_for, request, redirect, flash, jsonify
app = Flask(__name__)

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Restaurant, MenuItem


engine = create_engine('sqlite:///restaurantmenu.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


@app.route('/')
@app.route('/restaurants')
def restaurantsPage():
    #return "This is the main restaurants page"
    restaurant_list = session.query(Restaurant)
    top_menu_item_list = getTopMenuItems(restaurant_list)
    return render_template('index.html', restaurant_list=restaurant_list, top_menu_items = top_menu_item_list)


@app.route('/restaurant/<int:item_id>/<int:vote>')
def voteForItem(item_id, vote):
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
    restaurant = session.query(Restaurant).filter_by(id = restaurant_id).one()
    if request.method == 'POST':
        print("inside post for restaurants edit")
        restaurant.name = request.form['name']
        session.add(restaurant)
        session.commit()
        return redirect(url_for('restaurantsPage'))
    else:
        return render_template('editrestaurant.html', restaurant = restaurant)


@app.route('/restaurants/<int:restaurant_id>/delete', methods=['GET','POST'])
def restaurantsDelete(restaurant_id):
    #return "This is the edit restaurants page for restaurant {0}".format(restaurant_id)
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
    if request.method == 'POST':
        print("inside post for restaurants news")
        newRestaurant = Restaurant(name=request.form['name'])
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


if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host = '0.0.0.0', port = 5000)
