# -*- coding: utf-8 -*-
# Creo que funciona con 3.8
# python-telegram-bot~=13.1

from telegram.ext import Filters, MessageHandler, Updater
import logging
from random import randint
from time import sleep
from chats import *
from recordatorios import *
import todatetimes
from utils import *
from constants import *

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

updater = None
dispatcher = None
botname = "tengo_que_bot"

def cada_dia():
    global cada_dia_timer

    # Guardado Diario.
    save()

    # Vuelve a ejecutar esta funcion luego de 1 dia.
    cada_dia_timer = Timer(DIA / PROB_DE_APAGADO, cada_dia)
    cada_dia_timer.start()

cada_dia_timer = Timer(DIA / PROB_DE_APAGADO, cada_dia)


def any_message(bot, message):
    text = message.text
    if text == None:
        text = ""

    # Primero se fija si debe ignorar el comando y de paso crea el comando mas limpio
    if "@" in text:
        if text[text.index("@") + 1:] != botname:
            return
        text = text[:text.index("@")]

    # Guardas:
    # Guarda 1: minimiza todo
    text = text.lower()
    # guarda 2: reemplaza tildes (solo esto por el dias)
    text = text.replace(u"í", u"i")
    # guarda 3: los "no tengo que" no sirven.
    text = text.replace("no tengo que", "")

    # agarra el chat (si no existe lo crea):
    if message.chat.id not in chats:
        chats[message.chat.id] = Chat(message.chat)
    chat = chats[message.chat.id]

    # sub-index o sea, el X tal que /diaX
    subindex = -1
    subindex_r = None
    i = 0
    temp = ""
    for c in text:
        if c == " ":
            break
        elif c in map(str, range(10)):
            temp += c
    if temp != "":
        subindex = int(temp)
        subindex_r = chat.rec_from_uid(subindex)
    else:
        subindex_r = chat.actual_r

    # analiza el caso...
    if text == "/start":
        if message.chat.type == "private":
            chat.clarify(PRIVATEWELCOME, True)
        else:
            chat.clarify(GROUPWELCOME, True)
    elif text == "/help":
        chat.clarify(HELP, True)
    elif text == "/modo" and subindex == -1:
        chat.clarify(MODOSHELP, True)
    elif text.startswith("/modo"):
        adj = subindex
        chat.setadj(adj, adj not in chat.adjectives)
        if adj in chat.adjectives:
            chat.clarify("Se activo ese modo. /modo{} para des-activarlo".format(adj), True)
        else:
            chat.clarify("Se desactivo ese modo. /modo{} para activarlo".format(adj), True)
    elif text == "/ping":
        chat.clarify("pong", True)
    elif text.startswith("/info"):
        textinfo = chat.info(text[6:])
        chat.lastinfomessage = chat.clarify(textinfo, siosi=True)
    elif text == "/next":
        sooner = None
        for r in chat.recordatorios:
            if r.seg == -1:
                continue

            if sooner == None or (sooner.how_much_left() > r.how_much_left()):
                sooner = r

        if sooner != None:
            chat.clarify_edit_r(sooner)
        else:
            chat.clarify("No existen recordatorios activos.", True)

    elif text == "/limpiar":
        new = []
        for r in chat.recordatorios:
            if r.seg != -1:
                new.append(r)
        chat.recordatorios = new

        chat.update_lastinfomessage()
    elif text == "/debughelp" and message.chat.id == ADMIN_CHAT_ID:
        chat.clarify(DEBUGHELP, True)
    elif text == "/save":
        save()
        chat.clarify("Guardado.")
    elif text == "/proxbigchange":
        for c in chats.values():
            c.clarify("Se borraran todos los recordatorios, lo siento, puedes agregarlos de nuevo en unas horas.")
            for r in c.recordatorios:
                if r.seg != -1:
                    c.clarify(".", reply=r.message)
    elif text == "/chatid":
        chat.clarify("El chat id de este chat es: " + str(message.chat.id), True)
    elif text == "/userid":
        chat.clarify("Tu user id es: " + str(message.from_user.id), True)
    elif text == "." and message.reply_to_message != None:
        r = chat.recordatorio_from_message(message.reply_to_message.message_id)
        if r != None:
            chat.clarify_edit_r(subindex_r)
    elif text.startswith("/editar"):
        if subindex_r != None:
            chat.clarify_edit_r(subindex_r, showtime=False)
        else:
            chat.clarify("No existe eso.")
    elif text.startswith("/ver") and subindex_r != None:
        chat.clarify_edit_r(subindex_r, showtime=True)
    elif text.startswith("/borrar"):
        if subindex_r == None:
            chat.clarify("No existe eso")
        elif subindex_r.seg == -1:
            chat.clarify("Ya estaba borrado")
        else:
            chat.clarify("Borrado")
            subindex_r.cancel()
    elif text.startswith("/ya") and subindex_r != None:
        subindex_r.cancel()
        chat.update_lastinfomessage()
    elif text.startswith("/periodic") and subindex_r != None:
        subindex_r.setadj(PERIODIC, True)
        chat.clarify(PERIODICHELP)
    elif text.startswith("/alarm") and subindex_r != None:
        subindex_r.setadj(ALARM, True)
        chat.clarify(ALARMHELP)
    elif text.startswith("/dia") and chat.actual_r != None:
        if subindex != -1:
            chat.actual_r.restart(subindex * DIA)
            chat.clarify(te_lo_recordare_en(subindex, "dia"))
        else:
            chat.actual_r.restart(randint(DIA, 3 * DIA))
            chat.clarify(te_lo_recordare_en(None, "dia"))
    elif text.startswith("/hora") and chat.actual_r != None:
        if subindex != -1:
            chat.actual_r.restart(subindex * HORA)
            chat.clarify(te_lo_recordare_en(subindex, "hora"))
        else:
            chat.actual_r.restart(randint(2 * HORA, 4 * HORA))
            chat.clarify(te_lo_recordare_en(None, "hora"))
    elif text.startswith("/min") and chat.actual_r != None:
        if subindex != -1:
            chat.actual_r.restart(subindex * MIN)
            chat.clarify(te_lo_recordare_en(subindex, "minuto"))
        else:
            chat.actual_r.restart(randint(10 * MIN, 20 * MIN))
            chat.clarify(te_lo_recordare_en(None, "minuto"))
    elif (ONLYTQ not in chat.adjectives and (message.chat.type == "private" or "tengo que" in text) or text.startswith(
            "tq")):
        datatimes = []
        try:
            datatimes, _ = todatetimes.to_list_of_datetime(text)
        except Exception as e:
            print(e)
            chat.clarify("Hubo un error al interpretar tu recordatorio.")

        guarda = 8
        for d in datatimes:
            guarda -= 1
            if guarda == 0:
                chat.clarify("Muchos recordatorios, no se agregaron todos los solicitados.")
                break

            r = chat.new_rec(message)

            extrainfo = "Sonará: {}\n".format(str(d)[:-6])
            segs = (d - datetimenow()).total_seconds()
            if segs < 3:
                segs = randint(HORA, HORA + 15 * MIN)
                extrainfo = "Te lo recuerdo en un rato\n"

            chat.clarify(extrainfo + REC_AGREGADO, siosi=text.endswith(".."), rec=r)

            r.restart(segs)
            chat.actual_r = r


