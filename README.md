Restaurants and Menus Application

What it uses/Requirements:
1. Flask Framework (http://flask.pocoo.org/) 
2. Python 2.7.6+ (https://www.python.org/download/releases/2.7.6/)
3. SQLAlchemy (http://www.sqlalchemy.org/) using a SQLite database
4. OAuth2 client - https://github.com/google/oauth2client 
5. Set up credentials with Google as per https://developers.google.com/identity/protocols/OAuth2
6. Save the client_secrets.json file (With the client ID and client secret) in a folder one step above where these files are stored 
   ex. if final_projects.py is in ../../MyFlaskWork/RestaurantApp/, then store client_secrets in ../../MyFlaskWork/


How it works:
1. Shows a list of restaurants @ '/' or '/restaurants'
2. Each restaurant displays its top voted menu item below it
3. Each restaurant displays the map to its location reviews for it, and the images associated with that restaurant
4. Each restaurant name is a link to the menu of that restaurant
5. You can log in using your Google credentials to explore more options - such as editing, deleting, adding new content
6. Upon logging in, you can edit all content. You can delete the content you have created. You can create new restaurants, add new reviews, and and images
 

7. Menu items page of each restaurant has items displayed grouped according to course (appetizers, entree, dessert, beverages)
   Each item can be edited only after log in, and deleted only by the person who created it
8. Each item entry displays the item name, price, description, and votes
9. You can vote like or dislike as many times as you like (maybe fix this in the future)


10. API endpoints -
- JSON data for restaurant list: @ '/restaurants/JSON'
- JSON data for each restaurant menu: @ '/restaurants/<int:restaurant_id>/JSON'
- JSON data for individual menu item: @ '/restaurants/<int:restaurant_id>/<int:menu_id>/JSON'
- JSON data for images per restaurant: @ '/restaurants/images/<int:restaurant_id>/JSON'
- JSON data for restaurant review per restaurant: @ '/restaurants/<int:restaurant_id>/reviews/JSON'


Python files:
1. database_setup.py - set up the ORM - Base class, Restaurant class, MenuItem class, Tag class, Review class, Images class.
2. session_setup.py - set up the session by adding all the imports and setting up the basic session 
3. routing.py - all the routing to relevant functions
4. helper.py - all functions that help with the functionality but aren't associated with any routing
5. authorization.py - all authorization functions
6. final_projects.py - main file that runs the program


/templates:
1. index.html - main file, list of restaurants
2. newrestaurant.html - form to create new restaurant, redirects back to index.html
3. editrestaurant.html - form edit specific restaurant (change name), redirects back to index.html
4. deleterestaurant.html - delete specific restaurant (asks again if you want to delete), redirects back to index.html
5. restaurantmenu.html - list of menu items sorted by course for specific restaurant
6. newmenuitem.html - form to create new menu item for a specific restaurant. Redirects to restaurantmenu.html
7. editmenuitem.html - form to edit existing menu item for a specific restaurant. redirects to restaurantmenu.html
8. deletemenu.html - deletes menuitem - asks user to confirm. redirects to restaurantment.html
9. navbar-template.html - contains the head section of html files and the basic navbar.
10. navbar-restaurant.html - contains the navbar details for restaurants page
11. navbar-restaurantdetails.html contains the navbar for the restaurant details (edit/add/delete)
12. navbar-menu.html - contains the navbar for the restaurant menu 

13. login.html - allows you to log in to Google to authenticate the user

/static

14. restaurant_app.js - javascript file for the AngularJS controllers and services

15. main.css - custom styling

/images folder - to hold uploaded images


TODOs:
1. Add CSRF protection
2. Add API endpoints for XML
3. Add feature to include users by invitation only
4. UI enhancement

BUGS:

