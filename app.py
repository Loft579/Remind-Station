# -*- coding: utf-8 -*-
# Creo que funciona con 3.8
# python-telegram-bot~=13.1
# telegram~=0.0.1

import argparse
import dotenv

# Define how the command will be used in Terminal/Bash/Shell Script/Command Line
parser = argparse.ArgumentParser(description="Tengo Que Bot")
parser.add_argument('-e', '--env-file', type=str, required=True, help='The name of the environment file to load.')

# Get the arguments from command line
args = parser.parse_args()

if args.env_file:
    # Load env variables from file
    dotenv.load_dotenv(args.env_file)

from telegram.ext import Filters, MessageHandler, Updater
import logging
from random import randint
import time
from time import sleep
from customstdout import change_original_stdout
from utils import *
from constants import *
from whisperbot import openai_whisper_api
from trello import *
import traceback
from trello_do import *
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
from imageutils import ImageUtils

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

updater = None
dispatcher = None
botname = 'tengo_que_bot'


# Los seconds que se pospone el recordatorio la primera vez que se
# crea.
def get_defualt_seconds():
    return randint(HOUR * 6, HOUR * 8)

def any_message(bot, message):
    text = message.text

    is_message_from_whisper_op = message.from_user.id == 43759228 or message.from_user.id == 424819435

    # If there is an image, download it
    if message.photo != []:
        file = message.photo[-1].get_file()
        image_filename = str(message.chat.id) + '_received_image.jpg'
        file.download(image_filename)
        logging.info("Image downloaded")
    else:
        image_filename = None

    if not text and message.caption:
        text = message.caption
    
    is_text_from_msg = True
    if not text and message.voice and is_message_from_whisper_op:
        filename = f'{message.chat.id}_received_audio.ogg'
        file = bot.getFile(message.voice.file_id)
        file.download(filename)
        assert os.path.exists(filename)
        text = openai_whisper_api(local_filepath=filename)
        is_text_from_msg = False

    if not text and image_filename is not None:
        text = ImageUtils.extract_text_from_image(image_path=image_filename)
        is_text_from_msg = False
    
    if not text:
        clarify(message.chat.id, "No text in message. Please send a message with text or a voice message.")
        return

    # sub-index o sea, el X tal que /dayX, pero del mensaje enviado por el usuario
    subindex = -1

    i = 0
    temp = ''
    for c in text:
        if c == ' ':
            break
        elif c in map(str, range(10)):
            temp += c
    if temp != '':
        subindex = int(temp)

    # analiza el caso...
    if text == '/help':
        clarify(message.chat.id, HELP)
    elif text == '/hardcode':
        print("user id:", get_user_id_by_name("agusavior"))
    elif text == '/mode' or text == '/mode ':
        clarify(message.chat.id, MODOSHELP)
    elif text.startswith('/mode '):
        adj = text.split(" ")[1]
        if adj == "all":
            chats_mode[message.chat.id] = adj
            clarify(message.chat.id, "all cards will be added")
        elif adj == "off":
            chats_mode[message.chat.id] = adj
            clarify(message.chat.id, "mode off")
        elif adj.startswith("@"):
            adj = adj[1:]
            user_id = get_user_id_by_name(adj)
            if user_id != None:
                chats_mode[message.chat.id] = get_user_id_by_name(adj)
                clarify(message.chat.id, "mode settled in " + str(user_id))
            else:
                clarify(message.chat.id, "cannot get the user")
        else:
            clarify(message.chat.id, "error: unknow mode")

    elif text.startswith('/see'):
        see(message.chat.id, subindex)
    elif text.startswith('/show'):
        the_pass = refresh_pass(message.chat.id, set_last_card = subindex, get_card = subindex)
        if the_pass.card_collected != None:
            the_card = the_pass.card_collected
            clarify(message.chat.id, "name:\n" + str(the_card["name"]))
            clarify(message.chat.id, "desc:\n" + str(the_card["desc"]))
            clarify(message.chat.id, "url:\n" + str(the_card["url"]))
            clarify(message.chat.id, "labels:\n" + str(the_card["labels"]))
        else:
            if the_pass.is_last_edited == False:
                clarify(message.chat.id, "not card found, try using a valid ID.")
    elif text == '/ping':
        clarify(message.chat.id, 'pong')
    elif text == '/version':
        version = open('version', 'r')
        clarify(message.chat.id, version.read())
        version.close()
    elif text.startswith('/list'):
        refresh_pass(message.chat.id, clarify_list = True)
    elif text == '/names':
        the_pass = refresh_pass(message.chat.id, collect_names = True)
        if the_pass.names_message != "":
            clarify(message.chat.id, the_pass.names_message)
        else:
            clarify(message.chat.id, "No names to view")
    elif text == '/clean':
        chat_mode = None
        if message.chat.id in chats_mode:
            chat_mode = chats_mode[message.chat.id]
        if chat_mode != "all":
            clarify(message.chat.id, "loading...")
            refresh_pass(message.chat.id, clean = True)
            clarify(message.chat.id, "clean done")
        else:
            clarify(message.chat.id, "cannot clean because “all” mode is activated.")
    elif text == '/debug_help':
        clarify(message.chat.id, DEBUGHELP)
    elif text == '/chat_id':
        clarify(message.chat.id, str(message.chat.id))
    elif text == '/my_user_id':
        clarify(message.chat.id, str(message.from_user.id))
    elif text == '/done':
        clarify(message.chat.id, 'did you mean /done' + str(chats_last_card[message.chat.id]) + " ?")
    elif text.startswith('/done'):
        the_pass = refresh_pass(message.chat.id, done_card = subindex)
        if the_pass.is_card_done == True:
            clarify(message.chat.id, "card done")
        else:
            pass
    elif text.startswith('/add '):
        urls = text.split(" ")
        urls.pop(0)
        the_card = get_card_from_url(urls[0])
        if the_card != None:
            the_pass = refresh_pass(message.chat.id, add_cmd = the_card["id"])
            if the_pass.is_add_cmd_done == True:
                clarify(message.chat.id, "card imported")
            else:
                clarify(message.chat.id, "error in importing the card")
        else:
            clarify(message.chat.id, "cannot get the card from URL")
    elif text.startswith('/sec'):
        the_pass = refresh_pass(message.chat.id, modify_sec = subindex)
        if the_pass.sec_set != None:
            clarify(message.chat.id, "the card will be reminded in " + seg_to_str(the_pass.sec_set))
        else:
            clarify(message.chat.id, "error in changing time")
    elif text.startswith('/min'):
        the_pass = refresh_pass(message.chat.id, modify_sec = subindex*MIN)
        if the_pass.sec_set != None:
            clarify(message.chat.id, "the card will be reminded in " + seg_to_str(the_pass.sec_set))
        else:
            clarify(message.chat.id, "error in changing time")
    elif text.startswith('/day'):
        the_pass = refresh_pass(message.chat.id, modify_sec = subindex*DAY)
        if the_pass.sec_set != None:
            clarify(message.chat.id, "the card will be reminded in " + seg_to_str(the_pass.sec_set))
        else:
            clarify(message.chat.id, "error in changing time")
    elif text.startswith('/hour'):
        the_pass = refresh_pass(message.chat.id, modify_sec = subindex*HOUR)
        if the_pass.sec_set != None:
            clarify(message.chat.id, "the card will be reminded in " + seg_to_str(the_pass.sec_set))
        else:
            clarify(message.chat.id, "error in changing time")
    elif not text.startswith("/"):
        # Create a new card
        
        parts_text = ["",""]

        parts_text[0] = text

        new_card = create_card(tengoque_lists[0], parts_text[0])

        if parts_text[1] != "":
            add_to_desc(new_card, parts_text[1])
        
        if image_filename is not None:
            add_image_to_card(new_card["id"], image_filename)
        
        the_pass = refresh_pass(message.chat.id, add_cmd = new_card["id"], ignore_show_name=is_text_from_msg)
        if the_pass.is_add_cmd_done == True:
            clarify(message.chat.id, "card added")


if __name__ == '__main__':
    print('Starting...')
    change_original_stdout()

    updater = Updater(token=TELEGRAM_BOT_TOKEN)
    dispatcher = updater.dispatcher

    def any_update(update, context): #executed by Telegram with every update.
        bot = context.bot
        if update.message and update.message.text and update.message.text == '/exit' and update.message.from_user.id == ADMIN_USER_ID:
            bot.send_message(update.message.chat.id, 'bye bye')
            updater.stop()
            print('Bot killed by /exit')
            exit()
        elif update.edited_message != None:
            pass # Nothing. Ignore in edited messages.
        else:
            try:
                any_message(bot, update.message)
            except Exception as e:
                bot.send_message(update.message.chat.id, str(e))

    core_handler = MessageHandler(Filters.all, any_update, run_async=True)
    dispatcher.add_handler(core_handler)

    updater.start_polling()

    try:
        print('Press Ctrl+C to exit.')
        while True:
            try:
                refresh_pass(None)
            except Exception as e:
                print(e)
            print("chats_last_card:", chats_last_card)
            sleep(10)
    except KeyboardInterrupt:
        print('\nCtrl+C detected. Bye bye.')

    print('Waiting for update.stop()...')
    updater.stop()


