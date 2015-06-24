import os
import sys
from datetime import datetime

from sqlalchemy import Column, ForeignKey, Integer, String, DateTime

from sqlalchemy.ext.declarative import declarative_base

from sqlalchemy.orm import relationship

from sqlalchemy import create_engine

Base = declarative_base()

class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    email = Column(String(100), nullable=False)
    picture = Column(String(150), nullable=True)


class Restaurant(Base):
    __tablename__ = 'restaurant'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    address = Column(String(250), nullable=True)
    phone = Column(String(16), nullable=True)
    web = Column(String(50), nullable=True)
    description = Column(String(500), nullable=True)
    last_update = Column(DateTime, default=datetime.utcnow())
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)

    @property
    def serialize(self):
        return {
            'name'      : self.name,
            'address'   : self.address,
            'phone'     : self.phone,
            'web'       : self.web,
            'description': self.description,
            'last_update': str(self.last_update)
        }


class Image(Base):
    __tablename__ = 'image'

    id = Column(Integer, primary_key=True)
    image_path = Column(String(50), nullable=False)
    upload_by = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)

    @property
    def serialize(self):
        return {
            'image_path': self.image_path,
            'user_name' : self.user.name,
            'user_email': self.user.email,
        }


class Tags(Base):
    __tablename__ = 'tags'

    id = Column(Integer, primary_key=True)
    tag_name = Column(String(50), nullable=False)
    restaurant_id = Column(Integer, ForeignKey('restaurant.id'))
    restaurant = relationship(Restaurant)


class Reviews(Base):
    __tablename__ = 'reviews'

    id = Column(Integer, primary_key=True)
    reviewer_name = Column(String(100), nullable=False)
    review = Column(String(500), nullable=False)
    stars = Column(Integer, nullable=False)
    time = Column(DateTime, default=datetime.utcnow())
    restaurant_id = Column(Integer, ForeignKey('restaurant.id'))
    restaurant = relationship(Restaurant)

    @property
    def serialize(self):

        return {
            'reviewer_name'     : self.reviewer_name,
            'review'            : self.review,
            'stars'             : self.stars,
            'id'                : self.id,
            'time'              : str(self.time),
        }


class MenuItem(Base):
    __tablename__ = 'menu_item'

    name = Column(String(80), nullable=False)
    id = Column(Integer, primary_key=True)
    description = Column(String(250))
    price = Column(String(10), nullable=False)
    course = Column(String(20), nullable=False)
    likes = Column(Integer, nullable=False)
    dislikes = Column(Integer, nullable=False)
    restaurant_id = Column(Integer, ForeignKey('restaurant.id'))
    restaurant = relationship(Restaurant)
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)

    # We added this serialize function to be able to send JSON objects in a serializable format
    @property
    def serialize(self):

        return {
            'name'          : self.name,
            'description'   : self.description,
            'id'            : self.id,
            'price'         : self.price,
            'course'        : self.course,
            'likes'         : self.likes,
            'dislikes'      : self.dislikes
        }


class MenuItemImages(Base):
    __tablename__ = 'menuitem_images'
    id = Column(Integer, primary_key=True)
    menu_id = Column(Integer, ForeignKey('menu_item.id'))
    menu_item = relationship(MenuItem)
    image_id = Column(Integer, ForeignKey('image.id'))
    image = relationship(Image)


class RestaurantImages(Base):
    __tablename__ = 'restaurant_images'
    id = Column(Integer, primary_key=True)
    restaurant_id = Column(Integer, ForeignKey('restaurant.id'))
    restaurant = relationship(Restaurant)
    image_id = Column(Integer, ForeignKey('image.id'))
    image = relationship(Image)


engine = create_engine('sqlite:///myrestaurantmenu.db')

Base.metadata.create_all(engine)

