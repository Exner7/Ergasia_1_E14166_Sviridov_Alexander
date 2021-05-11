# Import necessary modules.

from pymongo import MongoClient

from flask import Flask, jsonify, request, Response

import uuid  # For generating a user_uuid.
import time  # Used in session generation.
import json

# For retreiving current year.
from datetime import datetime



# Database interaction settings

# Connect to local mongodb.
client = MongoClient( 'mongodb://localhost:27017/' )

# Select the InfoSys database.
db = client[ 'InfoSys' ]

# Select the Students collection.
students = db[ 'Students' ]

# Select the Users collection.
users = db[ 'Users' ]



# Define dictionary and functions ...

# Initialize sessions-dictionary.
users_sessions = {}

# Creates a new user-session.
def create_session( username ):

    # generate a new user-uuid
    user_uuid = str( uuid.uuid1() )

    # insert new user-session to the sessions-dictionary
    users_sessions[ user_uuid ] = ( username, time.time() )

    return user_uuid

# Checks if user-session is valid.
def is_session_valid( user_uuid ):
    return user_uuid in users_sessions



# Initialize the flask application.
app = Flask( __name__ )



# API Endpoints declarations start ...



# 1. [ POST ] ( endpoint ): /createUser
#
# Get username, password from json request data
# and create a new user by inserting
# username and password in Users.
@app.route( '/createUser', methods = [ 'POST' ] )
def create_user():

    data = None  # Initialize data.

    try:
        # Retrieve the json request data.
        data = json.loads( request.data )
    except Exception:
        return Response(
                'Bad json data.',
                status = 500,
                mimetype = 'application/json' )

    if data == None:
        return Response(
                'Bad request.',
                status = 500,
                mimetype = 'application/json' )

    if 'username' not in data or 'password' not in data:
        return Response(
                'Incomplete information.',
                status = 500,
                mimetype = 'application/json' )

    if users.find( { 'username': data[ 'username' ] } ).count() != 0:
        # If a user with the username exists,
        # then return with an error response.
        return Response(
                'A user with the given username already exists.',
                status = 400,
                mimetype = 'application/json' )

    # Insert new user to the users collection.
    users.insert_one( {
                'username': data[ 'username' ],
                'password': data[ 'password' ]
            } )

    # Return with a success response.
    return Response(
            'The user ' + data[ 'username' ] + ' was added to the database.',
            status = 200,
            mimetype = 'application/json' )



# 2. [ POST ] ( endpoint ): /login
#
# Get username, password from json request data
# if valid create a new session for the user,
# and return with a response containing uuid.
@app.route( '/login', methods = [ 'POST' ] )
def login():

    data = None  # Initialize data.

    try:
        # Retrieve the json request data.
        data = json.loads( request.data )
    except Exception:
        return Response(
                'Bad json data.',
                status = 500,
                mimetype = 'application/json' )

    if data == None:
        return Response(
                'Bad request.',
                status = 500,
                mimetype = 'application/json' )

    if 'username' not in data or 'password' not in data:
        return Response(
                'Incomplete information.',
                status = 500,
                mimetype = 'application/json' )

    if users.find( {
                'username': data[ 'username' ],
                'password': data[ 'password' ]
            } ).count() == 0:
        # If username and password do not
        # correspond to an existing user,
        # return with an error response.
        return Response(
                'Wrong username or password.',
                status = 400,
                mimetype = 'application/json' )

    # Create a new session for the user.
    user_uuid = create_session( data[ 'username' ] )

    # Construct response message using the uuid and username.
    res = { 'uuid': user_uuid, 'username': data[ 'username' ] }

    # Return with success response
    # containing the above message.
    return Response(
            json.dumps( res ),
            status = 200,
            mimetype = 'application/json' )



