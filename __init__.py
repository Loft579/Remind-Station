# -*- coding: utf-8 -*-
# Creo que funciona con 3.8
# python-telegram-bot~=13.1

from telegram.ext import Filters, MessageHandler, Updater
from telegram import Bot
import logging
from threading import Timer
from random import randint
from time import time, sleep
from datetime import datetime
import pickle
import todatetimes

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)


with open("token", 'r') as f:
    TOKEN = f.readline().strip()

ADMIN_USER_ID = 43759228

updater = None
dispatcher = None
bot = None
botname = "tengo_que_bot"
ADMIN_CHAT_ID = 43759228

RECORDARTEXT = """¿Hiciste esto?
/editar{} &| /horas | /dias &| /borrar{}
"""

REC_AGREGADO = """/editar{} | /borrar{}&
/min50 | /hora8 | /dia1&"""

EDITS = """/borrar{}
&/min30 | /hora1
/hora4 | /hora8
/dia1 | /dia3
/periodic{}
/alarm{}&"""

# Si este numero es 1, guardara 1 vez por dia.
# Si es 48, guardara 48 veces por dia.
PROB_DE_APAGADO = 48

PERIODICHELP = """Listo, es periodicó.& Ahora elige un período si quieres: /hora8 /dia1 /dia7 ... etc&"""

ALARMHELP = """Listo."""

AUN_NO_HAY_RECS = """Este chat no tiene recordatorios.
"""

chats = dict()  # chatid => Chat
CHATSFILENAME = "chats.pickle"

alltimers = []

MIN = 60
HORA = 60 * MIN
DIA = HORA * 24

PRIVATEWELCOME = """Hola. Puedes decirme todo lo que tengas que hacer, y yo te lo recordaré.
/help para ver comandos especiales."""

GROUPWELCOME = """Hola. Voy a recordar cada mensaje que contenga un "tengo que".
/help para ver comandos especiales."""

HELP = """
' /info ' Para ver la lista de recordatorios.
' /modo ' Para cambiar los modos.
' /info ' Para ver la lista de todos los recordatorios.
' /info X ' Para mostrar solo los recodatorios que contengan X.
' /next ' Para ver el recordatorio mas cercano en el tiempo.
' /periodicX ' Convierte el recordatorio X en periódico, haciendo que suene cada cierto tiempo constante, una y otra vez.
' /alarmX ' Convierte el recordatorio X en una alarma, que sonará mucho más veces hasta que se apague.

Bot creado por @agusavior /debughelp
"""

DEBUGHELP = """
/save
/ping
/chatid
/userid
/start
"""


def cada_dia():
    global cada_dia_timer

    # Guardado Diario.
    save()

    # Vuelve a ejecutar esta funcion luego de 1 dia.
    cada_dia_timer = Timer(DIA / PROB_DE_APAGADO, cada_dia)
    cada_dia_timer.start()


cada_dia_timer = Timer(DIA / PROB_DE_APAGADO, cada_dia)


def seg_to_str(seg):
    ret = ""

    showseg = True
    if seg > DIA:
        ret += "{} dias ".format(int(seg / DIA))
        seg = seg % DIA
        showseg = False
    if seg > HORA:
        ret += "{} horas ".format(int(seg / HORA))
        seg = seg % HORA
        showseg = False
    if seg > MIN:
        ret += "{} minutos ".format(int(seg / MIN))
        seg = seg % MIN
    if showseg and seg != 0:
        ret += str(int(seg)) + " segundos"
    return ret


def save():
    with open(CHATSFILENAME, 'wb') as handle:
        pickle.dump(chats, handle, protocol=pickle.HIGHEST_PROTOCOL)


def load():
    with open(CHATSFILENAME, 'rb') as handle:
        dictchatsviejo = pickle.load(handle)
        print("dictchatsviejo tenia un len de " + str(len(dictchatsviejo)))
        chats.update(dictchatsviejo)


# Adjetivos:
AUTOSET = 0  # Si su timer fue seteado automaticamente
PERIODIC = 1
ALARM = 2


class Recordatorio:
    def __init__(self, message, uid):
        self.message = message

        self.seg = -1  # si es -1, no esta activado. si es distinto marca en
        # cuanto tiempo se ejecutara el timer desde que se inicio con start
        self.timerindex = -1
        self.epoch_of_start = -1  # epoch del momento cuando se inicio el timer

        # self.periodic = False

        self.uid = uid

        # En general, para agregarle caracteristicas a un rec.
        self.adjectives = set()

    def setadj(self, adj, value):
        if value:
            self.adjectives.add(adj)
        elif adj in self.adjectives:
            self.adjectives.remove(adj)

    def trigger(self):
        nombre = ""
        try:
            nombre = self.message.from_user.first_name
            assert (isinstance(nombre, str))
        except:
            nombre = "che"

        mychat = chats[self.message.chat.id]

        # Primero recuerda:
        mychat.clarify(nombre + " " + RECORDARTEXT, rec=self, reply=self.message, siosi=True)

        # Segundo, pone el mensaje este en actual_r
        mychat.actual_r = self

        # Y por las dudas lo pospone:
        if ALARM in self.adjectives:
            self.restart(max(MIN, self.seg / 3), autoset=True)
        if PERIODIC in self.adjectives:
            self.restart(self.seg, autoset=True)
        else:
            self.restart(self.seg * 2, autoset=True)

    # start o restart, es para poner el timer
    def restart(self, seg, autoset=False):
        self.cancel()
        timer = Timer(seg, self.trigger)
        self.timerindex = len(alltimers)
        alltimers.append(timer)
        self.seg = seg
        self.epoch_of_start = time()
        timer.start()
        self.setadj(AUTOSET, autoset)

    def cancel(self):
        if self.seg != -1 and self.timerindex in range(len(alltimers)):
            alltimers[self.timerindex].cancel()
        self.timerindex = -1
        self.seg = -1

    # retorna cuantos segundos faltan para que suene este rec
    def how_much_left(self):
        yapaso = time() - self.epoch_of_start
        return self.seg - yapaso

    # esta funcion se debe ejecutar 1 vez por cada recordatorio
    # cada vez que se apaga el bot y se prende de vuelta, ya que
    # los timers se han borrado y necesita llenar alltimers de vuelta.
    def recreate_timer(self):
        if self.seg == -1:
            # no hace falta, el timer ese ya no sirve mas
            return

        timer = Timer(self.how_much_left(), self.trigger)
        self.timerindex = len(alltimers)
        alltimers.append(timer)
        timer.start()


