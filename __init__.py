# -*- coding: utf-8 -*-
# Creo que funciona con 3.8
# python-telegram-bot~=13.1
# telegram~=0.0.1

from telegram.ext import Filters, MessageHandler, Updater
import logging
from random import randint
from time import sleep
from chats import *
from customstdout import change_original_stdout
from recordatorios import *
from utils import *
from constants import *

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

updater = None
dispatcher = None
botname = 'tengo_que_bot'


def each_day():
    global each_day_timer

    # Guardado Diario.
    save()

    # Vuelve a ejecutar esta funcion luego de 1 day.
    each_day_timer = Timer(DAY / PROB_DE_APAGADO, each_day)
    each_day_timer.start()


each_day_timer = Timer(DAY / PROB_DE_APAGADO, each_day)


# Los seconds que se pospone el recordatorio la primera vez que se
# crea.
def get_defualt_seconds():
    return randint(HOUR * 6, HOUR * 8)


def perform_next(chat):
    sooner = None
    for r in chat.recordatorios:
        if r.seg == -1:
            continue

        if sooner == None or (sooner.how_much_left() > r.how_much_left()):
            sooner = r

    if sooner != None:
        chat.clarify_edit_r(sooner)
    else:
        chat.clarify('No active reminders.', True)


def any_message(bot, message):
    try:
        text = message.text or '[reminder with no text]'

        # Primero se fija si debe ignorar el comando y de paso crea el comando mas limpio
        if '@' in text:
            if text[text.index('@') + 1:] != botname:
                return
            text = text[:text.index('@')]

        # agarra el chat (si no existe lo crea):
        if message.chat.id not in chats:
            chats[message.chat.id] = Chat(message.chat)
        chat = chats[message.chat.id]

        # sub-index o sea, el X tal que /dayX
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
            subindex_r = chat.rec_from_uid(subindex)
        else:
            subindex_r = chat.actual_r

        # analiza el caso...
        if text == '/start':
            if message.chat.type == 'private':
                chat.clarify(PRIVATEWELCOME, True)
            else:
                chat.clarify(GROUPWELCOME, True)
        elif text == '/help':
            chat.clarify(HELP, True)
        elif text == '/mode' and subindex == -1:
            chat.clarify(MODOSHELP, True)
        elif text.startswith('/mode'):
            adj = subindex
            chat.setadj(adj, adj not in chat.adjectives)
            if adj in chat.adjectives:
                chat.clarify('Actived. /mode{} to disable it.'.format(adj), True)
            else:
                chat.clarify('Disabled. /mode{} to activate.'.format(adj), True)
        elif text == '/ping':
            chat.clarify('pong', True)
        elif text.startswith('/list'):
            textinfo = chat.info(text[6:])
            chat.lastinfomessage = chat.clarify(textinfo, siosi=True)
        elif text == '/next':
            perform_next(chat)
        elif text == '/clean':
            new = []
            for r in chat.recordatorios:
                if r.seg != -1:
                    new.append(r)
            chat.recordatorios = new

            chat.update_lastinfomessage()
        elif text == '/debughelp' and message.chat.id == ADMIN_CHAT_ID:
            chat.clarify(DEBUGHELP, True)
        elif text == '/save':
            save()
            chat.clarify('Save it.')
        elif text == '/proxbigchange': # TODO: Delete this
            for c in chats.values():
                c.clarify('Se borraran todos los recordatorios, lo siento, puedes agregarlos de nuevo en unas horas.')
                for r in c.recordatorios:
                    if r.seg != -1:
                        c.clarify('.', reply=r.message_id)
        elif text == '/chatid':
            chat.clarify(str(message.chat.id), True)
        elif text == '/userid':
            chat.clarify(str(message.from_user.id), True)
        elif text == '.' and message.reply_to_message != None:
            r = chat.recordatorio_from_message(message.reply_to_message.message_id)
            if r != None:
                chat.clarify_edit_r(subindex_r)
        elif text.startswith('/edit'):
            if subindex_r is not None:
                chat.clarify_edit_r(subindex_r, showtime=False)
            else:
                chat.clarify('It does not exist.')
        elif text.startswith('/merge'):
            if subindex_r is not None:
                chat.actual_r.merge_with(subindex_r)
                subindex_r.cancel()
                chat.update_lastinfomessage()
                chat.clarify('Mergeado.')
            else:
                chat.clarify('No existe eso.')
        elif text.startswith('/view') and subindex_r != None:
            chat.clarify_edit_r(subindex_r, showtime=True)
        elif text.startswith('/done'):
            if subindex_r is None:
                chat.clarify('It does not exist.')
            elif subindex_r.seg == -1:
                chat.clarify('Already done.')
            else:
                chat.clarify('Done')
                subindex_r.cancel()
            perform_next(chat)
        elif text.startswith('/ok') and subindex_r != None:
            subindex_r.cancel()
            chat.update_lastinfomessage()
        elif text.startswith('/periodic') and subindex_r != None:
            subindex_r.setadj(PERIODIC, True)
            chat.clarify(PERIODICHELP)
        elif text.startswith('/alarm') and subindex_r != None:
            subindex_r.setadj(ALARM, True)
            chat.clarify(ALARMHELP)
        elif text.startswith('/day') and chat.actual_r != None:
            if subindex != -1:
                chat.actual_r.restart(subindex * DAY)
                chat.clarify(ill_remember_text_builder(subindex, 'day'))
            else:
                chat.actual_r.restart(randint(DAY, 3 * DAY))
                chat.clarify(ill_remember_text_builder(3, 'day'))
        elif text.startswith('/hour') and chat.actual_r != None:
            if subindex != -1:
                chat.actual_r.restart(subindex * HOUR)
                chat.clarify(ill_remember_text_builder(subindex, 'hours'))
            else:
                chat.actual_r.restart(randint(2 * HOUR, 4 * HOUR))
                chat.clarify(ill_remember_text_builder(8, 'hours'))
        elif text.startswith('/min') and chat.actual_r is not None:
            if subindex != -1:
                chat.actual_r.restart(subindex * MIN)
                chat.clarify(ill_remember_text_builder(subindex, 'minute'))
            else:
                chat.actual_r.restart(randint(10 * MIN, 20 * MIN))
                chat.clarify(ill_remember_text_builder(30, 'minute'))
        elif text.startswith('...') and chat.actual_r is not None:
            chat.actual_r.append_message_id(message.message_id)
            chat.clarify('Last reminder has been expanded.')
        else:
            # Create a new Recordatorio
            r = chat.new_rec(message)

            segs = get_defualt_seconds()
            extrainfo = 'Ok.\n'

            chat.clarify(extrainfo + REC_AGREGADO, siosi=text.endswith('..'), rec=r)

            r.restart(segs)
            chat.actual_r = r
        
    except Exception as e:
        traceback.print_exc()


