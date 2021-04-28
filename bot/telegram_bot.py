"""
This is a core module for Telegram bot version.

Adjusts bot replies to user command/messages.
"""
import hashlib
import time
from typing import Dict, Union

import requests
from telegram import Bot, Message
from telegram import InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import CommandHandler, MessageHandler, Updater, \
    CallbackContext, Filters
from telegram.update import Update

from bot.parser import extract_japanese_words
from utils.logging import logger

private_message_commands = ["help", "start", "echo"]


def start_reply(update: Update, context: CallbackContext) -> None:
    """The reply action on user's /start command"""
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text=f"Hello, my name is {context.bot.first_name}. "
                                  "I am a bot. "
                                  "You can type `/help` to know me better...")


def help_reply(update: Update, context: CallbackContext) -> None:
    """The reply action on user's /help command"""
    text = ("Info:\n"
            "You can use the following commands:\n")
    for auc in private_message_commands:
        text += f"\t`/{auc}`\n"
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text=text)


def echo_reply(update: Update, _: CallbackContext) -> None:
    """Echo user message"""
    text = update.message.text
    answer = ' '.join(text.split(' ')[1:])
    update.message.reply_text(answer)
    update.message.reply_text('Check this link:',
                              reply_markup=InlineKeyboardMarkup([
                                  [InlineKeyboardButton(text='link', url='https://yandex.ru')]
                              ]))


def reply_japanese(update: Update, _: CallbackContext) -> None:
    """Echo only japanese words"""
    if update.message is not None:
        text = update.message.text
        answer = f'Japanese words: {extract_japanese_words(text)}'
        update.message.reply_text(answer)


def run_pm(bot_token: str) -> None:
    """
    Function to activate Telegram bot custom behaviour in private messages.
    It is considered as test function to verify whether telegram responds properly.

    :param bot_token: Telegram bot token
    :type bot_token: str
    :return: None

    Usage:
        >>> from bot import telegram_bot
        >>> token = "<your_token>"
        >>> telegram_bot.run_pm(token)
        2021-04-11 13:27:50,212 - apscheduler.scheduler - INFO - Scheduler started
        Talk to the bot here: t.me/<name_of_the_bot_corresponding_to_the_token>
         or inside Telegram application: @<name_of_the_bot_corresponding_to_the_token>
        Press Ctrl+C to stop the bot...
    """
    updater = Updater(token=bot_token, use_context=True)
    dispatcher = updater.dispatcher
    user_command_handlers = [
        CommandHandler('start', start_reply),
        CommandHandler('help', help_reply),
        CommandHandler("echo", echo_reply),
    ]
    for uch in user_command_handlers:
        dispatcher.add_handler(uch)

    user_message_handlers = [MessageHandler(Filters.text, reply_japanese)]
    for umh in user_message_handlers:
        dispatcher.add_handler(umh)

    updater.start_polling()
    logger.info("Talk to the bot here: t.me/{name}\n"
                " or inside Telegram application: @{name}".format(name=updater.bot.username))
    logger.info("Press Ctrl+C to stop the bot...")
    updater.idle()


def clear_bot_updates(bot: Bot) -> None:
    """Clear pending updates from Telegram"""
    new_updates = bot.get_updates()
    if new_updates != []:
        new_id = new_updates[-1].update_id + 1
        bot.get_updates(offset=new_id)
        logger.debug("Pending updates cleared")
    else:
        logger.debug('No pending updates')


