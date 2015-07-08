Restaurant Application

What it uses/Requirements:
1. Flask (0.10.1) (http://flask.pocoo.org/) 
2. Werkzeug (0.10.4) 
   (Above two are necessary to use request.get_requests(), or else you will see an error "AttributeError: 'Request' object has no attribute 'get_json' ". This is required for the AJAX requests.)

3. Python (2.7.6+) (https://www.python.org/download/releases/2.7.6/)
4. SQLAlchemy (0.8.4) (http://www.sqlalchemy.org/) using a SQLite database
5. OAuth2 client (1.4.11) - https://github.com/google/oauth2client   
6. Flask-SeaSurf (0.2.0) for the CSRF protection

TO RUN: 
1. Make sure the requirements are up to date. 
2. Set up credentials with Google as per https://developers.google.com/identity/protocols/OAuth2
3. Save the client_secrets.json file (With the client ID and client secret) in the same folder as final_projects.py
4. Update the "data-clientid" field in the login.html file to your client id that you have in the client_secrets.json file. (Under the "GOOGLE PLUS SIGN IN" comment) 
5. Go to the folder where all the project files (specifically, final_projects.py file) are stored

6. Enter command "python final_projects.py"
7. Open browser and navigate to "localhost:5000/restaurants"


WHAT CAN YOU DO:

As a user, you can do the following WITHOUT logging in:
1. View restaurant info, including the reviews, map, and images, that others have uploaded
2. View menu item info, including the details and images, that others have uploaded

As a user, you can do the following AFTER logging in:
1. Create restaurant
2. Add/edit details to a new/existing restaurant
3. Add reviews to a existing restaurant (including newly created ones)
4. Add images to a existing restaurants (including newly created ones)
   Note: In the main page ('/'' or '/restaurants') you can see images that users have uploaded as "Restaurant images"
   as well as images that have been uploaded to individual menu items (carousel used in the main page).
   Restaurant images (those uploaded to the "Restaurant" cannot be edited, but those uploaded to individual menu items can be edited - editing or deleting "Restaurant images" is a TODO).
7. Add/remove tags for existing restaurant
6. Delete existing restaurant that YOU (and not someone else) have created

6. Create menu items for existing restaurants
7. Edit menu items, including changing the image associated with the menu item.

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
9. You can vote like or dislike on every menu item if you are signed in. You can swap your vote, but can vote only once per item.

10. API endpoints -
- JSON data for restaurant list: @ '/restaurants/JSON'
- JSON data for individual restaurant: @ '/restaurant/<int:restaurant_id>/JSON'
- JSON data for each restaurant menu: @ '/restaurants/menu/JSON'
- JSON data for individual menu item: @ '/restaurants/<int:restaurant_id>/<int:menu_id>/JSON'
- JSON data for images per restaurant: @ '/restaurants/images/<int:restaurant_id>/JSON'
- JSON data for restaurant review per restaurant: @ '/restaurants/<int:restaurant_id>/reviews/JSON'
- RSS feed for restaurant information: @ '/restaurants/RSS'


Python files:
1. database_setup.py - set up the ORM - Base class, Restaurant class, MenuItem class, Tag class, Review class, Images class.
2. session_setup.py - set up the SQLalchemy session
3. flask_setup.py - set up the Flask app and the CSRF module
4. routing.py - all the routing to relevant functions
5. helper.py - all functions that help with the functionality but aren't associated with any routing
6. authentication.py - all authentication functions
7. api_endpoints.py - all api call functions
8. final_projects.py - main file that runs the program


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

/static:
14. restaurant_app.js - javascript file for the AngularJS controllers and services
15. main.css - custom styling:
/images folder - to hold uploaded images

/static/images/uploads:
all the uploaded image files.


TODOs:
1. create a user page, where the user can see details of their actions
2. Add feature to include users by invitation only
4. UI enhancement

BUGS:

