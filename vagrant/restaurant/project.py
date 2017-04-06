
from flask import Flask, render_template, request, redirect, url_for

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
    output += "<a href ='/restaurant/1/menu/'>Restaurant 1</a>"
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

# Task 1: Create route for newMenuItem function here
@app.route('/restaurant/<int:restaurant_id>/menu/new/', methods=['GET','POST'])
def newMenuItem(restaurant_id):
    if request.method == 'POST':
        newItem = MenuItem(name = request.form['name'],restaurant_id =
            restaurant_id)
        session.add(newItem)
        session.commit()
        return redirect(url_for('restaurantMenu', restaurant_id = 
            restaurant_id))
    else:
        return render_template('newmenuitem.html', restaurant_id = 
            restaurant_id)

# Task 2: Create route for editMenuItem function here
@app.route('/restaurant/<restaurant_id>/menu/<menu_id>/edit/', methods = ['GET',
                                                                        'POST'])
def editMenuItem(restaurant_id, menu_id):
    editedItem = session.query(MenuItem).filter_by(id=menu_id).one()
    if request.method == 'POST':
        if request.form['name']:
            editedItem.name = request.form['name']
        session.add(editedItem)
        session.commit()
        return redirect(url_for('restaurantMenu',
                                restaurant_id=restaurant_id))
    else: 
        return render_template('editmenuitem.html',
                                restaurant_id=restaurant_id,
                                menu_id=menu_id,
                                i=editedItem)

# Task 3: Create a route for deleteMenuItem function here
@app.route('/restaurant/<restaurant_id>/menu/<menu_id>/delete/')
def deleteMenuItem(restaurant_id, menu_id):
    return "page to delete a menu item. Task 3 complete!"

if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=5000)

