"""This module is the main module of lexibot client, the bot."""

import argparse
import json

from bot import telegram_bot


def main():
    """Method to run a bot"""
    parser = argparse.ArgumentParser(description="Main script to invoke "
                                     "custom bots")
    parser.add_argument("-bcp", "--bot_config_path", type=str,
                        help="\t.json configuration file for the bot, example:"
                        "\t\t`config.json`")
    args = parser.parse_args()
    with open(args.bot_config_path, "r") as rf:
        config = json.load(rf)
    bot_type = config["bot_type"]
    if bot_type == "telegram":
        assert "token" in config["telegram"], ("For `telegram` bot type you"
                                               "have to provide Telegram token")
        telegram_bot.run(config["telegram"]["token"])
    else:
        pass


if __name__ == '__main__':
    main()
