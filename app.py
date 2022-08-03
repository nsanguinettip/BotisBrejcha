import datetime
import json
import logging
import random
#import prettytable as pt
from telegram.ext import CallbackQueryHandler
from telegram.ext import CallbackContext
from telegram.ext import CommandHandler
from telegram.ext import Updater
from telegram.ext import MessageHandler, Filters
from Common.Util import get_formatted_date, get_variables
from Common.APIManagement import add_infra_data, get_infra_data as get_infra_list, get_acc_infra_data, update_infra_data, get_pending_jobs, add_pending_job, delete_pending_job, get_recurrent_jobs, start_remote_infra, stop_remote_infra, reset_remote_infra, update_job_start as update_start_job, update_infra_interactions, get_infra_interactions as get_interactions, get_contacts as get_contacts_report, get_interaction_by_user as get_interactions_user, get_manual_profiles, update_validated_profiles, add_blacklist
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update, ParseMode


#TOKEN = '5357158986:AAFjtqG2iToqVfLOD8VIlO_pGlGjg-k7VyI'
TOKEN = '5482457484:AAHKczj_u8T21ft_jBX-x6Q3e9yZtZ4xjGk'

COMMANDS = []


def jobs(update: Update, context: CallbackContext):
    command_list = COMMANDS
    #command_list = update.message.text.split(' --')
    main_command = command_list[0].strip().split(",")[0]
    response = "(%s) command invalid. " % main_command
    if main_command == "new":  # /run new --job=L --duration=120 --intensity=2 --recurrent=1 --start="01-31-2022 10:02" --vm=1 --links=""
        response = add_job(command_list, str(update.effective_user.id))
    if main_command == "update":  # /run update --job_id=12 --start_time="12:00"
        response = update_job_start(command_list)
    if main_command == "list":  # /run list --vm=1
        response = get_job_list(command_list)
    if main_command == "delete":  # /run delete --job_id=1
        response = delete_job(command_list)

    # TODO: Agregar List, se puede pensar en hacer un utilitis para enviar un texto procesado de los posts de bodzin

    context.bot.send_message(chat_id=update.effective_chat.id, text=response)


# /run list --vm=1
def get_job_list(command_list):
    #recorrer los jobs
    variables = get_variables(command_list)
    if "vm" in variables:
        response = get_pending_jobs(variables["vm"])
        response2 = get_recurrent_jobs(variables["vm"])

        return response["data"] + response2["data"]
    else:
        return "Missing parameters."


# /run new --job=L --duration=120 --intensity=2 --recurrent=1 --start="01-31-2022 10:02" --vm=1 --post_list=""
def add_job(command_list, author_telegram_id):
    response_text = ""
    variables = get_variables(command_list)
    if "bot_id" in variables and "vm" in variables:
        new_config = process_config(variables)
        new_job = {"infra_id": variables["vm"], "bot_id": variables["bot_id"],
                   "date_created": get_formatted_date(datetime.datetime.now()), "status": "Pending",
                   "start_time": variables["start_time"], "recurrent": variables["recurrent"], "schedule": "",
                   "config": json.dumps(new_config), "last_status": get_formatted_date(datetime.datetime.now()),
                   "elapsed": 0, "author_telegram_id": author_telegram_id}
        response = add_pending_job([new_job])
        if response["code"] == 200:
            response_text = "Trabajo agregado."
        else:
            response_text = "Error, no se pudo agregar el trabajo"
    else:
        response_text = "Parametros faltantes."
    return response_text


def update_job_start(command_list):
    response_text = ""
    variables = get_variables(command_list)
    if "job_id" in variables and "start_time" in variables:
        updated_job = {"start_time": variables["start_time"], "job_id": variables["job_id"]}
        response = update_start_job(updated_job)
        if response["code"] == 200:
            response_text = "Trabajo %s actualizado" % variables["job_id"]
        else:
            response_text = "Error, no se pudo actualizar"
    else:
        response_text = "Parametros faltantes."
    return response_text


def process_config(variables):
    new_config = {"duration": variables["duration"], "intensity": variables["intensity"]}
    if "skip_count" in variables:
        new_config["skip_count"] = variables["skip_count"]
    else:
        new_config["skip_count"] = 15
    if "post_list" in variables:
        new_config["post_list"] = variables["post_list"]
    new_config["interaction_flags"] = {}

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
    response_text = ""
    variables = get_variables(command_list)
    if "job_id" in variables != "":
        response = delete_pending_job(variables["job_id"])
        if response["code"] == 200:
            response_text = "Trabajo eliminado"
        else:
            response_text = "Error, no se pudo eliminar"
    else:
        response_text = "Missing parameters."
    return response_text


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
    if main_command == "interaction":  # /infra interaction --vm=1 --interactions=''
        response = update_interactions(command_list)
    #if main_command == "contacts":  # /infra contacts --vm=1
    #    response = get_contacts_infra(command_list)

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
        print(response)
        if response["code"] == 200:
            response_text = "VM %s reiniciada" % variables["vm"]
        else:

            response_text = "Error, no se pudo reiniciar"
        return response_text
    else:
        return "Parametros faltantes"


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


