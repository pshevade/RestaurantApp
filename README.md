Restaurants and Menus Application

What it uses/Requirements:
1. Flask Framework (http://flask.pocoo.org/), Python + SQLAlchemy (http://www.sqlalchemy.org/) using a SQLite database
2. HTML/CSS (Javascript and AngularJS in the future)


How it works:
1. Shows a list of restaurants @ '/' or '/restaurants'
2. Each restaurant has an edit or delete option
3. Each restaurant displays its top voted menu item below it
4. On the restaurants page, you have the option of creating a new restaurant
5. Each restaurant name is a link to the menu of that restaurant

6. Menu items page of each restaurant has items displayed grouped according to course (appetizers, entree, dessert, beverages)
7. Each item can be edited or deleted
8. Each item entry displays the item name, price, description, and votes
9. You can vote like or dislike as many times as you like (maybe fix this in the future)
10. Menu items page allows user to create new menu item

11. API endpoints -
- JSON data for restaurant list: @ '/restaurants/JSON'
- JSON data for each restaurant menu: @ '/restaurants/<int:restaurant_id>/JSON'
- JSON data for individual menu item: @ '/restaurants/<int:restaurant_id>/<int:menu_id>/JSON'


Python files:
1. database_setup.py - set up the ORM - Base class, Restaurant class, MenuItem class.
2. lotsofmenus.py - file given in Udacity Full Stack Fundamentals course. Contains data for a lot of restaurants and menu items.
3. restaurant_info.py - file uses the Flask framework to create functions and routing for CRUD operations on restaurant/menu database


Templates:
1. index.html - main file, list of restaurants
2. newrestaurant.html - form to create new restaurant, redirects back to index.html
3. editrestaurant.html - form edit specific restaurant (change name), redirects back to index.html
4. deleterestaurant.html - delete specific restaurant (asks again if you want to delete), redirects back to index.html
5. restaurantmenu.html - list of menu items sorted by course for specific restaurant
6. newmenuitem.html - form to create new menu item for a specific restaurant. Redirects to restaurantmenu.html
7. editmenuitem.html - form to edit existing menu item for a specific restaurant. redirects to restaurantmenu.html
8. deletemenu.html - deletes menuitem - asks user to confirm. redirects to restaurantment.html


Updates:
1. revamp the look and layout. Where should edit/delete/new/etc. buttons go?
2. Allow feedback/review from user
3. javascript fancy stuff - angularjs would be awesome - how can i use Angular to do the voting/customer feedback, and hook it up to Flask?


BUGS:
1. If a restaurant is deleted, its menu items are not!!! They get reassigned to the next restaurant that gets created!?
2. Many buttons are not working - need to make sure they are "button type='submit'"
