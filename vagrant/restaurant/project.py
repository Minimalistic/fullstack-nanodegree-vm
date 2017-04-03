from flask import Flask
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Restaurant, MenuItem

app = Flask(__name__)

engine = create_engine('sqlite:///restaurantmenu.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

#Welcome page
@app.route('/')
def WelcomePage():
    output = "<h1>Welcome to the Restaurants Project Main Page</h1>"
    output += "<a href='/restaurants'>Go to Restaurants List</a>"
    return output

#Restaurants page - currently lists all menu items rather than what it should.
@app.route('/restaurants')
def RestaurantsPage():
    restaurant = session.query(Restaurant).first()
    items = session.query(MenuItem).filter_by(restaurant_id=restaurant.id)
    output = ''

    output += "<a href = '/restaurants/new' > Make a New Restaurant Here </a></br></br>"

    for i in items:
        output += i.name
        output += '</br>'
        output += i.price
        output += '<br>'
        output += i.description
        output += '</br>'
        output += '</br>'
    return output

if __name__ == '__main__':
	app.debug = True
	app.run(host = '0.0.0.0', port = 5000)