def get_infra_interactions(command_list):
    variables = get_variables(command_list)
    if "vm" in variables:
        response = get_interactions(variables["vm"])
        return response
    else:
        return "Missing parameters."


def get_interaction_user(command_list):
    variables = get_variables(command_list)
    if "vm" in variables:
        response = get_interactions_user(variables["vm"])
        return response
    else:
        return "Missing parameters."


'''def get_contacts_infra(update: Update, command_list):
    variables = get_variables(command_list)
    for variables() in variables:

        table = pt.PrettyTable(['DMs', 'Com', 'Fol', 'Likes', 'Total'])
        data = [
            (203, 133, 'ABC', 203, 626),
            (783, 333, 'ABC', 285, 126),
            (235, 192, 'ABC', 205, 126),
            (985, 292, 'ABC', 205, 216),
        ]
        for DMs, Com, Fol, Likes, Total in data:
            table.add_row([f'{DMs:.0f}', f'{Com:.0f}', Fol, f'{Likes:.0f}', f'{Total:.0f}'])

        update.message.reply_text(f'<pre>{table}</pre>', parse_mode=ParseMode.HTML)
'''


def update_interactions(command_list):
    variables = get_variables(command_list)
    if "vm" in variables and "interactions" in variables:
        interactions_hour, interactions_day = eval(variables["interactions"])
        interactions = {"day": {"dms": interactions_day[0], "comments": interactions_day[1],
                                "likes": interactions_day[2], "follows": interactions_day[3]},
                        "hour": {"dms": interactions_hour[0], "comments": interactions_hour[1],
                                 "likes": interactions_hour[2], "follows": interactions_hour[3]}
         }
        infra_data = {
            "infra_id": variables["vm"],
            "interactions_credit": str(interactions).replace("'", '"')
        }
        response = update_infra_interactions(infra_data)
        if response["code"] == 200:
            response_text = "Interaccion actualizada."
        else:
            response_text = "Error, no se pudo agregar la interaccion"
        return response_text
    else:
        return "Parametros faltantes"


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
    if "?" in update.message.text.lower():
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


def validator_files(update: Update, context: CallbackContext):
    profile_count = 10
    profile_list = get_manual_profiles(profile_count)
    for profile in profile_list:
        url = 'https://twitter.com/%s' % profile["username"]
        validate_button = [
                [InlineKeyboardButton("👍", callback_data="like"),
                 InlineKeyboardButton("👎", callback_data="dislike")],
        ]
        reply_markup = InlineKeyboardMarkup(validate_button)
        context.bot.send_message(chat_id=update.effective_chat.id, text=url, reply_markup=reply_markup)


def validate_button(update, context):
    twitter_profile = update.callback_query.message["text"]
    username = twitter_profile.strip().split(".com/")[1]
    querydata = update.callback_query
    if querydata.data == "like":
        profile = {
            'username': username,
            'validated': True
        }
        update_validated_profiles([profile])
    else:
        profile = {
            'username': username
        }
        add_blacklist([profile])
    context.bot.send_message(chat_id=querydata.message.chat_id,
                             text="Diste %s a %s." % (querydata.data, username))


def test(update, context):
    update.message.reply_text(main_menu_message(),
                              reply_markup=main_menu_keyboard())


async def main_menu(update, context):
    query = update.callback_query
    query.answer()
    query.edit_message_text(
                    text=main_menu_message(),
                    reply_markup=main_menu_keyboard())


def run_menu(update, context):
    query = update.callback_query
    query.answer()
    query.edit_message_text(
                        text=run_menu_message(),
                        reply_markup=run_menu_keyboard())
    COMMANDS.append(query.data)


def schedule_menu(update, context):
    query = update.callback_query
    query.answer()
    query.edit_message_text(
                        text=schedule_menu_message(),
                        reply_markup=schedule_menu_keyboard())
    recurrent = "recurrent=1"
    COMMANDS.append(recurrent)


def admin_menu(update, context):
    query = update.callback_query
    query.answer()
    query.edit_message_text(
                        text=admin_menu_message(),
                        reply_markup=admin_menu_keyboard())


def vm_menu(update, context):
    query = update.callback_query
    query.answer()
    query.edit_message_text(
                        text=vm_menu_message(),
                        reply_markup=vm_menu_keyboard())
    COMMANDS.append(query.data)


