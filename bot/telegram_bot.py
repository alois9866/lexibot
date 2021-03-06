"""This is a core module for Telegram bot version"""

from telegram.ext import CommandHandler, Updater

available_user_commands = ["help", "start"]


def start_reply(update, context):
    """The reply action on user's /start command"""
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text=f"Hello, my name is {context.bot.first_name}. "
                             "I am a bot. "
                             "You can type `/help` to know me better...")


def help_reply(update, context):
    """The reply action on user's /help command"""
    text = ("Info:\n"
            "You can use the following commands:\n")
    for auc in available_user_commands:
        text += f"\t`/{auc}`\n"
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text=text)


def run(bot_token):
    """Function to activate Telegram bot custom behaviour"""
    updater = Updater(token=bot_token, use_context=True)
    dispatcher = updater.dispatcher
    user_command_handlers = [
        CommandHandler('start', start_reply),
        CommandHandler('help', help_reply)
    ]
    for uch in user_command_handlers:
        dispatcher.add_handler(uch)

    updater.start_polling()
    print(f"Talk to the bot here: t.me/{updater.bot.username}\n"
          f" or inside Telegram application: @{updater.bot.username}")
    print("Press Ctrl+C to stop the bot...")
    updater.idle()


if __name__ == "__main__":
    pass
