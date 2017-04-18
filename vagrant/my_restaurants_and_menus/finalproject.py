from flask import   Flask,              \
                    render_template,    \
                    request,            \
                    redirect,           \
                    url_for,            \
                    flash,              \
                    jsonify             

from database_setup import Base, Restaurant, MenuItem
from sqlalchemy import  create_engine,  \
                        asc
from sqlalchemy.orm import sessionmaker

app = Flask(__name__)

engine = create_engine('sqlite:///restaurantmenu.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

## Root of website, displays list of available restaurants.
@app.route('/')
@app.route('/restaurants')
def listRestaurants():
    restaurants = session.query(Restaurant).order_by(asc(Restaurant.name))
    return render_template('restaurants.html', restaurants=restaurants)

## Lists out matching restaurant menu
@app.route('/restaurants/<int:restaurant_id>/menu/')
def showRestaurant(restaurant_id):
    restaurant = session.query(Restaurant).filter_by(id=restaurant_id).one()
    items = session.query(MenuItem).filter_by(restaurant_id=restaurant.id)
    return render_template('restaurant_menu.html',
                            restaurant=restaurant,
                            items=items)

## Edits a restaurant
@app.route('/restaurants/<int:restaurant_id>/menu/edit/', methods=['GET',
                                                                    'POST'])
def editRestaurant(restaurant_id):
    editedRestaurant = session.query(Restaurant).filter_by(id=restaurant_id).one()
    if request.method =='POST':
        if request.form['name']:
            editedRestaurant.name=request.form['name']
            session.add(editedRestaurant)
            session.commit()
            flash ("Restaurant edit saved successfully!")
        return redirect(url_for('showRestaurant',
                                restaurant_id=restaurant_id))
    else:
        return render_template('edit_restaurant.html',
                                restaurant_id=restaurant_id,
                                i=editedRestaurant)

@app.route('/restaurants/<int:restaurant_id>/delete/',methods=['GET','POST'])
def deleteRestaurant(restaurant_id):
    restaurantToDelete = session.query(Restaurant).filter_by(id=restaurant_id).one()
    if request.method == 'POST':
        session.delete(restaurantToDelete)
        session.commit()
        flash ("Restaurant deleted successfully!")
        return redirect(url_for('listRestaurants',
                                restaurant_id=restaurant_id))
    else:
        return render_template('delete_restaurant.html',
                                restaurant=restaurantToDelete)

## Task 1: Create route for newMenuItem function here
@app.route('/restaurants/<int:restaurant_id>/menu/new/', methods=['GET','POST'])
def newMenuItem(restaurant_id):
    if request.method == 'POST':
        newItem = MenuItem(name=request.form['name'],
                           description=request.form['description'],
                           price=request.form['price'],
                           restaurant_id = restaurant_id)
        session.add(newItem)
        session.commit()
        flash ("New menu item created!")
        return redirect(url_for('showRestaurant',
                                restaurant_id = restaurant_id))
    else:
        return render_template('new_menu_item.html',
                                restaurant_id = restaurant_id)

# Task 2: Create route for editMenuItem function here
@app.route('/restaurants/<restaurant_id>/menu/<menu_id>/edit/',methods = ['GET',
                                                                        'POST'])
def editMenuItem(restaurant_id, menu_id):
    editedItem = session.query(MenuItem).filter_by(id=menu_id).one()
    if request.method == 'POST':
        if request.form['name']:
            editedItem.name = request.form['name']
            editedItem.description = request.form['description']
            editedItem.price = request.form['price']
        session.add(editedItem)
        session.commit()
        flash ("Edited menu item saved!")
        return redirect(url_for('showRestaurant',
                                restaurant_id=restaurant_id))
    else: 
        return render_template('edit_menu_item.html',
                                restaurant_id=restaurant_id,
                                menu_id=menu_id,
                                i=editedItem)

# Task 3: Create a route for deleteMenuItem function here
@app.route('/restaurants/<restaurant_id>/menu/<menu_id>/delete/',methods=['GET',
                                                                        'POST'])
def deleteMenuItem(restaurant_id, menu_id):
    itemToDelete = session.query(MenuItem).filter_by(id=menu_id).one()
    if request.method == 'POST':
        session.delete(itemToDelete)
        session.commit()
        flash ("Menu item deleted successfully!")
        return redirect(url_for('showRestaurant',
                                restaurant_id=restaurant_id))
    else:
        return render_template('delete_menu_item.html',
                                item=itemToDelete,
                                restaurant_id=restaurant_id)

if __name__ == '__main__':
    #This should be a secure password, but is not for learning.
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
