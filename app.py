import datetime
import json
import logging
import random

from telegram import Update
from telegram.ext import CallbackContext
from telegram.ext import CommandHandler
from telegram.ext import Updater
from telegram.ext import MessageHandler, Filters
from Common.Util import get_formatted_date, get_variables
from Common.APIManagement import add_infra_data, get_infra_data as get_infra_list, get_acc_infra_data, update_infra_data, get_pending_jobs, add_pending_job, delete_pending_job, get_recurrent_jobs, start_remote_infra, stop_remote_infra, reset_remote_infra, update_job_start as update_start_job

TOKEN = '5357158986:AAFjtqG2iToqVfLOD8VIlO_pGlGjg-k7VyI'


def jobs(update: Update, context: CallbackContext):

    command_list = update.message.text.split(' --')
    main_command = command_list[0].strip().split(" ")[1]
    response = "(%s) command invalid. " % main_command


    if main_command == "new":  # /run new --job=L --duration=120 --intensity=2 --recurrent=1 --start="01-31-2022 10:02" --vm=1 --links=""
        response = add_job(command_list)
    if main_command == "update":  # /run update --job_id=12 --start_time="12:00"
        response = update_job_start(command_list)
    if main_command == "list":  # /run list --vm=1
        response = get_job_list(command_list)
    if main_command == "delete":  # /run delete --job_id=1
        response = delete_job(command_list)

    # TODO: Agregar List, se puede pensar en hacer un utilitis para enviar un texto procesado de los posts de bodzin

    context.bot.send_message(chat_id=update.effective_chat.id, text=json.dumps(response, indent=4, sort_keys=True))


def get_job_list(command_list):
    variables = get_variables(command_list)
    if "vm" in variables:
        response = get_pending_jobs(variables["vm"])
        response2 = get_recurrent_jobs(variables["vm"])
        return response["data"] + response2["data"]
    else:
        return "Missing parameters."


# /run new --job=L --duration=120 --intensity=2 --recurrent=1 --only_dm=0 --start="01-31-2022 10:02" --vm=1 --post_list=""
def add_job(command_list):
    variables = get_variables(command_list)
    if "bot_id" in variables and "vm" in variables:
        new_config = process_config(variables)
        new_job = {"infra_id": variables["vm"], "bot_id": variables["bot_id"],
                   "date_created": get_formatted_date(datetime.datetime.now()), "status": "Pending",
                   "start_time": variables["start_time"], "recurrent": variables["recurrent"], "schedule": "", "config": json.dumps(new_config)}
        response = add_pending_job([new_job])
        return response
    else:
        return "Missing parameters."


def update_job_start(command_list):
    variables = get_variables(command_list)
    if "job_id" in variables and "start_time" in variables:
        updated_job = {"start_time": variables["start_time"], "job_id": variables["job_id"]}
        response = update_start_job(updated_job)
        return response
    else:
        return "Missing parameters."

def process_config(variables):
    new_config = {"duration": variables["duration"], "intensity": variables["intensity"]}
    if "skip_count" in variables:
        new_config["skip_count"] = variables["skip_count"]
    else:
        new_config["skip_count"] = 15
    if "post_list" in variables:
        new_config["post_list"] = variables["post_list"]
    new_config["interaction_flags"] = {}
    if "only_dm" in variables:
        new_config["interaction_flags"]["only_dms"] = bool(variables["only_dm"])
    else:
        new_config["interaction_flags"]["only_dms"] = False

    if "interactions" in variables:
        new_config["interaction_flags"]["comments_on"] = ("c" in str(variables["interactions"]).lower())
        new_config["interaction_flags"]["messages_on"] = ("m" in str(variables["interactions"]).lower())
        new_config["interaction_flags"]["likes_on"] = ("l" in str(variables["interactions"]).lower())
    else:
        new_config["interaction_flags"]["messages_on"] = True
        new_config["interaction_flags"]["comments_on"] = True
        new_config["interaction_flags"]["likes_on"] = True
    if "filter_type" in variables:
        new_config["filter_type"] = variables["filter_type"]
    else:
        new_config["filter_type"] = "all"

    if "inbox_link" in variables:
        new_config["inbox_link"] = variables["inbox_link"]
    else:
        new_config["inbox_link"] = ""

    return new_config


