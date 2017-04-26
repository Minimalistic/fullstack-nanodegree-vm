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

# Auth
from flask import session as login_session
import  random, string

# Step % GConnect
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests

CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']

engine = create_engine('sqlite:///restaurantmenu.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

@app.route('/login')
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits) \
                    for x in xrange(32))
    login_session['state'] = state
    return render_template('login.html', STATE=state)

@app.route('/gconnect', methods=['POST'])
def gconnect():
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    code = request.data
    try:
        # Update the authorization code into a credentials object
        oath_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oath_flow.redirect_uri = 'postmessage'
        credentials = oath_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(json.dumps('Failed to upgrade the \
            authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s' % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # If there was an error in the access token info, abord.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 50)
        response.headers['Content-Type'] = 'application/json'
    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user"
                ), 401)
        response.headers['Content-Type'] = ' application/json'
        return response
    # Check if user is already logged in
    stored_credentials = login_session.get('credentials')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_credentials is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps('Current user is already connected.'),
            200)
        response.headers['Content-Type'] = 'application/json'

    # Store the access token in the session for later use.
    login_session['credentials'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data["name"]
    login_session['picture'] = data["picture"]
    login_session['email'] = data["email"]

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
    flash("you are now logged in as %s" % login_session['username'])
    print "done!"
    return output

# Disconnect - Revoke a current user's token and reset their login_session.
@app.route('/gdisconnect')
def gdisconnect():
    # Only disconnect a connected user.
    credentials = login_session.get('credentials')
    access_token = credentials
    if credentials is None:
        response = make_response(json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Execute HTTP GET request to revoke token.
    url = ('https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token)
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]

    if result.status == 200:
        # Reset the user's session.
        del login_session['credentials']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']

        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response
    else:
        # For whatever reason, the given token was invalid...
        response = make_response(
            json.dumps('Failed to revoke token for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response

## Root of website, displays list of available restaurants.
@app.route('/')
@app.route('/showRestaurants')
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

## Adds a new restarant
@app.route('/restaurant/new/', methods=['GET','POST'])
def newRestaurant():
    if 'username' not in login_session:
        return redirect('/login')
    if request.method == 'POST':
        if request.form['name']:
            newRestaurant = Restaurant(name=request.form['name'])
            session.add(newRestaurant)
            session.commit()
            flash ("The new restaurant has been created!")
            return redirect(url_for('listRestaurants'))
        else:
            flash ("Restaurant name cannot be blank!")
            return render_template('new_restaurant.html' )
    else:
        return render_template('new_restaurant.html')

## Edits a restaurant
@app.route('/restaurants/<int:restaurant_id>/menu/edit/', methods=['GET',
                                                                    'POST'])
def editRestaurant(restaurant_id):
    if 'username' not in login_session:
        return redirect('/login')
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
            flash ('Restaurant name cannot be blank!')
            return render_template('edit_restaurant.html',
                                   restaurant_id=restaurant_id, 
                                   i=editedRestaurant)
    else:
        return render_template('edit_restaurant.html',
                                restaurant_id=restaurant_id,
                                i=editedRestaurant)

@app.route('/restaurants/<int:restaurant_id>/delete/',methods=['GET','POST'])
def deleteRestaurant(restaurant_id):
    if 'username' not in login_session:
        return redirect('/login')
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
    if 'username' not in login_session:
        return redirect('/login')
    if request.method == 'POST':
        if request.form['name']:
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
            flash ('Menu item cannot be blank!')
            return render_template('new_menu_item.html',
                                   restaurant_id = restaurant_id)
    else:
        return render_template('new_menu_item.html',
                                restaurant_id = restaurant_id)

# Task 2: Create route for editMenuItem function here
@app.route('/restaurants/<restaurant_id>/menu/<menu_id>/edit/',methods = ['GET',
                                                                        'POST'])
def editMenuItem(restaurant_id, menu_id):
    if 'username' not in login_session:
        return redirect('/login')
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
            flash ('Edited menu item cannot be blank!')
            return render_template('edit_menu_item.html',
                                   restaurant_id=restaurant_id,
                                   menu_id=menu_id,
                                   i=editedItem)
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
