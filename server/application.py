"""This module contains the server itself and handlers for it's endpoints."""
import datetime
import json

import flask

import model

_app = flask.Flask(__name__)
_dbConnection = None
_bot_token_hash = None


def _initialized():
    """Returns True if all parameters of the application were set."""
    return _dbConnection and _bot_token_hash


def initialize_app(conn, bot_token_hash) -> flask.Flask:
    """Returns Flask application initialized with DB connection."""
    global _dbConnection, _bot_token_hash
    _dbConnection = conn
    _bot_token_hash = bot_token_hash
    return _app


@_app.route('/i/<int:link_id>', methods=['GET'])
def click(link_id: int):
    """Handles short-link click."""
    if not _initialized():
        return 'Not started.', 500

    full_link = model.handle_click(_dbConnection, link_id)
    return flask.redirect(full_link)


@_app.route('/create', methods=['POST'])
def create():
    """
    Creates new short-link.

    Takes JSON object as an input, which should contain chat id as 'chat_id', word as 'word' and bot token hash as 'token_hash'.

    Returns the ID of newly created link.
    """
    if not _initialized():
        return 'Not started.', 500
    if not flask.request.is_json:
        return 'Request not in JSON format', 400

    data = flask.request.get_json()
    if not data:
        return 'No valid input provided', 401

    token_hash = data.get('token_hash')
    if not token_hash:
        return 'No bot token hash provided', 401
    if token_hash != _bot_token_hash:
        return 'Incorrect bot token hash', 401

    return str(model.create(_dbConnection, data.get('chat_id'), data.get('word')))


@_app.route('/top/<string:chat_id>', methods=['GET'])
def get_top(chat_id: str):
    """
    Returns pairs of (word, number of clicks) for top 5 clicked words for chat with 'chat_id'.

    Takes optional parameter 'date'. The result will be filtered for the time period, which includes date.
    If 'date' parameter is not provided it is defaulted to current date in UTC.
    """
    if not chat_id:
        return 'No chat ID provided', 401

    date = flask.request.args.get('date')
    if not date:
        date = datetime.datetime.utcnow().date()
    else:
        date = datetime.datetime.strptime(date, '%Y-%m-%d').date()

    pairs = model.get_words_with_clicks(_dbConnection, chat_id, date)
    return json.dumps({'words': pairs}, ensure_ascii=False)


@_app.errorhandler(Exception)
def all_exception_handler(error):
    """Handles all exceptions."""
    print('ERROR', error)
    return f'Error: {error}', 500