# 3. [ GET ] ( endpoint ): /getStudent
#
# ( Authorization required )
# Given an email in the json request data
# get student with the email from Students
@app.route( '/getStudent', methods=[ 'GET' ] )
def get_student():

    user_uuid = None  # Initialize uuid.

    try:
        # Retrieve the request Authorization header.
        user_uuid = request.headers[ 'Authorization' ]
    except Exception:
        # If an exception occurs while
        # retreiving the Authorization header,
        # return with an error response.
        return Response(
                'Authorization Key Error',
                status = 500,
                mimetype = 'application/json' )

    if not is_session_valid( user_uuid ):
        # If the user is not authorized,
        # return with an error response.
        return Response(
                'Unauthorized.',
                status = 401,
                mimetype = 'application/json' )

    data = None  # Initialize data.

    try:
        # Retrieve the json request data.
        data = json.loads( request.data )
    except Exception:
        return Response(
                'Bad json data.',
                status = 500,
                mimetype = 'application/json' )

    if data == None:
        return Response(
                'Bad request.',
                status = 500,
                mimetype = 'application/json' )

    if 'email' not in data:
        return Response(
                'Incomplete information.',
                status = 500,
                mimetype = 'application/json' )

    found = students.find_one( { 'email': data[ 'email' ] } )

    if not found:
        # If no student with the provided email is found,
        # return with an error response.
        return Response(
                'Student not found.',
                status = 400,
                mimetype = 'application/json' )

    # Construct the student dictionary.

    student = {}  # Initialize student.

    for key in found.keys():

        # Skip '_id' key.
        if key == '_id':
            continue

        student[ key ] = found[ key ]

    # Return with a success response
    # containing the student dictionary.
    return Response(
            json.dumps( student ),
            status = 200,
            mimetype = 'application/json' )



# 4. [ GET ] ( endpoint ): /getStudents/thirties
#
# ( Authorization required )
# Respond with a list of 30 year-old students in database.
@app.route( '/getStudents/thirties', methods = [ 'GET' ] )
def get_students_thirties():

    user_uuid = None  # Initialize uuid.

    try:
        # Retrieve the request Authorization header.
        user_uuid = request.headers[ 'Authorization' ]
    except Exception:
        # If an exception occurs while
        # retreiving the Authorization header,
        # return with an error response.
        return Response(
                'Authorization Key Error',
                status = 500,
                mimetype = 'application/json' )

    if not is_session_valid( user_uuid ):
        # If the user is not authorized,
        # return with an error response.
        return Response(
                'Unauthorized.',
                status = 401,
                mimetype = 'application/json' )

    # Get the current year.
    current_year = datetime.today().year

    # Find the students that are 30 years-old.
    results = students.find( { 'yearOfBirth': ( current_year - 30 ) } )

    if results.count() == 0:
        # If no students that are 30 years-old are found,
        # return with an error response.
        return Response(
                'No students that are 30 years-old found.',
                status = 400,
                mimetype = 'application/json' )

    # Construct the students list.

    students_thirties = []

    for result in results:

        # Construct student dictionary.

        student = {}

        for key in result.keys():

            # Skip '_id' key.
            if key == '_id':
                continue

            student[ key ] = result[ key ]

        students_thirties.append( student )

    # Return with a success response
    # containing the students list.
    return Response(
            json.dumps( students_thirties ),
            status = 200,
            mimetype = 'application/json' )



# 5. [ GET ] ( endpoint ): /getStudents/oldies
#
# ( Authorization required )
# Respond with a list of students that are at least 30 years-old.
@app.route( '/getStudents/oldies', methods = [ 'GET' ] )
def get_students_oldies():

    user_uuid = None  # Initialize uuid.

    try:
        # Retrieve the request Authorization header.
        user_uuid = request.headers[ 'Authorization' ]
    except Exception:
        # If an exception occurs while
        # retreiving the Authorization header,
        # return with an error response.
        return Response(
                'Authorization Key Error',
                status = 500,
                mimetype = 'application/json' )

    if not is_session_valid( user_uuid ):
        # If the user is not authorized,
        # return with an error response.
        return Response(
                'Unauthorized.',
                status = 401,
                mimetype = 'application/json' )

    # Get the current year.
    current_year = datetime.today().year

    # Search for the students that are at least 30 years-old.
    results = students.find( {
                'yearOfBirth': { '$lte': ( current_year - 30 ) }
            } )

    if results.count() == 0:
        # If no students that are at least 30 years-old are found,
        # return with an error response
        return Response(
                "No students that are at least 30 years-old found.",
                status = 500,
                mimetype = "application/json" )

    # Construct the students list.

    students_oldies = []

    for result in results:

        # Construct student dictionary.

        student = {}

        for key in result.keys():

            # Skip '_id' key.
            if key == '_id':
                continue

            student[ key ] = result[ key ]

        students_oldies.append( student )

    # Return with a success response
    # containing the students list.
    return Response(
            json.dumps( students_oldies ),
            status = 200,
            mimetype = 'application/json' )



