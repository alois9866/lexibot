"""This module is the main module of lexibot server."""

import os
import sys

import bjoern
import psycopg2

import application

USER_VAR = 'DBUSER'
PASSWORD_VAR = 'DBPASSWORD'
DB_HOST_VAR = 'DBHOST'

HOST = '0.0.0.0'
PORT = 80

if __name__ == '__main__':
    user = os.environ.get(USER_VAR)
    if user is None:
        sys.exit(USER_VAR + ' is not set')

    password = os.environ.get(PASSWORD_VAR)
    if password is None:
        sys.exit(PASSWORD_VAR + ' is not set')

    db_host = os.environ.get(DB_HOST_VAR)
    if db_host is None:
        sys.exit(DB_HOST_VAR + ' is not set')

    conn = psycopg2.connect(database="postgres", user=user, password=password, host=db_host, port="5432")
    try:
        app = application.initialize_app(conn)
        print(f'Starting server at {HOST}:{PORT}')
        bjoern.run(app, HOST, PORT)
    finally:
        conn.close()
