"""This module is the main module of lexibot client, the bot."""

import argparse
import gettext
import json
import logging
import sys
from pathlib import Path

from bot import telegram_bot
from utils.logging import configure_logger

logger = logging.getLogger('lexibot')

l10n_dir_path = Path(sys.argv[0]).parents[1] / 'l10n'
gettext.bindtextdomain('lexibot', l10n_dir_path)
gettext.install('lexibot', l10n_dir_path, names=("ngettext",))

def main():
    """Run a bot."""
    logger.info(l10n_dir_path)
    parser = argparse.ArgumentParser(description=_("Main script to invoke "
                                     "custom Telegram bots"))
    parser.add_argument('-cp', '--config_path', type=str,
                        help=_("\t.json configuration file, check README.md for an example"))
    parser.add_argument('-v', '--verbosity',
                        required=False, action='store_true',
                        help=_("\twhether to print debug messages from logger"))
    args = parser.parse_args()
    assert args.config_path, _("--config_path is not provided.")
    with open(args.config_path, 'r') as rf:
        config = json.load(rf)
    assert 'token' in config, _("You have to provide Telegram token")
    assert 'server' in config, \
        _("You have to provide server ip address bot interacts with")
    logger.setLevel(logging.DEBUG if args.verbosity else logging.INFO)
    telegram_bot.run_channel(config=config)


if __name__ == '__main__':
    configure_logger()
    main()