def delete_job(command_list):
    variables = get_variables(command_list)
    if "job_id" in variables != "":
        response = delete_pending_job(variables["job_id"])
        return response
    else:
        return "Missing parameters."


def infra(update: Update, context: CallbackContext):
    if "--config=" in update.message.text:
        split = update.message.text.split("--config=")
        config = split[-1].replace("\n", "").replace("\t", "")
        command_list = split[0].split(' --')
        main_command = command_list[0].strip().split(" ")[1]
        response = config_infra(command_list, config)
    else:
        command_list = update.message.text.split(' --')
        main_command = command_list[0].strip().split(" ")[1]
        response = "(%s) command invalid. " % main_command

    if main_command == "add":  # /infra add --user=test_user --vm=1
        response = add_infra(command_list)
    if main_command == "list":  # /infra list
        response = get_infra_list()
   # if main_command == "get":  # /infra get --vm=1
   #     response = get_infra(command_list)
    if main_command == "start":  # /infra start --vm=1
        response = start_infra(command_list)
    if main_command == "stop":  # /infra stop --vm=1
        response = stop_infra(command_list)
    if main_command == "reset":  # /infra reset --vm=1
        response = reset_infra(command_list)

    context.bot.send_message(chat_id=update.effective_chat.id, text=response)


def get_infra(command_list):
    variables = get_variables(command_list)
    if "vm" in variables:
        response = get_acc_infra_data(variables["vm"])
        return response
    else:
        return "Missing parameters."


def start_infra(command_list):
    variables = get_variables(command_list)
    if "vm" in variables:
        response = start_remote_infra(variables["vm"])
        return response
    else:
        return "Missing parameters."


def stop_infra(command_list):
    variables = get_variables(command_list)
    if "vm" in variables:
        response = stop_remote_infra(variables["vm"])
        return response
    else:
        return "Missing parameters."


def reset_infra(command_list):
    variables = get_variables(command_list)
    if "vm" in variables:
        response = reset_remote_infra(variables["vm"])
        return response
    else:
        return "Missing parameters."


def add_infra(command_list):
    variables = get_variables(command_list)
    if "account_username" in variables and "vm" in variables:
        new_infra = {
            "account_username": variables["account_username"],
            "infra_id": variables["vm"],
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
    if "vm" in variables:
        infra_data = {
            "infra_id": variables["vm"],
            "config": config
        }
        response = update_infra_data(infra_data)
        return response
    else:
        return "Missing parameters."

'''
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
'''


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
    if "quien" in update.message.text.lower():
        rand = random.uniform(0, 1)
        if rand < 0.1:
            context.bot.send_message(chat_id=update.effective_chat.id, text="Dejen laburar hijos de puta")
        else:
            context.bot.send_message(chat_id=update.effective_chat.id, text="Yo")
    elif "who" in update.message.text.lower():
        rand = random.uniform(0, 1)
        if rand < 0.1:
            context.bot.send_message(chat_id=update.effective_chat.id, text="Dejen laburar hijos de puta")
        else:
            context.bot.send_message(chat_id=update.effective_chat.id, text="Me")
    else:
        context.bot.send_message(chat_id=update.effective_chat.id, text=update.message.text)
        print(update.message.reply_to_message)


def run(update: Update, context: CallbackContext):
    soon_message = 'Falta poquito, no seas ansioso %s!' % update.effective_user.first_name
    context.bot.send_message(chat_id=update.effective_chat.id, text=soon_message)


logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                     level=logging.INFO)
updater = Updater(token=TOKEN, use_context=True)
dispatcher = updater.dispatcher

infra_handler = CommandHandler('infra', infra)
dispatcher.add_handler(infra_handler)

run_handler = CommandHandler('run', jobs)
dispatcher.add_handler(run_handler)

help_handler = CommandHandler('help', help)
dispatcher.add_handler(help_handler)

echo_handler = MessageHandler(Filters.text & (~Filters.command), echo)
dispatcher.add_handler(echo_handler)

updater.start_polling()