MUTED = 0
ONLYTQ = 1
CLEANER = 2
MODOSHELP = """
' /modo0 ' [modo silencioso] manda pocos mensajes.
' /modo1 ' [modo ignorador] ignora los 'tengo que'.
' /modo2 ' [modo limpiador] borra mensajes propios."""


class Chat:
    def __init__(self, telegramchat):
        self.telegramchat = telegramchat
        self.recordatorios = []
        self.actual_r = None  # El recordatorio implicitamente actual
        self.modomolesto = (telegramchat.type == "private")
        self.lastuid = 0
        self.lastmessage = None
        self.lastnewtext = ""
        self.lastinfomessage = None
        self.lastinfomessage_extra = ""

        self.adjectives = set()

        # if telegramchat.type != "private":
        #    self.adjectives.add(MUTED)

    def setadj(self, adj, value):
        if value:
            self.adjectives.add(adj)
        elif adj in self.adjectives:
            self.adjectives.remove(adj)

    # Retorna la informacion de todas las cosas internas de este chat
    def info(self, extra=""):
        haymugre = False
        info = ""
        for r in self.recordatorios:
            # Por las dudas:
            if r.message.text == None:
                r.message.text = ""

            if extra not in r.message.text:
                continue

            if r.seg == -1:
                info += u"❎ "
                haymugre = True
            else:
                if ALARM in r.adjectives:
                    info += u"⏰ "
                elif PERIODIC in r.adjectives:
                    info += u"📰 "
                elif AUTOSET in r.adjectives:
                    info += u"⌛️ "
                else:
                    info += u"📌 "

            info += u"/ver" + str(r.uid)
            if r.seg != -1:
                info += " /ya" + str(r.uid)
            info += "\n"

            info += r.message.text + "\n"

        if haymugre:
            info += u"¿ /limpiar ?"

        if info != "":
            return info
        else:
            if extra != "":
                return "No existe recordatorio con '{}'.".format(extra)
            else:
                return AUN_NO_HAY_RECS

    def update_lastinfomessage(self):
        if self.lastinfomessage != None:
            bot.edit_message_text(self.info(), chat_id=self.telegramchat.id, message_id=self.lastinfomessage.message_id)

    # Manda un mensaje. Es casi como bot.send_message
    def clarify(self, text, siosi=False, rec=None, reply=None):
        if not siosi and MUTED in self.adjectives:
            return None

        # Se fija si debe modificarse el mensaje anterior:
        if self.lastmessage != None:
            tempid = self.lastmessage.message_id
            if CLEANER in self.adjectives:
                bot.delete_message(self.telegramchat.id, tempid)
            elif self.lastnewtext != "":
                try:
                    bot.edit_message_text(self.lastnewtext, chat_id=self.telegramchat.id, message_id=tempid)
                except:
                    print("Un mensaje no se pudo editar. No importa mucho.")

        if rec != None:
            text = text.format(*(5 * [rec.uid]))

        # Si existe el & es porque
        # el proximo last debera editar su texto interno
        temp = ""
        if "&" in text:
            ws = text.split("&")
            if len(ws) == 3:
                temp = ws[0] + ws[2]

            text = text.replace("&", "")

        # Manda el mensaje:
        m = None
        if reply == None:
            m = bot.send_message(self.telegramchat.id, text)
        else:
            m = bot.send_message(self.telegramchat.id, text, reply_to_message_id=reply.message_id)
            # m = bot.reply_to(reply, text)

        # Pone los last para la proxima
        self.lastmessage = m
        self.lastnewtext = temp

        return m

    def clarify_edit_r(self, r, showtime=True):
        self.actual_r = r

        s = ""
        if showtime:
            if r.seg != -1:
                s = u"⏳ en {}\n".format(seg_to_str(r.how_much_left()))
            else:
                s = u"⌛️ no sonará\n"

        self.clarify(s + EDITS, siosi=True, rec=r, reply=r.message)

    def recordatorio_from_message(self, message_id):
        for r in self.recordatorios:
            if r.message.message_id == message_id:
                return r
        return None

    def new_rec(self, message):
        r = Recordatorio(message, self.lastuid + 1)
        self.lastuid += 1
        self.recordatorios.append(r)
        return r

    def rec_from_uid(self, uid):
        for r in self.recordatorios:
            if r.uid == uid:
                return r
        return None


def te_lo_recordare_en(cantidad, tipo):
    if cantidad == None:
        cantidad = "unos"
        tipo += "s"
    elif cantidad > 1:
        tipo += "s"
    return u"Te lo recordaré en " + str(cantidad) + u" " + tipo


@run_async
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
    # elif text.startswith("/si") and subindex_r != None:
    #    subindex_r.cancel()
    #    chat.clarify("Perfecto 👍")
    # elif text.startswith("/auno") and subindex_r != None:
    #    chat.clarify("Ok, lo recordare mas tarde.")
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
            segs = (d - datetime.now()).total_seconds()
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
    bot = Bot(token=TOKEN)

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