if __name__ == "__main__":
    print("Inicia el main")

    # Intenta cargar el archivo existente asi rellena el dict chats:
    try:
        load()
        print("Cargados los chats desde el archivo. # de Chats: " + str(len(chats)))
    except Exception as e:
        print("No existe el archivo " + CHATSFILENAME + " o hubo un error.")
        print("El problema fue: " + str(e))
        print("Se creara dicho archivo")
        save()

    updater = Updater(token=TOKEN)
    dispatcher = updater.dispatcher

    # Empieza el ciclo de los dias:
    cada_dia_timer.start()

    # Si cargo algo desde el archivo, restaura el alltimers
    if chats != dict():
        print("recreando timers...")
        for c in chats.values():
            for r in c.recordatorios:
                r.recreate_timer()


    def any_update(update, context):
        bot = context.bot
        if update.message and update.message.text:
            if update.message.text == "/exit" and update.message.from_user.id == ADMIN_USER_ID:
                bot.send_message(update.message.chat.id, "muerto")
                updater.stop()
                print("Bot muerto por /exit")
                exit()
            elif update.edited_message != None:
                any_message(bot, update.edited_message)
            elif update.message != None:
                any_message(bot, update.message)
        else:
            print("update.message es None o texto vacio")


    core_handler = MessageHandler(Filters.text | Filters.command, any_update, run_async=True)
    dispatcher.add_handler(core_handler)

    updater.start_polling()
    try:
        print("Aprieta Ctrl-C para cerrar")
        while True:
            sleep(0.5)
        # print "Salio del raw_input(). Se cerrarÃ¡."
    except KeyboardInterrupt:
        print("Se detectÃ³ Ctrl-C. Se cerrarÃ¡.")

    print("update.stop()...")
    updater.stop()

    print("Guardamos...")
    save()

    print("Cancela timers")

    # cancela todos los timers para que no ocurran cosas raras despues:
    for t in alltimers:
        t.cancel()
    cada_dia_timer.cancel()

    print("Closed")
