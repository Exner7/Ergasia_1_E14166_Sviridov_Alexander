# Import necessary modules

from pymongo import MongoClient

from flask import Flask, jsonify, request, Response

import uuid
import time
import json

from datetime import datetime

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



# 1. [ POST ] ( endpoint ): /createUser
#
# Get username, password from json request data
# and create a new user by inserting
# username and password in Users.
@app.route( '/createUser', methods = [ 'POST' ] )
def create_user():

    # initialize request data object
    data = None

    try:
        # retrieve the json request data
        data = json.loads( request.data )
    except Exception as e:
        # if an exception occurs while retreiving data return with an error response
        return Response( 'Bad json data.', status = 500, mimetype = 'application/json' )

    if data == None:
        # if the retrieved json request data are empty return with an error response 
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
    return Response( 'The user ' + data[ 'username' ] + ' was added to the database.', status = 200, mimetype = 'application/json' )



# 2. [ POST ] ( endpoint ): /login
#
# Get username, password from json request data
# if valid create a new session for the user
# and return with a response containing uuid.
@app.route( '/login', methods = [ 'POST' ] )
def login():

    # initialize request data object
    data = None

    try:
        # retrieve the json request data
        data = json.loads( request.data )
    except Exception as e:
        # if an exception occurs while retreiving data return with an error response
        return Response( 'Bad json data.', status = 500, mimetype = 'application/json' )

    if data == None:
        # if the retrieved json request data are empty return with an error response 
        return Response( 'Bad request.', status = 500, mimetype = 'application/json' )

    if 'username' not in data or 'password' not in data:
        # if username or password is not in tha json request data return with an error response
        return Response( 'Incomplete information.', status = 500, mimetype = 'application/json' )

    if users.find( { 'username': data[ 'username' ], 'password': data[ 'password' ] } ).count() == 0:
        # if there is no user with the provided username and password return with an error response
        return Response( 'Wrong username or password.', status = 400, mimetype = 'application/json' )

    # create a new user-session
    user_uuid = create_session( data[ 'username' ] )

    res = { 'uuid': user_uuid, 'username': data[ 'username' ] }

    # return with a success response containing the user-uuid
    return Response( json.dumps( res ), status = 200, mimetype = 'application/json' )



# 3. [ GET ] ( endpoint ): /getStudent
#
# ( Authorization required )
# Given an email in the json request data
# get student with the email from Students
@app.route( '/getStudent', methods=[ 'GET' ] )
def get_student():

    # initialize request data object
    data = None

    try:
        #retrieve the json request data
        data = json.loads( request.data )
    except Exception as e:
        # if an exception occurs while retreiving data return with an error response
        return Response( 'Bad json data.', status = 500, mimetype = 'application/json' )

    if data == None:
        # if the retrieved json request data are empty return with an error response
        return Response( 'Bad request.', status = 500, mimetype = 'application/json' )

    if 'email' not in data:
        # if username or password is not in tha json request data return with an error response
        return Response( 'Incomplete information.', status = 500, mimetype = 'application/json' )

    # retrieve the request authorization header
    user_uuid = request.headers[ 'Authorization' ]

    if not is_session_valid( user_uuid ):
        # if the user is not authorized return with an error response
        return Response( 'Unauthorized.', status = 401, mimetype = 'application/json' )

    found = students.find_one( { 'email': data[ 'email' ] } )

    if not found:
        # if no student with the provided email is found return with an error response
        return Response( 'Student not found.', status = 400, mimetype = 'application/json' )

    # construct student dictionary

    student = { 'name': found[ 'name' ], 'email': found[ 'email' ], 'yearOfBirth': found[ 'yearOfBirth' ] }

    if 'address' in found:
        student[ 'address' ] = found[ 'address' ]

    if 'courses' in found:
        student[ 'courses' ] = found[ 'courses' ]

    return Response( json.dumps( student ), status = 200, mimetype = 'application/json' )



# 4. [ GET ] ( endpoint ): /getStudents/thirties
#
# ( Authorization required )
# Respond with a list of 30 year-old students in database.
@app.route( '/getStudents/thirties', methods = [ 'GET' ] )
def get_students_thirties():

    # retrieve the request authorization header
    user_uuid = request.headers[ 'Authorization' ]

    if not is_session_valid( user_uuid ):
        # if the user is not authorized return with an error response
        return Response( 'Unauthorized.', status = 401, mimetype = 'application/json' )

    # get current year
    current_year = datetime.today().year

    # search for 30 year-old students in the database
    search_results = students.find( { 'yearOfBirth': ( current_year - 30 ) } )

    if not search_results:
        # if no 30 year-old students are found in the database return with an error response
        return Response( 'No 30 year-old students found.', status = 400, mimetype = 'application/json' )

    # initialize students list
    students_thirties = []

    # construct the students_thirties list
    for result in search_results:

        item = {
            'name': result[ 'name' ],
            'email': result[ 'email' ],
            'yearOfBirth': result[  'yearOfBirth' ]
        }

        if 'address' in result:
            item[ 'address' ] = result[ 'address' ]

        if 'courses' in result:
            item[ 'courses' ] = result[ 'courses' ]

        students_thirties.append( item )

    # return with a success response containing the students_thirties list
    return Response( json.dumps( students_thirties ), status = 200, mimetype = 'application/json' )    



# ... API Endpoints declarations end



# Run the flask application
if __name__ == '__main__':
    app.run( debug = True, host = '0.0.0.0', port = 5000 )