def duration_menu(update, context):
    query = update.callback_query
    query.answer()
    query.edit_message_text(
                    text=duration_menu_message(),
                    reply_markup=duration_menu_keyboard())
    COMMANDS.append(query.data)


def start_hour_menu(update, context):
    query = update.callback_query
    query.answer()
    query.edit_message_text(
                    text=start_hour_menu_message(),
                    reply_markup=start_hour_menu_keyboard())
    COMMANDS.append(query.data)


def start_min_menu(update, context):
    query = update.callback_query
    query.answer()
    query.edit_message_text(
                    text=start_min_menu_message(),
                    reply_markup=start_min_menu_keyboard())
    COMMANDS.append(query.data)


def confirmation_menu(update, context):
    query = update.callback_query
    query.answer()
    query.edit_message_text(
                    text=confirmation_menu_message(),
                    reply_markup=confirmation_menu_keyboard())
    if "recurrent=1" in COMMANDS:
        COMMANDS.append(query.data)
        COMMANDS.append("intensity=1")
        start_time = "00:00"
        COMMANDS.append(start_time)
        print(COMMANDS)
    else:
        # command_list = update.message.text.split(' --')
        # main_command = command_list[0].strip().split(",")[0]
        COMMANDS.append(query.data)
        COMMANDS.append("recurrent=0")
        COMMANDS.append("intensity=1")
        print(COMMANDS)
    jobs(update, context)



# and so on for every callback_data option
def first_submenu(bot, update):
  pass

# /run new --job=L --duration=120 --intensity=2 --recurrent=1 --start="01-31-2022 10:02" --vm=1 --post_list=""
############################ Keyboards #########################################
def main_menu_keyboard():
    keyboard = [[InlineKeyboardButton('Run', callback_data='new')],
                [InlineKeyboardButton('Schedule', callback_data='recurrent')],
                [InlineKeyboardButton('Admin', callback_data='admin')]]
    return InlineKeyboardMarkup(keyboard)


def run_menu_keyboard():
    keyboard = [[InlineKeyboardButton('L', callback_data='job=L')],
                [InlineKeyboardButton('SB', callback_data='job=SB')]]
    return InlineKeyboardMarkup(keyboard)


def schedule_menu_keyboard():
    keyboard = [[InlineKeyboardButton('Add', callback_data='new')],
                [InlineKeyboardButton('List', callback_data='m2_2')],
                [InlineKeyboardButton('Update', callback_data='main')]]
    return InlineKeyboardMarkup(keyboard)


def admin_menu_keyboard():
    keyboard = [[InlineKeyboardButton('Infra', callback_data='m1')],
                [InlineKeyboardButton('Reportes', callback_data='m2_2')]]
    return InlineKeyboardMarkup(keyboard)


def vm_menu_keyboard():
    keyboard = ([[InlineKeyboardButton('1', callback_data='vm=1'),
                 InlineKeyboardButton('2', callback_data='vm=2'),
                InlineKeyboardButton('3', callback_data='vm=3'),
                InlineKeyboardButton('4', callback_data='vm=4')],
                [InlineKeyboardButton('5', callback_data='vm=5'),
                InlineKeyboardButton('6', callback_data='vm=6'),
                InlineKeyboardButton('7', callback_data='vm=7'),
                InlineKeyboardButton('8', callback_data='vm=8')],
                [InlineKeyboardButton('9', callback_data='vm=9'),
                InlineKeyboardButton('10', callback_data='vm=10'),
                InlineKeyboardButton('11', callback_data='vm=11'),
                InlineKeyboardButton('12', callback_data='vm=12')],
                [InlineKeyboardButton('13', callback_data='vm=13'),
                InlineKeyboardButton('14', callback_data='vm=14'),
                InlineKeyboardButton('15', callback_data='vm=15'),
                InlineKeyboardButton('16', callback_data='vm=16')],
                 ]
                )
    return InlineKeyboardMarkup(keyboard)


def duration_menu_keyboard():
    keyboard = [[InlineKeyboardButton('30 mins', callback_data='duration=30'),
                InlineKeyboardButton('60 mins', callback_data='duration=60'),
                InlineKeyboardButton('90 mins', callback_data='duration=90')],
                [InlineKeyboardButton('120 mins', callback_data='duration=120'),
                InlineKeyboardButton('180 mins', callback_data='duration=180'),
                InlineKeyboardButton('240 mins', callback_data='duration=240')],
                [InlineKeyboardButton('300 mins', callback_data='duration=300')]]
    return InlineKeyboardMarkup(keyboard)


