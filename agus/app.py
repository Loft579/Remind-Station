# -*- coding: utf-8 -*-
# Creo que funciona con 3.8
# python-telegram-bot~=13.1
# telegram~=0.0.1

from telegram.ext import Filters, MessageHandler, Updater
import logging
from random import randint
import time
from time import sleep
from utils import *
from constants import *
from agus.trello import get_all_cards, get_one_card, create_card
import traceback
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
from pseudotags import set_seconds_to_card

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
        text = message.text or message.caption or ''

        # sub-index o sea, el X tal que /dayX, pero del mensaje enviado por el usuario
        subindex = -1

        # Get the number of the command
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
            # TODO
            raise NotImplementedError('TODO')
        elif text == '/ping':
            bot.send_message(message.chat.id, 'Pong')
        elif text.startswith('/see'):
            # TODO
            raise NotImplementedError('TODO')
        elif text == '/version':
            # TODO
            raise NotImplementedError('TODO')
        elif text == '/names':
            cards = get_all_cards()
            names = ''
            for card in cards:
                names += card['name']
            bot.send_message(message.chat.id, names)
        elif text == '/chat_id':
            bot.send_message(message.chat.id, str(message.chat.id))
        elif text == '/my_user_id':
            bot.send_message(message.chat.id, str(message.from_user.id))
        elif text.startswith('/done'):
            # TODO
            raise NotImplementedError('TODO')
        elif text.startswith('/sec'):
            modify_sec = subindex
            card = get_one_card(card_id=last_card_id)
            set_seconds_to_card(card=card, seconds=modify_sec)
        elif not text.startswith("/"):
            new_card = create_card()
            
            if message.photo != []:
                file = message.photo[-1].get_file()
                filename = str(message.chat.id) + '_received_image.jpg'
                file.download(filename)
                logging.info("Image downloaded")
                add_image_to_card(new_card["id"], filename)
            
            the_pass = refresh_pass(message.chat.id, add_cmd = new_card["id"])
            if the_pass.is_add_cmd_done == True:
                clarify(message.chat.id, new_card['url'] + " added")


def main():
    print('Starting...')

    updater = Updater(token=TELEGRAM_BOT_TOKEN)
    dispatcher = updater.dispatcher

    def any_update(update, context): #executed by Telegram with every update.
        bot = context.bot
        any_message(bot, update.message)

    core_handler = MessageHandler(Filters.all, any_update, run_async=True)
    assert dispatcher is not None
    dispatcher.add_handler(core_handler)
    
    updater.start_polling()

    try:
        print('Press Ctrl+C to exit.')
        while True:
            try:
                ... # TODO
            except Exception as e:
                traceback.print_exc()
            sleep(10)
    except KeyboardInterrupt:
        print('\nCtrl+C detected. Bye bye.')

    print('Waiting for update.stop()...')
    updater.stop()
