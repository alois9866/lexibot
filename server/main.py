"""This module is the main module of lexibot server."""

import argparse
import json
import hashlib

import bjoern
import psycopg2

import application

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Main script to run server")
    parser.add_argument("-cp", "--config_path", type=str,
                        help="\t.json configuration file, check README.md for an example")

    args = parser.parse_args()
    with open(args.config_path, "r") as rf:
        config = json.load(rf)

    assert "db" in config, "db parameter is not set in config file"
    for p in ["user", "password", "ip", "port"]:
        assert p in config["db"], f"{p} parameter is not set in config['db'] file"
    assert "bot_token" in config, "bot_token parameter is not set in config file"
    bot_token_hash = hashlib.sha256(config["bot_token"].encode("utf-8")).hexdigest()

    conn = psycopg2.connect(database="postgres",
                            user=config["db"]["user"],
                            password=config["db"]["password"],
                            host=config["db"]["ip"],
                            port=config["db"]["port"])
    try:
        app = application.initialize_app(conn, bot_token_hash)
        print(f'Starting server at {config["server"]["ip"]}:{config["server"]["port"]}')
        bjoern.run(app, config["server"]["ip"], int(config["server"]["port"]))
    finally:
        conn.close()
