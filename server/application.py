"""This package contains the server itself and handlers for it's endpoints."""
import json

import flask

import model

_app = flask.Flask(__name__)
_dbConnection = None


def initialize_app(conn) -> flask.Flask:
    """Returns Flask application initialized with DB connection"""
    global _dbConnection
    _dbConnection = conn
    return _app


@_app.route('/i/<int:link_id>', methods=['GET'])
def click(link_id: int):
    """Handles short link click"""
    if _dbConnection is None:
        return 'Not started.', 500

    full_link = model.handle_click(_dbConnection, link_id)
    return flask.redirect(full_link)


@_app.route('/create', methods=['POST'])
def create():
    """Creates new link. Takes JSON object as an input, which should contain chat id as 'chat_id', word as 'word' and bot token as 'token'."""
    if _dbConnection is None:
        return 'Not started.', 500

    if not flask.request.is_json():
        return 'Request not in JSON format', 400

    data = json.loads(flask.request.get_json())[0]
    token = data.get('token')
    if token is None or len(token) == 0:
        return 'No bot token', 401

    if not model.bot_registered(_dbConnection, token):
        return 'Incorrect bot token', 401

    full_link = model.create(_dbConnection, data.get('chat_id'), data.get('word'))
    return flask.redirect(full_link)


@_app.errorhandler(Exception)
def all_exception_handler(error):
    """Handles all exceptions"""
    return f'Error: {error}.', 500
