
from flask import Flask, render_template
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Restaurant, MenuItem

app = Flask(__name__)

engine = create_engine('sqlite:///restaurantmenu.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

@app.route('/')
@app.route('/restaurant')
def MainPage():
    output = ''
    output += "<h1>Welcome to Restaurants and Menus</h1>"
    output += "<p>Below you will find the available Restaurants \
                in the database.</p>"
    output += "<a href ='/restaurants/1/menu/'>Restaurant 1</a>"
    output += "<br>"
    output += "<a href ='/restaurant/2/menu/'>Restaurant 2</a>"
    output += "<br>"
    output += "<a href ='/restaurant/3/menu/'>Restaurant 3</a>"
    output += "<br>"
    output += "<a href ='/restaurant/4/menu/'>Restaurant 4</a>"
    output += "<br>"
    output += "<a href ='/restaurant/5/menu/'>Restaurant 5</a>"
    output += "<br>"
    output += "<a href ='/restaurant/6/menu/'>Restaurant 6</a>"
    output += "<br>"
    output += "<a href ='/restaurant/7/menu/'>Restaurant 7</a>"
    output += "<br>"
    output += "<a href ='/restaurant/8/menu/'>Restaurant 8</a>"
    output += "<br>"
    output += "<a href ='/restaurant/9/menu/'>Restaurant 9</a>"
    output += "<p>Currently this list is not generated on the fly.</p>"
    return output

@app.route('/restaurant/<int:restaurant_id>/menu/')
def restaurantMenu(restaurant_id):
    restaurant = session.query(Restaurant).filter_by(id=restaurant_id).one()
    items = session.query(MenuItem).filter_by(restaurant_id=restaurant.id)
    return render_template('menu.html', restaurant=restaurant, items=items)
    # Old method without templating below:
    # output = ''
    # output += "<h3>"
    # output += "<a href='/'>Go Back to Main Page</a>"
    # output += "</h3>"
    # for i in items:
    #     output += i.name
    #     output += '</br>'
    #     output += i.price
    #     output += '</br>'
    #     output += i.description
    #     output += '</br>'
    #     output += "<a href ='/restaurant/<restaurant_id>/menu/<menu_id>/edit/'>Edit</a>"
    #     output += " / "
    #     output += "<a href ='/restaurant/<restaurant_id>/menu/<menu_id>/delete/'>Delete</a>"
    #     output += '</br>'
    #     output += '</br>'
    # output += "To add a new item to this menu, "
    # output += "<a href='#''>click here.</a>"
    # return output

# Task 1: Create route for newMenuItem function here
@app.route('/restaurant/<int:restaurant_id>/menu/new/')
def newMenuItem(restaurant_id):
    return "page to create a new menu item. Task 1 complete!"

# Task 2: Create route for editMenuItem function here
@app.route('/restaurant/<restaurant_id>/menu/<menu_id>/edit/')
def editMenuItem(restaurant_id, menu_id):
    return "page to edit a menu item. Task 2 complete!"

# Task 3: Create a route for deleteMenuItem function here
@app.route('/restaurant/<restaurant_id>/menu/<menu_id>/delete/')
def deleteMenuItem(restaurant_id, menu_id):
    return "page to delete a menu item. Task 3 complete!"

if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=5000)

