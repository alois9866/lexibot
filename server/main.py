"""This module is the main module of lexibot server."""

import argparse
import hashlib
import json
import os
import sys
from pathlib import Path
import gettext

import application

import bjoern
import psycopg2

l10n_dir_path = Path(sys.argv[0]).parents[1] / 'l10n'
gettext.bindtextdomain('lexibot', l10n_dir_path)
gettext.install('lexibot', l10n_dir_path, names=("ngettext",))


USER_VAR = 'DBUSER'
PASSWORD_VAR = 'DBPASSWORD'
DB_HOST_VAR = 'DBHOST'

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Main script to run server")
    parser.add_argument("-cp", "--config_path", type=str,
                        help="\t.json configuration file, check README.md for an example")

    user = os.environ.get(USER_VAR)
    if not user:
        sys.exit(USER_VAR + _(' variable is not set: should contain DB user name.'))

    password = os.environ.get(PASSWORD_VAR)
    if not password:
        sys.exit(PASSWORD_VAR + _(' variable is not set: should contain DB user password.'))

    db_host = os.environ.get(DB_HOST_VAR)
    if not db_host:
        sys.exit(DB_HOST_VAR + _(' variable is not set: should contain DB host address.'))

    args = parser.parse_args()
    with open(args.config_path, "r") as rf:
        config = json.load(rf)

    assert 'server' in config, _('"server" parameter is not set in config file.')
    assert 'ip' in config['server'], _('"server.ip" parameter is not set in config file.')
    assert 'port' in config['server'], _('"server.port" parameter is not set in config file.')

    assert 'token' in config, _('"token" parameter is not set in config file: should contain token of corresponding Telegram bot client.')
    bot_token_hash = hashlib.sha256(config['token'].encode('utf-8')).hexdigest()

    conn = psycopg2.connect(database='postgres',
                            user=user,
                            password=password,
                            host=db_host,
                            port='5432')
    try:
        app = application.initialize_app(conn, bot_token_hash)
        print(_('Starting server at {}:{}').format(config["server"]["ip"], config["server"]["port"]))
        bjoern.run(app, config["server"]["ip"], int(config["server"]["port"]))
    finally:
        conn.close()
