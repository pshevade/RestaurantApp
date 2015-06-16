from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database_setup import Restaurant, Base, Tags, Reviews, MenuItem

engine = create_engine('sqlite:///myrestaurantmenu.db')
# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
# A DBSession() instance establishes all conversations with the database
# and represents a "staging zone" for all the objects loaded into the
# database session object. Any change made against the objects in the
# session won't be persisted into the database until you call
# session.commit(). If you're not happy about the changes, you can
# revert all of them back to the last commit by calling
# session.rollback()
session = DBSession()



#Menu for Madras Cafe
restaurant1 = Restaurant(name = "Madras Cafe",
                        address = "1177 W El Camino Real, Sunnyvale, CA 94087",
                        phone = "408-737-2323",
                        web = "http://www.madrascafe.us",
                        tag_line = "Local, fast, and decent South Indian food, cheap!",
                        description = "Madras Cafe is a good place to get some cheap and decent quality South Indian Food. Located right on El Camino rd, Madras Cafe has only grown desipte the stiff competition."
                        )

session.add(restaurant1)
session.commit()

tag1 = Tags(tag_name = "South Indian",
            restaurant = restaurant1)
session.add(tag1)
session.commit()
tag2 = Tags(tag_name = "cheap",
            restaurant = restaurant1)
session.add(tag2)
session.commit()
tag3 = Tags(tag_name = "idli",
            restaurant = restaurant1)
session.add(tag3)
session.commit()
tag4 = Tags(tag_name = "dosa",
            restaurant = restaurant1)

session.add(tag4)
session.commit()
restaurant2 = Restaurant(name = "Panera Bread",
                        address = "1035 El Monte Ave, Mountain View, CA",
                        phone = "650-968-2066",
                        web = "http://www.panerabread.com",
                        tag_line = "US Chain featuring bakery products, sandwiches, and salads",
                        description = "Panera bread serves good, healthy food, at reasonable rates. The food that won't make you feel crappy after eating!"
                        )

session.add(restaurant2)
session.commit()

tag1 = Tags(tag_name = "bakery",
            restaurant = restaurant2)
session.add(tag1)
session.commit()
tag2 = Tags(tag_name = "bread",
            restaurant = restaurant2)
session.add(tag2)
session.commit()
tag3 = Tags(tag_name = "salad",
            restaurant = restaurant2)
session.add(tag3)
session.commit()
tag4 = Tags(tag_name = "sandwich",
            restaurant = restaurant2)
session.add(tag4)
session.commit()