# 6. [ GET ] ( endpoint ): /getStudentAddress
#
# ( Authorization required )
# Find a student that has an address by a given email.
@app.route( '/getStudentAddress', methods=[ 'GET' ] )
def get_student_address():

    user_uuid = None  # Initialize uuid.

    try:
        # Retrieve the request Authorization header.
        user_uuid = request.headers[ 'Authorization' ]
    except Exception:
        # If an exception occurs while
        # retreiving the Authorization header,
        # return with an error response.
        return Response(
                'Authorization Key Error',
                status = 500,
                mimetype = 'application/json' )

    if not is_session_valid( user_uuid ):
        # If the user is not authorized,
        # return with an error response.
        return Response(
                'Unauthorized.',
                status = 401,
                mimetype = 'application/json' )

    data = None  # Initialize data.

    try:
        # Retrieve the json request data.
        data = json.loads( request.data )
    except Exception:
        return Response(
                'Bad json data.',
                status = 500,
                mimetype = 'application/json' )

    if data == None:
        return Response(
                'Bad request.',
                status = 500,
                mimetype = 'application/json' )

    if 'email' not in data:
        return Response(
                'Incomplete information.',
                status = 500,
                mimetype = 'application/json' )

    # Search database for the student with the provided email.
    found = students.find_one( { 'email': data[ 'email' ] } )

    if not found:
        # If no student with the provided email is found,
        # return with an error response.
        return Response(
                'Student not found.',
                status = 400,
                mimetype = 'application/json' )

    if 'address' not in found:
        # If the student found has no address,
        # return with an error response.
        return Response(
                'The student with the email '
                        + data[ 'email' ]
                        + ' has no address.',
                status = 400,
                mimetype = 'application/json' )

    # Construct the student dictionary.

    street = found[ 'address' ][ 0 ][ 'street' ]

    postcode = found[ 'address' ][ 0 ][ 'postcode' ]

    student = {
        'name': found[ 'name' ],
        'street': street,
        'postcode': postcode
    }

    # Return with a success response,
    # containing the student's address information.
    return Response(
            json.dumps( student ),
            status = 200,
            mimetype = 'application/json' )



# 7. [ DELETE ] ( endpoint ): /deleteStudent
#
# ( Authorization required )
# Given an email in the json request data delete
# student with the given email from the database.
@app.route( '/deleteStudent', methods=[ 'DELETE' ] )
def delete_student():

    user_uuid = None  # Initialize uuid.

    try:
        # Retrieve the request Authorization header.
        user_uuid = request.headers[ 'Authorization' ]
    except Exception:
        # If an exception occurs while
        # retreiving the Authorization header,
        # return with an error response.
        return Response(
                'Authorization Key Error',
                status = 500,
                mimetype = 'application/json' )

    if not is_session_valid( user_uuid ):
        # If the user is not authorized,
        # return with an error response.
        return Response(
                'Unauthorized.',
                status = 401,
                mimetype = 'application/json' )

    data = None  # Initialize data.

    try:
        # Retrieve the json request data.
        data = json.loads( request.data )
    except Exception:
        return Response(
                'Bad json data.',
                status = 500,
                mimetype = 'application/json' )

    if data == None:
        return Response(
                'Bad request.',
                status = 500,
                mimetype = 'application/json' )

    if 'email' not in data:
        return Response(
                'Incomplete information.',
                status = 500,
                mimetype = 'application/json' )

    if students.delete_one( { 'email': data['email'] } ).deleted_count == 0:
        # If the student with the given email is not deleted,
        # return with an error response.
        return Response(
                'Student not found.',
                status = 400,
                mimetype = 'application/json' )

    # Return with a success response.
    return Response(
            'Student deleted successfully.',
            status = 200,
            mimetype = 'application/json' )



