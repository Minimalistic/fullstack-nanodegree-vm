from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Restaurant, MenuItem

engine = create_engine('sqlite:///restaurantmenu.db')

Base.metadata.bind = engine

DBSession = sessionmaker(bind = engine)
session = DBSession()

# List first result of the 'Restaurant' column.
firstResult = session.query(Restaurant).first()

# Command to display column information for each item.
items = session.query(MenuItem).all()

# When console is up, command such as
# for item in items:
# 		print item.name
# will list out all of the menu items.
# would like to make that a easy command in future.

# CRUD Update
veggieBurgers = session.query(MenuItem).filter_by(name = 'Veggie Burger')
for veggieBurger in veggieBurgers:
	print veggieBurger.id
	print veggieBurger.price
	print veggieBurger.restaurant.name
	print "\n"

UrbanVeggieBurger = session.query(MenuItem).filter_by(id = 10).one()