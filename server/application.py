"""This package contains the server inself and handlers for it's endpoints."""
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
def index(link_id: int):
    """Handles short link click"""
    if _dbConnection is None:
        return 'Not started.', 500
    full_link = model.handle_click(_dbConnection, link_id)
    return flask.redirect(full_link)


@_app.errorhandler(Exception)
def all_exception_handler(error):
    """Handles all exceptions"""
    return f'Error: {error}.', 500
