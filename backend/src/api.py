import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS
import sys

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)

cors = CORS(app, resources={r"/*": {"origins": "*"}})


@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Headers',
                         'Content-Type,Authorization,true')
    response.headers.add('Access-Control-Allow-Methods',
                         'GET,PATCH,POST,DELETE,OPTIONS')
    return response


'''
@TODO uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
'''
# db_drop_and_create_all()

# ROUTES
'''
@TODO implement endpoint
    GET /drinks
        it should be a public endpoint
        it should contain only the drink.short() data representation
    returns status code 200 and json {"success": True, "drinks": drinks}
    where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''


@app.route('/drinks', methods=["GET"])
def get_drinks():
    try:
        all_drinks = Drink.query.order_by(Drink.id).all()
        if len(all_drinks) == 0:
            abort(404)

        drinks = []
        for drink in all_drinks:
            formatted_drink = Drink.short(json.loads(str(drink)))
            drinks.append(formatted_drink)

        return jsonify({
            'success': True,
            'drinks': drinks
        })

    except Exception as e:
        print(e)

    return "Done"


'''
@TODO implement endpoint
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks}
    where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''


@app.route('/drinks-detail', methods=["GET"])
@requires_auth('get:drinks-detail')
def get_drinks_detail(jwt):
    try:
        all_drinks = Drink.query.order_by(Drink.id).all()
        if len(all_drinks) == 0:
            abort(404)

        return jsonify({
            'success': True,
            'drinks': json.loads(str(all_drinks))
        })

    except Exception as e:
        print(e)

    return "Done"


'''
@TODO implement endpoint
    POST /drinks
        it should create a new row in the drinks table
        it should require the 'post:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink}
    where drink an array containing only the newly created drink
        or appropriate status code indicating reason for failure
'''


@app.route('/drinks', methods=["POST"])
@requires_auth('post:drinks')
def create_drink(jwt):
    body = request.get_json()

    new_title = body.get('title', None)
    recipe = body.get('recipe', None)

    try:
        drink = []
        new_recipe = json.dumps(recipe)
        new_drink = Drink(id=None, title=new_title, recipe=new_recipe)
        new_drink.insert()
        new_drink.long()
        drink.append(new_drink)

        return jsonify({
            'success': True,
            'drinks': json.loads(str(drink))
        })
    except Exception as e:
        print(e)

    return "Done"


'''
@TODO implement endpoint
    PATCH /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should update the corresponding row for <id>
        it should require the 'patch:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink}
    where drink an array containing only the updated drink
        or appropriate status code indicating reason for failure
'''


@app.route('/drinks/<int:drink_id>', methods=["PATCH"])
@requires_auth('patch:drinks')
def update_drink(jwt, drink_id):
    body = request.get_json()

    updated_title = body.get('title', None)
    recipe = body.get('recipe', None)

    try:
        updated_drink = Drink.query.filter(Drink.id == drink_id).one_or_none()
        if updated_drink is None:
            abort(404)

        updated_recipe = json.dumps(recipe)
        updated_drink.title = updated_title
        updated_drink.recipe = updated_recipe
        Drink.update(updated_drink)
        Drink.long(updated_drink)
        drink = []
        drink.append(updated_drink)

        return jsonify({
            'success': True,
            'drinks': json.loads(str(drink))
        })
    except Exception as e:
        print(e)

    return "Done"


'''
@TODO implement endpoint
    DELETE /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should delete the corresponding row for <id>
        it should require the 'delete:drinks' permission
    returns status code 200 and json {"success": True, "delete": id}
    where id is the id of the deleted record
        or appropriate status code indicating reason for failure
'''


@app.route('/drinks/<int:drink_id>', methods=["DELETE"])
@requires_auth('delete:drinks')
def delete_drink(jwt, drink_id):
    try:
        deleted_drink = Drink.query.filter(Drink.id == drink_id).one_or_none()
        if deleted_drink is None:
            abort(404)

        Drink.delete(deleted_drink)

        return jsonify({
            'success': True,
            'delete': drink_id
        })
    except Exception as e:
        print(e)

    return "Done"


# Error Handling
'''
Example error handling for unprocessable entity
'''


@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "unprocessable"
    }), 422


'''
@TODO implement error handlers using the @app.errorhandler(error) decorator
    each error handler should return (with approprate messages):
             jsonify({
                    "success": False, 
                    "error": 404,
                    "message": "resource not found"
                    }), 404

'''

'''
@TODO implement error handler for 404
error handler should conform to general task above
'''


@app.errorhandler(404)
def resource_not_found(error):
    return jsonify({
        "success": False,
        "error": 404,
        "message": "resource not found"
    }), 404


'''
@TODO implement error handler for AuthError
error handler should conform to general task above
'''


@app.errorhandler(AuthError)
def handle_auth_error(ex):
    response = jsonify(ex.error)
    response.status_code = ex.status_code
    return response
