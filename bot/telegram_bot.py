"""
This is a core module for Telegram bot version.

Adjusts bot replies to user command/messages.
"""

from telegram.ext import CommandHandler, MessageHandler, Updater,\
    CallbackContext, Filters
from telegram.update import Update
from telegram import InlineKeyboardMarkup, InlineKeyboardButton
from telegram import Bot, Message

from bot.parser import extract_japanese_words

import time
import requests
import hashlib


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
    """Function to activate Telegram bot custom behaviour in private messages

    :param bot_token: Telegram bot token
    :type bot_token: str
    :return: None
    :rtype: NoneType

    Usage::

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
    print(f"Talk to the bot here: t.me/{updater.bot.username}\n"
          f" or inside Telegram application: @{updater.bot.username}")
    print("Press Ctrl+C to stop the bot...")
    updater.idle()

def clear_bot_updates(bot: Bot) -> None:
    new_updates = bot.get_updates()
    if new_updates != []:
        new_id = new_updates[-1].update_id+1
        bot.get_updates(offset=new_id)
        print("Pending updates clear")
    else:
        print('No pending updates')

def send_word_links(bot: Bot,
                    channel_id: str,
                    message: Message,
                    server_ip: str ='0.0.0.0:80') -> None:
    text = message.text
    bot_token_hash = hashlib.sha256(bot.token.encode('utf-8')).hexdigest()
    print(f'Bot hash {bot_token_hash}')
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
        print(f"Processing word {jw}")
        word_data["word"] = jw
        resp = requests.post(url, json=word_data)
        print(f'Response', f"status: {resp.status_code}",
              f"content: {resp.text}", sep='\n\t')
        word_id = resp.json()
        word_links.append(link_generator(word_id))

    reply_markup = []
    for word,link in zip(japanese_words, word_links):
        reply_markup.append([InlineKeyboardButton(text=f"for word `{word}`", url=link)])

    bot.send_message(channel_id,
                     text='Check out word translations via the following links:',
                     reply_markup=InlineKeyboardMarkup(reply_markup))


def send_regular_report(bot: Bot,
                        channel_id: str,
                        server_ip: str ='0.0.0.0:80') -> None:
    url = f"http://{server_ip}/top/{channel_id}"
    resp = requests.get(url)
    print(f'Response', f"status: {resp.status_code}",
          f"content: {resp.text}", sep='\n\t')
    message_text = "Regular report on user clicks:\n"
    for word_link,count in resp.json()["words"]:
        word = word_link.split('/')[-1]
        message_text += f"\t link for word `{word}` has been clicked {count} times so far\n"
    bot.send_message(chat_id=channel_id, text=message_text)


def run_channel(bot_token: str, channel_id: str, server_ip: str ='0.0.0.0:80') -> None:
    bot = Bot(token=bot_token)
    update_freq = 5
    report_update_freq = 10
    last_report_timestamp = time.time()
    try:
        print(f"Starting up the {bot.username} bot custom behaviour...")
        clear_bot_updates(bot)
        while True:
            time.sleep(update_freq)
            updates = bot.get_updates()
            if time.time() - last_report_timestamp > report_update_freq:
                send_regular_report(bot, channel_id)
                last_report_timestamp = time.time()
            if updates == []:
                continue
            for upd in updates:
                message = upd.channel_post
                if message is not None:
                    # print(message.chat_id, channel_id)
                    if message.chat_id == channel_id:
                        send_word_links(bot, channel_id, message)

            # the following method clears the queue of all previous updates
            clear_bot_updates(bot)
    except KeyboardInterrupt:
        pass
    print('Finishing custom bot behaviour.')

if __name__ == "__main__":
    pass
