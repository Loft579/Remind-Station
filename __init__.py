# -*- coding: utf-8 -*-
# Creo que funciona con 3.8
# python-telegram-bot~=13.1
# telegram~=0.0.1

from telegram.ext import Filters, MessageHandler, Updater
import logging
from random import randint
import time
from time import sleep
from customstdout import change_original_stdout
from utils import *
from constants import *
from trello import *
import traceback
from trello_do import *
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

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
    if True:
        text = message.text or ''

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
            chats_mode[message.chat.id] = adj
        elif text.startswith('/show_plus'):
            the_pass = refresh_pass(message.chat.id, set_last_card = subindex, get_card = subindex)
            if the_pass.card_collected != None:
                clarify(message.chat.id, str(the_pass.card_collected["name"]))
                cmds_msg = "reminder duration: " + seg_to_str(int(the_pass.code_collected[3])) + ". time left: " + seg_to_str((int(the_pass.code_collected[2]) + int(the_pass.code_collected[3])) - int(time.time())) + "\n/done" + str(chats_last_card[message.chat.id]) + " /sec" + str(int(int(the_pass.code_collected[3]) / 2)) + " /hour2 " + "/hour6 " + "/hour12 " + "/day1 " + "/day2 " + "/day4"
                clarify(message.chat.id, cmds_msg)
            else:
                if the_pass.is_last_edited == False:
                    clarify(message.chat.id, "not card found, try using a valid ID.")
        elif text.startswith('/show'):
            the_pass = refresh_pass(message.chat.id, set_last_card = subindex, get_card = subindex)
            if the_pass.card_collected != None:
                clarify(message.chat.id, str(the_pass.card_collected["name"]))
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
            pass #Trello mod
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
            
            if "\n" in text[:NAME_LIMIT]:
                parts_text = text.split('\n', 1)
            else:
                parts_text = [text[:NAME_LIMIT], text[NAME_LIMIT:]]

            new_card = create_card(tengoque_lists[0], parts_text[0])

            if parts_text[1] != "":
                add_to_desc(new_card, parts_text[1])
            
            if message.photo != []:
                file = message.photo[-1].get_file()
                file.download(str(message.chat.id) + '_received_image.jpg') #mod
                logging.info("Image downloaded")
                add_image_to_card(new_card["id"], str(message.chat.id) + '_received_image.jpg')
            
            the_pass = refresh_pass(message.chat.id, add_cmd = new_card["id"])
            if the_pass.is_add_cmd_done == True:
                clarify(message.chat.id, new_card['url'] + " added")
    #except Exception as e:
        #traceback.print_exc()


if __name__ == '__main__':
    print('Starting...')

    change_original_stdout()

    updater = Updater(token=TOKEN)
    dispatcher = updater.dispatcher
    

    def any_update(update, context): #lo ejecuta Telegram en cada update.
        bot = context.bot
        if update.message and update.message.text and update.message.text == '/exit' and update.message.from_user.id == ADMIN_USER_ID:
            bot.send_message(update.message.chat.id, 'bye bye')
            updater.stop()
            print('Bot killed by /exit')
            exit()
        elif update.edited_message != None:
            pass # Nothing. Ignore in edited messages.
        elif update.message is not None:
            any_message(bot, update.message)
        else:
            any_message(bot, None)

    refresh_pass(None, first_pass = True)

    #dispatcher.add_handler(MessageHandler(Filters.photo, image_handler))
    core_handler = MessageHandler(Filters.all, any_update, run_async=True)
    dispatcher.add_handler(core_handler)
    
    
    updater.start_polling()

    try:
        print('Press Ctrl+C to exit.')
        while True:
            sleep(10)
            refresh_pass(None)
            print("---")
            print(chats_last_card)
    except KeyboardInterrupt:
        print('\nCtrl+C detected. Bye bye.')

    print('Waiting for update.stop()...')
    updater.stop()


