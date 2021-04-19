"""This module is the main module of lexibot server."""

import argparse
import hashlib
import json
import os
import sys

import bjoern
import psycopg2

import application

USER_VAR = 'DBUSER'
PASSWORD_VAR = 'DBPASSWORD'
DB_HOST_VAR = 'DBHOST'

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Main script to run server")
    parser.add_argument("-cp", "--config_path", type=str,
                        help="\t.json configuration file, check README.md for an example")

    user = os.environ.get(USER_VAR)
    if not user:
        sys.exit(USER_VAR + ' variable is not set: should contain DB user name.')

    password = os.environ.get(PASSWORD_VAR)
    if not password:
        sys.exit(PASSWORD_VAR + ' variable is not set: should contain DB user password.')

    db_host = os.environ.get(DB_HOST_VAR)
    if not db_host:
        sys.exit(DB_HOST_VAR + ' variable is not set: should contain DB host address.')

    args = parser.parse_args()
    with open(args.config_path, "r") as rf:
        config = json.load(rf)

    assert 'server' in config, '"server" parameter is not set in config file.'
    assert 'ip' in config['server'], '"server.ip" parameter is not set in config file.'
    assert 'port' in config['server'], '"server.port" parameter is not set in config file.'

    assert 'token' in config, '"token" parameter is not set in config file: should contain token of corresponding Telegram bot client.'
    bot_token_hash = hashlib.sha256(config['token'].encode('utf-8')).hexdigest()

    conn = psycopg2.connect(database='postgres',
                            user=user,
                            password=password,
                            host=db_host,
                            port='5432')
    try:
        app = application.initialize_app(conn, bot_token_hash)
        print(f'Starting server at {config["server"]["ip"]}:{config["server"]["port"]}')
        bjoern.run(app, config["server"]["ip"], int(config["server"]["port"]))
    finally:
        conn.close()
