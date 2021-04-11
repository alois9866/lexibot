"""
This is a core module for Telegram bot version.

Adjusts bot replies to user command/messages.
"""
import logging

from telegram.ext import CommandHandler, MessageHandler, Updater,\
    CallbackContext, Filters
from telegram.update import Update

from bot.parser import extract_japanese_words

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                     level=logging.INFO)

available_user_commands = ["help", "start", "echo"]


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
    for auc in available_user_commands:
        text += f"\t`/{auc}`\n"
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text=text)


def echo_reply(update: Update, _: CallbackContext) -> None:
    """Echo user message"""
    text = update.message.text
    answer = ' '.join(text.split(' ')[1:])
    update.message.reply_text(answer)


def reply_japanese(update: Update, _: CallbackContext) -> None:
    """Echo only japanese words"""
    if update.message is not None:
        text = update.message.text
        answer = f'Japanese words: {extract_japanese_words(text)}'
        update.message.reply_text(answer)


def run(bot_token):
    """Function to activate Telegram bot custom behaviour

    :param bot_token: Telegram bot token
    :type bot_token: str
    :return: None
    :rtype: NoneType

    Usage::

        >>> from bot import telegram_bot
        >>> token = "<your_token>"
        >>> telegram_bot.run(token)
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


if __name__ == "__main__":
    pass