# 8. [ PATCH ] ( endpoint ): /addCourses
#
# ( Authorization required )
# Add a list of courses to a student with
# the email provided in json request data.
@app.route( '/addCourses', methods = [ 'PATCH' ] )
def add_courses():

    user_uuid = None  # Initialize uuid.

    try:
        # Retrieve the request Authorization header.
        user_uuid = request.headers[ 'Authorization' ]
    except Exception:
        # If an exception occurs while
        # retreiving the Authorization header,
        # return with an error response.
        return Response(
                'Authorization Key Error',
                status = 500,
                mimetype = 'application/json' )

    if not is_session_valid( user_uuid ):
        # If the user is not authorized,
        # return with an error response
        return Response(
                'Unauthorized.',
                status = 401,
                mimetype = 'application/json' )

    data = None  # Initialize data.

    try:
        # Retrieve the json request data.
        data = json.loads( request.data )
    except Exception:
        return Response(
                'Bad json data.',
                status = 500,
                mimetype = 'application/json' )

    if data == None:
        return Response(
                'Bad request.',
                status = 500,
                mimetype = 'application/json' )

    if 'email' not in data or 'courses' not in data:
        return Response(
                'Incomplete information.',
                status = 500,
                mimetype = 'application/json' )

    if not isinstance( data[ 'courses' ], list ):
        # If courses is not a list,
        # return with an error response.
        return Response(
                'courses should be a list.',
                status = 500,
                mimetype = 'application/json' )

    for item in data[ 'courses' ]:
        if ( not isinstance( item, dict ) or
                len( item ) != 1 or
                    not isinstance( list( item.values() )[ 0 ], int ) ):
            # If any item in the courses list
            # is not a one-key dictionary with an integer value,
            # then return with an error response
            return Response(
                    'courses should only contain '
                            + 'one-key integer-value dictionaries.',
                    status = 500,
                    mimetype = 'application/json' )

    # Add the courses list to the student matching the given email.
    if students.update_one(
            { 'email': data[ 'email' ] },
            { '$set': { 'courses': data[ 'courses' ] } } ).matched_count == 0:
        # If no student matched the provided email,
        # return with an error response.
        return Response(
                'Student not found.',
                status = 400,
                mimetype = 'application/json' )

    # Return with a success response.
    return Response(
            'Student updated successfully.',
            status = 200,
            mimetype = 'application/json' )



# 9. [ GET ] ( endpoint ): /getPassedCourses
#
# ( Authorization required )
# Return a list of passed courses of
# the student with the provided email.
@app.route( '/getPassedCourses', methods = [ 'GET' ] )
def get_passed_courses():

    # Authorization validation ...

    user_uuid = None

    try:
        # retrieve the request authorization header
        user_uuid = request.headers[ 'Authorization' ]
    except Exception:
        # If an exception occurs while
        # retreiving the Authorization header,
        # return with an error response.
        return Response(
                'Authorization Key Error',
                status = 500,
                mimetype = 'application/json' )

    if not is_session_valid( user_uuid ):
        # If the user is not authorized,
        # return with an error response.
        return Response(
                'Unauthorized.',
                status = 401,
                mimetype = 'application/json' )

    # Data validation ...

    data = None  # Initialize data

    try:
        # retrieve the json request data
        data = json.loads( request.data )
    except Exception:
        return Response(
                'Bad json data.',
                status = 500,
                mimetype = 'application/json' )

    if data == None:
        return Response(
                'Bad request.',
                status = 500,
                mimetype = 'application/json' )

    if 'email' not in data:
        return Response(
                'Incomplete information.',
                status = 500,
                mimetype = 'application/json' )

    # Student search ...

    # Search database for the student with the provided email.
    found = students.find_one( { 'email': data[ 'email' ] } )

    if not found:
        # If no student with the provided email is found,
        # return with an error response.
        return Response(
                'Student not found.',
                status = 400,
                mimetype = 'application/json' )

    # Courses check ...

    if 'courses' not in found:
        # If the student found has no courses,
        # return with an error response.
        return Response(
                'The student with the email '
                        + data[ 'email' ]
                        + ' has no courses.',
                status = 400,
                mimetype = 'application/json' )

    # Filter passed courses ...

    passed_courses = []

    for course in found[ 'courses' ]:
        if 5 <= list( course.values() )[ 0 ]:
            passed_courses.append( course )

    if len( passed_courses ) == 0:
        # If the student has no passed courses,
        # return with an error response.
        return Response(
                'The student with the email '
                        + data[ 'email' ]
                        + ' has no passed courses.',
                status = 400,
                mimetype = 'application/json' )

    # Construct output ...

    student = { 'name': found[ 'name' ], 'passed courses': passed_courses }

    # Return with a success response
    # containing the student and passed courses.
    return Response(
            json.dumps( student ),
            status = 200,
            mimetype = 'application/json' )



# ... API Endpoints declarations end



# Run the flask application
if __name__ == '__main__':
    app.run( debug = True, host = '0.0.0.0', port = 5000 )
