import datetime
import logging
from telegram import Update
from telegram.ext import CallbackContext
from telegram.ext import CommandHandler
from telegram.ext import Updater
from telegram.ext import MessageHandler, Filters
from telegram import InlineQueryResultArticle, InputTextMessageContent
from Common.Util import get_formatted_date, get_variables
from Common.APIManagement import add_infra_data, get_infra_data as get_infra_list, get_acc_infra_data, update_infra_data

TOKEN = '5357158986:AAFjtqG2iToqVfLOD8VIlO_pGlGjg-k7VyI'


def infra(update: Update, context: CallbackContext):
    if "--config=" in update.message.text:
        split = update.message.text.split("--config=")
        config = split[-1].replace("\n", "").replace("\t", "")
        command_list = split[0].split(' ')[1:]
        main_command = command_list[0]
        response = config_infra(command_list, config)
    else:
        command_list = update.message.text.split(' ')[1:]
        main_command = command_list[0]
        response = "(%s) command invalid. " % main_command

    if main_command == "add":  # /infra add --user=test_user --vm=1
        response = add_infra(command_list)
    if main_command == "list":  # /infra list
        response = get_infra_list()
    if main_command == "get":  # /infra get --user=test_test
        response = get_infra(command_list)

    context.bot.send_message(chat_id=update.effective_chat.id, text=response)


def get_infra(command_list):
    variables = get_variables(command_list)
    if variables["account_username"] != "":
        response = get_acc_infra_data(variables["account_username"])
        return response
    else:
        return "Missing parameters."


def add_infra(command_list):
    variables = get_variables(command_list)
    if variables["account_username"] != "" and variables["vm"] != "":
        new_infra = {
            "account_username": variables["account_username"],
            "vm": variables["vm"],
            "status": "Unknown",
            "last_update": get_formatted_date(datetime.datetime.now()),
            "config": ""
        }
        response = add_infra_data(new_infra)
        return response
    else:
        return "Missing parameters."


def config_infra(command_list, config):
    variables = get_variables(command_list)
    if variables["vm"] != "":
        infra_data = {
            "vm": variables["vm"],
            "config": config
        }
        response = update_infra_data(infra_data)
        return response
    else:
        return "Missing parameters."


def inline_caps(update: Update, context: CallbackContext):
    query = update.inline_query.query
    if not query:
        return
    results = [InlineQueryResultArticle(
        id=query.upper(),
        title='Caps',
        input_message_content=InputTextMessageContent(query.upper())
    )]
    context.bot.answer_inline_query(update.inline_query.id, results)


def help(update: Update, context: CallbackContext):
    help_message = '''Hey, %s! How are you?
Im @BotisBrejchaBot. Here are some commands you can try: 
    /help   -           This Message
    /hey    -           Welcome Message
    /schedule -         Schedule Config 
    /run -              Run Specific Configuration
    ''' % update.effective_user.first_name
    context.bot.send_message(chat_id=update.effective_chat.id, text=help_message)


def echo(update: Update, context: CallbackContext):
    context.bot.send_message(chat_id=update.effective_chat.id, text=update.message.text)


def run(update: Update, context: CallbackContext):
    soon_message = 'Falta poquito, no seas ansioso %s!' % update.effective_user.first_name
    context.bot.send_message(chat_id=update.effective_chat.id, text=soon_message)


def schedule(update: Update, context: CallbackContext):
    soon_message = 'Falta poquito, no seas ansioso %s!' % update.effective_user.first_name
    print(update.message.text)
    print(update.message.from_user.username)
    context.bot.send_message(chat_id=update.effective_chat.id, text=soon_message)


logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                     level=logging.INFO)
updater = Updater(token=TOKEN, use_context=True)
dispatcher = updater.dispatcher

infra_handler = CommandHandler('infra', infra)
dispatcher.add_handler(infra_handler)

run_handler = CommandHandler('run', run)
dispatcher.add_handler(run_handler)

help_handler = CommandHandler('help', help)
dispatcher.add_handler(help_handler)

echo_handler = MessageHandler(Filters.text & (~Filters.command), echo)
dispatcher.add_handler(echo_handler)

updater.start_polling()
