# Import necessary modules

from pymongo import MongoClient

from flask import Flask, jsonify

import uuid
import time



# Database interaction settings

# Connect to local mongodb
client = MongoClient( 'mongodb://localhost:27017/' )

# Select the InfoSys database
db = client[ 'InfoSys' ]

# Select the Students collection
students = db[ 'Students' ]

# Select the Users collection
users = db[ 'Users' ]



# Define helper objects

# Initialize sessions-dictionary
users_sessions = {}

# Creates a new user session
def create_session( username ):

    # generate a new user-uuid
    user_uuid = str( uuid.uuid1() )

    # insert new user session to the sessions-dictionary
    users_sessions[ user_uuid ] = ( username, time.time() )

    return user_uuid

# Checks if user session is valid
def is_session_valid( user_uuid ):
    return user_uuid in users_sessions



# Initialize the flask application
app = Flask( __name__ )



# API Endpoints declarations start ...
#
# ...................................
@app.route( '/', methods = [ 'GET' ] )
def test():
    return jsonify( students.find( {} ).count() )
# ...................................
#
# ... API Endpoints declarations end



# Run the flask application
if __name__ == '__main__':
    app.run( debug = True, host = '0.0.0.0', port = 5000 )