def start_hour_menu_keyboard():
    keyboard = ([[InlineKeyboardButton('1', callback_data='hour=01'),
                 InlineKeyboardButton('2', callback_data='hour=02'),
                 InlineKeyboardButton('3', callback_data='hour=03'),
                 InlineKeyboardButton('4', callback_data='hour=04'),
                 InlineKeyboardButton('5', callback_data='hour=05'),
                 InlineKeyboardButton('6', callback_data='hour=06')],
                 [InlineKeyboardButton('7', callback_data='hour=07'),
                 InlineKeyboardButton('8', callback_data='hour=08'),
                 InlineKeyboardButton('9', callback_data='hour=09'),
                 InlineKeyboardButton('10', callback_data='hour=10'),
                 InlineKeyboardButton('11', callback_data='hour=11'),
                 InlineKeyboardButton('12', callback_data='hour=00')],
                 ]
                )
    return InlineKeyboardMarkup(keyboard)


def start_min_menu_keyboard():
    keyboard = ([[InlineKeyboardButton('00', callback_data='min=00'),
                 InlineKeyboardButton('05', callback_data='min=05'),
                 InlineKeyboardButton('10', callback_data='min=10'),
                 InlineKeyboardButton('15', callback_data='min=15'),
                 InlineKeyboardButton('20', callback_data='min=20'),
                 InlineKeyboardButton('25', callback_data='min=25')],
                 [InlineKeyboardButton('30', callback_data='min=30'),
                 InlineKeyboardButton('35', callback_data='min=35'),
                 InlineKeyboardButton('40', callback_data='min=40'),
                 InlineKeyboardButton('45', callback_data='min=45'),
                 InlineKeyboardButton('50', callback_data='min=50'),
                 InlineKeyboardButton('55', callback_data='min=55')],
                 ]
                )
    return InlineKeyboardMarkup(keyboard)


def confirmation_menu_keyboard():
    keyboard = [[InlineKeyboardButton('SI', callback_data='confirmation=si'),
                InlineKeyboardButton('NO', callback_data='confirmation=no'),
                 ]]
    return InlineKeyboardMarkup(keyboard)


############################# Messages #########################################


def main_menu_message():
    return 'Choose the option in main menu:'


def run_menu_message():
    return 'Select job:'


def schedule_menu_message():
    return 'Select one option:'


def admin_menu_message():
    return 'Select one option:'


def duration_menu_message():
    return 'Select duration:'


def vm_menu_message():
    return 'Select one vm:'


def start_hour_menu_message():
    return 'Select start hour:'


def start_min_menu_message():
    return 'Select start min:'


def confirmation_menu_message():
    return 'Confirma los datos ingresados? %s:' % COMMANDS

############################# Handlers #########################################


logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
updater = Updater(token=TOKEN, use_context=True)
dispatcher = updater.dispatcher

infra_handler = CommandHandler('infra', infra)
dispatcher.add_handler(infra_handler)

run_handler = CommandHandler('run', jobs)
dispatcher.add_handler(run_handler)

help_handler = CommandHandler('help', help)
dispatcher.add_handler(help_handler)

'''get_contacts_infra = CommandHandler('contacts', get_contacts_infra)
dispatcher.add_handler(get_contacts_infra)'''

test_handler = CommandHandler('test', test)
dispatcher.add_handler(test_handler)

echo_handler = MessageHandler(Filters.text & (~Filters.command), echo)
dispatcher.add_handler(echo_handler)

validator_files = CommandHandler("validate", validator_files)
dispatcher.add_handler(validator_files)

validate_button_handler = CallbackQueryHandler(validate_button)
dispatcher.add_handler(validate_button_handler)

updater.dispatcher.add_handler(CallbackQueryHandler(main_menu, pattern='main'))
updater.dispatcher.add_handler(CallbackQueryHandler(vm_menu, pattern='new'))
updater.dispatcher.add_handler(CallbackQueryHandler(schedule_menu, pattern='recurrent'))
updater.dispatcher.add_handler(CallbackQueryHandler(admin_menu, pattern='admin'))
updater.dispatcher.add_handler(CallbackQueryHandler(first_submenu, pattern='m1_1'))
updater.dispatcher.add_handler(CallbackQueryHandler(duration_menu, pattern='job=L'))
updater.dispatcher.add_handler(CallbackQueryHandler(duration_menu, pattern='job=SB'))
updater.dispatcher.add_handler(CallbackQueryHandler(run_menu, pattern='vm='))
if "recurrent=1" in COMMANDS:
    print(COMMANDS)
    updater.dispatcher.add_handler(CallbackQueryHandler(start_hour_menu, pattern='duration'))
    updater.dispatcher.add_handler(CallbackQueryHandler(start_min_menu, pattern='hour'))
    updater.dispatcher.add_handler(CallbackQueryHandler(confirmation_menu, pattern='min'))
else:
    updater.dispatcher.add_handler(CallbackQueryHandler(confirmation_menu, pattern='duration'))



#updater.dispatcher.add_handler(CallbackQueryHandler(callback_contains_check, text_contains='SI'))

updater.start_polling()
