from flask import   Flask,              \
                    render_template,    \
                    request,            \
                    redirect,           \
                    url_for,            \
                    flash,              \
                    jsonify

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

app = Flask(__name__)

engine = create_engine('sqlite:///restaurantmenu.db')

DBSession = sessionmaker(bind=engine)
session = DBSession()

#----Temporary Database

#Fake Restaurants
restaurant = {'name': 'The CRUDdy Crab', 'id': '1'}
restaurants = [{'name': 'The CRUDdy Crab', 'id': '1', 'desc': 'Come to this restaurant when you are crabby, have crabs and want to be in a building that has crabby people that also have crabs and everyone partakes in a fine dining experience that involves eating crabs and other crustateans of the sea.'},
               {'name':'Blue Burgers', 'id':'2', 'desc': 'At Blue Burgers, we pride ourself at providing only the finest cuts of Smurf in our meals. From Smurf-Wings to Smurf-Steaks, we have it all.  Coming soon, Smurf-Brain, when you just gotta be a terrible person.'},
               {'name':'Taco Hut', 'id':'3', 'desc': 'When everything is closed and you hate yourself, stuff your face at our place!'}]

#Fake Menu Items
items = [ {'name':'Cheese Pizza', 'description':'made with fresh cheese', 'price':'$5.99','course' :'Entree', 'id':'1'}, {'name':'Chocolate Cake','description':'made with Dutch Chocolate', 'price':'$3.99', 'course':'Dessert','id':'2'},{'name':'Caesar Salad', 'description':'with fresh organic vegetables','price':'$5.99', 'course':'Entree','id':'3'},{'name':'Iced Tea', 'description':'with lemon','price':'$.99', 'course':'Beverage','id':'4'},{'name':'Spinach Dip', 'description':'creamy dip with fresh spinach','price':'$1.99', 'course':'Appetizer','id':'5'} ]
item =  {'name':'Cheese Pizza','description':'made with fresh cheese','price':'$5.99','course' :'Entree'}

#----Root page of website, displays list of available restaurants.

@app.route('/')
@app.route('/restaurants')
def listRestaurants():
    return render_template('restaurants.html',
                            restaurants=restaurants,)

@app.route('/restaurants/<int:restaurant_id>/menu/')
def restaurantMenu(restaurant_id):
    restaurant = session.query(Restaurant).filter_by(id=restaurant_id).one()
    items = session.query(MenuItem).filter_by(restaurant_id=restaurant.id)
    return render_template('menu.html',
                            restaurant=restaurant,
                            items=items)

# Task 1: Create route for newMenuItem function here
@app.route('/restaurants/<int:restaurant_id>/menu/new/', methods=['GET','POST'])
def newMenuItem(restaurant_id):
    if request.method == 'POST':
        newItem = MenuItem(name = request.form['name'],
                           restaurant_id = restaurant_id)
        session.add(newItem)
        session.commit()
        flash ("New menu item created!")
        return redirect(url_for('restaurantMenu',
                                restaurant_id = restaurant_id))
    else:
        return render_template('newmenuitem.html',
                                restaurant_id = restaurant_id)

# Task 2: Create route for editMenuItem function here
@app.route('/restaurants/<restaurant_id>/menu/<menu_id>/edit/',methods = ['GET',
                                                                        'POST'])
def editMenuItem(restaurant_id, menu_id):
    editedItem = session.query(MenuItem).filter_by(id=menu_id).one()
    if request.method == 'POST':
        if request.form['name']:
            editedItem.name = request.form['name']
        session.add(editedItem)
        session.commit()
        flash ("Edited menu item saved!")
        return redirect(url_for('restaurantMenu',
                                restaurant_id=restaurant_id))
    else: 
        return render_template('editmenuitem.html',
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
        return redirect(url_for('restaurantMenu',
                                restaurant_id=restaurant_id))
    else:
        return render_template('deletemenuitem.html',
                                item=itemToDelete,
                                restaurant_id=restaurant_id)

if __name__ == '__main__':
    #This should be a secure password, but is not for learning.
    app.debug = True
    app.run(host='0.0.0.0', port=5000)