if __name__ == '__main__':
    print('Starting...')

    change_original_stdout()

    # Intenta cargar el archivo existente asi rellena el dict chats:
    try:
        load()
        print('Chats loaded. len_chats: ' + str(len(chats)))
    except Exception as e:
        print('There is no file' + CHATSFILENAME + ' or something went wrong.')
        traceback.print_exc()

        # Save again
        save()

    updater = Updater(token=TOKEN)
    dispatcher = updater.dispatcher

    # Empieza el ciclo de los days:
    each_day_timer.start()

    # Si cargo algo desde el archivo, restaura el alltimers
    if chats != dict():
        print('Recreating timers...')
        for c in chats.values():
            for r in c.recordatorios:
                r.recreate_timer()

    # Migration code
    if False:
        print('Mudando...')
        for c in chats.values():
            for r in c.recordatorios:
                pass
                # setattr(r, 'message_ids', [r.message_id, ])

    def any_update(update, context):
        bot = context.bot
        if update.message and update.message.text and update.message.text == '/exit' and update.message.from_user.id == ADMIN_USER_ID:
            bot.send_message(update.message.chat.id, 'bye bye')
            updater.stop()
            print('Bot killed by /exit')
            exit()
        elif update.edited_message != None:
            any_message(bot, update.edited_message)
        elif update.message is not None:
            any_message(bot, update.message)
        else:
            any_message(bot, None)


    core_handler = MessageHandler(Filters.all, any_update, run_async=True)
    dispatcher.add_handler(core_handler)

    updater.start_polling()
    try:
        print('Press Ctrl+C to exit.')
        while True:
            sleep(0.5)
    except KeyboardInterrupt:
        print('Ctrl+C detected. Bye bye.')

    print('Waiting for update.stop()...')
    updater.stop()

    print('Saving...')
    save()

    # Cancela todos los timers para que no ocurran cosas raras despues:
    print('Closing timers')
    for t in alltimers:
        t.cancel()
    each_day_timer.cancel()

    print('Bye bye.')