def send_word_links(bot: Bot,
                    channel_id: str,
                    message: Message,
                    server_ip: str = '0.0.0.0:80') -> None:
    """
    Reply to channel message by providing links to online dictionary
    For every unique japanese word link is generated and sent to chat

    :param bot: telegeram.Bot instance created via unique Telegram bot token
    :param channel_id: `id` field to initialize telegram.Chat instance.
        For private channels telegram.Chat can only be obtained by calling
        telegram.User.get_chat(id=<id>) or telegram.Bot.get_chat(id=<id>)
        for the users/bots - participants of the channel
    :param message: telegram.Message instance which represents message in telegram channel
    :param server_ip: server ip address + port. Bot will communicate with server using this info.
    """
    text = message.text
    bot_token_hash = hashlib.sha256(bot.token.encode('utf-8')).hexdigest()
    logger.debug('Bot hash {0}'.format(bot_token_hash))
    japanese_words = extract_japanese_words(text)
    if japanese_words == []:
        return
    word_data = {
        "chat_id": channel_id,
        "word": None,
        "token_hash": bot_token_hash
    }
    url = f"http://{server_ip}/create"
    word_links = []
    link_generator = lambda id: f"http://{server_ip}/i/{id}"
    for jw in japanese_words:
        logger.debug("Processing word {}".format(jw))
        word_data["word"] = jw
        resp = requests.post(url, json=word_data)
        logger.debug("\n\t".join(['Response', "status: {}".format(resp.status_code),
                                  "content: {}".format(resp.text)]))
        # TODO: Will crash if server returns error.
        word_id = resp.json()
        assert isinstance(word_id, int)
        word_links.append(link_generator(word_id))

    reply_markup = []
    for word, link in zip(japanese_words, word_links):
        reply_markup.append([InlineKeyboardButton(text=word, url=link)])

    bot.send_message(channel_id,
                     text='Check out word translations:',
                     reply_markup=InlineKeyboardMarkup(reply_markup))


def send_regular_report(bot: Bot,
                        channel_id: str,
                        server_ip: str = '0.0.0.0:80') -> None:
    """Send regular report about user clicks on word links

    :param bot: telegeram.Bot instance created via unique Telegram bot token
    :param channel_id: `id` field to initialize telegram.Chat instance.
        For private channels telegram.Chat can only be obtained by calling
        telegram.User.get_chat(id=<id>) or telegram.Bot.get_chat(id=<id>)
        for the users/bots - participants of the channel
    :param server_ip: server ip address + port. Bot will communicate with server using this info.
    """

    url = f"http://{server_ip}/top/{channel_id}"
    resp = requests.get(url)
    logger.debug("\n\t".join(['Response', "status: {}".format(resp.status_code),
                              "content: {}".format(resp.text)]))
    word_info = resp.json()["words"]
    if len(word_info) != 0:
        message_text = "Most popular words:\n"
        for word_link, count in resp.json()["words"]:
            word = word_link.split('/')[-1]
            message_text += f"\t- `{word}` was clicked {count} times this week.\n"
        bot.send_message(chat_id=channel_id, text=message_text)


def run_channel(config: Dict[str, Union[str, Dict[str, str]]]) -> None:
    """Function to activate Telegram bot custom behaviour in a channel
    It runs endless while cycle, to terminate - press Ctrl+C

    :param config: dictionary with parameters related to server and bot client
    For details check README.md file in repo root
    :return: None

    Usage:
        >>> import json
        >>> from bot import telegram_bot
        >>> with open('./utils/my_config.json', 'r') as rf:
        ...     config = json.load(rf)
        ...
        >>> import logging
        >>> logging.getLogger('lexibot').setLevel(logging.DEBUG) # or logging.INFO
        >>> telegram_bot.run_channel(config)
        telegram_bot.py:198 Starting up the <bot_username> bot custom behaviour...
        telegram_bot.py:108 No pending updates
        ...
        ^Ctelegram_bot.py:219 Finishing custom bot behaviour.
    """
    bot = Bot(token=config["token"])
    registered_chats = {}

    update_freq = 5  # sec
    report_update_freq = 120  # 1 week

    last_report_timestamp = time.time()
    server_ip_port = f'{config["server"]["ip"]}:{config["server"]["port"]}'
    try:
        logger.info("Starting up the {0} bot custom behaviour...".format(bot.username))
        clear_bot_updates(bot)
        while True:
            try:
                time.sleep(update_freq)

                if time.time() - last_report_timestamp > report_update_freq:
                    for chat in registered_chats:
                        send_regular_report(bot, chat, server_ip_port)
                        last_report_timestamp = time.time()

                updates = bot.get_updates()
                if not updates:
                    continue
                for upd in updates:
                    message = upd.channel_post
                    if message is not None:
                        chat_id = message.chat_id
                        if not registered_chats.get(chat_id):
                            registered_chats[chat_id] = True
                        logger.debug([chat_id, message.text])
                        send_word_links(bot, chat_id, message, server_ip_port)

                clear_bot_updates(bot)
            except KeyboardInterrupt:
                raise
            except Exception as e:
                logger.error(e)
                clear_bot_updates(bot)
    except KeyboardInterrupt:
        pass
    logger.info('Finishing custom bot behaviour.')


if __name__ == "__main__":
    pass
