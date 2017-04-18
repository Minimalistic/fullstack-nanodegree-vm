import sys

from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine
from sqlalchemy.orm import backref

Base = declarative_base()
####### insert at end of file #######

class Restaurant(Base):
    __tablename__ = 'restaurant'

    name = Column(String(250), nullable=False)
    id = Column(Integer, primary_key=True)

##commented out for bugtesting
##class Employee(Base):
##  __tablename__ = 'employee'
##
##  name = Column(String(250), nullable=False)
##  id = Column(Integer)

class MenuItem(Base):
    __tablename__ = 'menu_item'

    name = Column(String(80), nullable=False)
    id = Column(Integer, primary_key=True)
    description = Column(String(250))
    price = Column(String(8))
    course = Column(String(250))
    restaurant_id = Column(Integer, ForeignKey('restaurant.id'))
    restaurant = relationship(
                            Restaurant,
                            backref=backref("children",
                            cascade="all, delete"))

    @property
    def serialize(self):
        #Returns object data in easily serializeable format
        return {
            'name'        : self.name,
            'description' : self.description,
            'id'          : self.id,
            'price'       : self.price,
            'course'      : self.course,
        }

## creates the file
engine = create_engine('sqlite:///restaurantmenu.db')

Base.metadata.create_all(engine)