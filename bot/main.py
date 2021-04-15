"""This module is the main module of lexibot client, the bot."""

import argparse
import json

from bot import telegram_bot


def main():
    """Method to run a bot"""
    parser = argparse.ArgumentParser(description="Main script to invoke "
                                     "custom Telegram bots")
    parser.add_argument("-bcp", "--bot_config_path", type=str,
                        help="\t.json configuration file for the bot, example:"
                        "\t\t`config.json`")
    args = parser.parse_args()
    with open(args.bot_config_path, "r") as rf:
        config = json.load(rf)
    assert "token" in config, "You have to provide Telegram token"
    assert "channel_id" in config,\
        "You have to provide id of Telegram channel bot needs to work with"
    telegram_bot.run_channel(bot_token=config["token"],
                             channel_id=config["channel_id"])


if __name__ == '__main__':
    main()
