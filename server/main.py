"""This module is the main module of lexibot server."""

import os
import sys

import psycopg2

USER_VAR = 'DBUSER'
PASSWORD_VAR = 'DBPASSWORD'
HOST_VAR = 'DBHOST'

if __name__ == '__main__':
    user = os.environ.get(USER_VAR)
    if user is None:
        sys.exit(USER_VAR + ' is not set')

    password = os.environ.get(PASSWORD_VAR)
    if password is None:
        sys.exit(PASSWORD_VAR + ' is not set')

    host = os.environ.get(HOST_VAR)
    if host is None:
        sys.exit(HOST_VAR + ' is not set')

    conn = psycopg2.connect(database="postgres", user=user, password=password, host=host, port="5432")

    # TODO

    conn.close()
