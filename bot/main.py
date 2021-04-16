"""This module is the main module of lexibot client, the bot."""

import argparse
import json
import logging

from bot import telegram_bot
from utils.logging import logger


def main():
    """Method to run a bot"""
    parser = argparse.ArgumentParser(description="Main script to invoke "
                                     "custom Telegram bots")
    parser.add_argument("-cp", "--config_path", type=str,
                        help="\t.json configuration file, check README.md for an example")
    parser.add_argument("-v", "--verbosity",
                        required=False, action='store_true',
                        help="\twhether to print debug messages from logger")
    args = parser.parse_args()
    with open(args.config_path, "r") as rf:
        config = json.load(rf)
    assert "bot_token" in config, "You have to provide Telegram token"
    assert "channel_id" in config,\
        "You have to provide id of Telegram channel bot needs to work with"
    assert "server" in config,\
        "You have to provide server ip address bot interacts with"
    logger.setLevel(logging.DEBUG if args.verbosity else logging.INFO)
    telegram_bot.run_channel(config=config)


if __name__ == '__main__':
    main()
