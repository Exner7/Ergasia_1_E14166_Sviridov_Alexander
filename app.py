# Import necessary modules

from pymongo import MongoClient

from flask import Flask, jsonify, request, Response

import uuid
import time
import json



# Database interaction settings

# Connect to local mongodb
client = MongoClient( 'mongodb://localhost:27017/' )

# Select the InfoSys database
db = client[ 'InfoSys' ]

# Select the Students collection
students = db[ 'Students' ]

# Select the Users collection
users = db[ 'Users' ]



# Define dictionary and functions

# Initialize sessions-dictionary
users_sessions = {}

# Creates a new user-session
def create_session( username ):

    # generate a new user-uuid
    user_uuid = str( uuid.uuid1() )

    # insert new user-session to the sessions-dictionary
    users_sessions[ user_uuid ] = ( username, time.time() )

    return user_uuid

# Checks if user-session is valid
def is_session_valid( user_uuid ):
    return user_uuid in users_sessions



# Initialize the flask application
app = Flask( __name__ )



# API Endpoints declarations start ...



# ...................................

# [ GET ] ( endpoint ): /
#
# this route is used for test purposes
# returns the jsonified users_sessions
@app.route( '/', methods = [ 'GET' ] )
def get_sessions():
    return jsonify( users_sessions )

# ...................................



# [ POST ] ( endpoint ): /createUser
#
# Get username, password from json request data
# and create a new user
# by inserting the username and password in Users
@app.route( '/createUser', methods = [ 'POST' ] )
def create_user():

    # initialize request data object
    data = None

    try:
        # retreive the json request data
        data = json.loads( request.data )
    except Exception as e:
        # if an exception occurs while retreiving data return with an error response
        return Response( 'Bad json data.', status = 500, mimetype = 'application/json' )

    if data == None:
        # if the retreived json request data are empty return with an error response 
        return Response( 'Bad request.', status = 500, mimetype = 'application/json' )

    if 'username' not in data or 'password' not in data:
        # if username or password is not in tha json request data return with an error response
        return Response( 'Incomplete information.', status = 500, mimetype = 'application/json' )

    if users.find( { 'username': data[ 'username' ] } ).count() != 0:
        # if a user with the username given in the data already exists then return with an error response
        return Response( 'A user with the given username already exists.', status = 400, mimetype = 'application/json' )

    # insert the new user to the Users collection
    users.insert_one( { 'username': data[ 'username' ], 'password': data[ 'password' ] } )

    # return with a success response
    return Response( data[ 'username' ] + ' was added to the MongoDB', status = 200, mimetype = 'application/json' )



# ... API Endpoints declarations end



# Run the flask application
if __name__ == '__main__':
    app.run( debug = True, host = '0.0.0.0', port = 5000 )
