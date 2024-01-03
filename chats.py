import pickle
import traceback

from typing import List

import telegram

import recordatorios
from utils import seg_to_str
from constants import *
from telegram import Bot

bot = Bot(token=TOKEN)

chats = dict()  # chatid => Chat


def save():
    for chat in chats.values():
        chat.lastmessage = None
        chat.lastinfomessage = None
    with open(CHATSFILEPATH, 'wb') as handle:
        pickle.dump(chats, handle, protocol=pickle.HIGHEST_PROTOCOL)


def load():
    with open(CHATSFILEPATH, 'rb') as handle:
        dictchatsviejo = pickle.load(handle)
        print('dictchatsviejo tenia un len de ' + str(len(dictchatsviejo)))
        chats.update(dictchatsviejo)


class Chat:
    def __init__(self, telegramchat):
        self.id = telegramchat.id
        self.recordatorios: List[recordatorios.Recordatorio] = []
        self.actual_r = None  # El recordatorio implicitamente actual
        self.modomolesto = (telegramchat.type == 'private')
        self.lastuid = 0
        self.lastmessage = None
        self.lastnewtext = ''
        self.lastinfomessage = None
        self.adjectives = set()

    def setadj(self, adj, value):
        if value:
            self.adjectives.add(adj)
        elif adj in self.adjectives:
            self.adjectives.remove(adj)

    # Retorna la informacion de todas las cosas internas de este chat
    def info(self, extra=''):
        haymugre = False
        info = ''
        for r in self.recordatorios:
            # Por las dudas:
            if r.text is None:
                r.text = ''

            if extra not in r.text:
                continue

            if r.seg == -1:
                info += u'❎ '
                haymugre = True
            else:
                if ALARM in r.adjectives:
                    info += u'⏰ '
                elif PERIODIC in r.adjectives:
                    info += u'📰 '
                elif AUTOSET in r.adjectives:
                    info += u'⌛️ '
                else:
                    info += u'📌 '

            info += u'/view' + str(r.uid)
            if r.seg != -1:
                info += ' /ok' + str(r.uid)
                # info += ' /merge' + str(r.uid)
            info += '\n'

            info += r.text + '\n'

            more = len(r.message_ids) - 1
            if more > 0:
                info += f'* And {more} more...\n'

        if haymugre:
            info += u'/clean'

        if info != '':
            return info
        else:
            if extra != '':
                return '"{}" not found.'.format(extra)
            else:
                return AUN_NO_HAY_RECS

    def update_lastinfomessage(self):
        if self.lastinfomessage is not None:
            bot.edit_message_text(self.info(), chat_id=self.id, message_id=self.lastinfomessage.message_id)

    # Manda un mensaje. Es casi como bot.send_message
    def clarify(self, text, siosi=False, rec=None, reply_message_id=None, reply_message_ids=None):
        if not siosi and MUTED in self.adjectives:
            return None

        # Se fija si debe modificarse el mensaje anterior:
        if self.lastmessage is not None:
            tempid = self.lastmessage.message_id
            if CLEANER in self.adjectives:
                bot.delete_message(self.id, tempid)
            elif self.lastnewtext != '':
                try:
                    bot.edit_message_text(self.lastnewtext, chat_id=self.id, message_id=tempid)
                except Exception as e:
                    traceback.print_exc()

        if rec is not None:
            text = text.format(*(5 * [rec.uid]))

        # Si existe el & es porque
        # el proximo last debera editar su texto interno
        temp = ''
        if '&' in text:
            ws = text.split('&')
            if len(ws) == 3:
                temp = ws[0] + ws[2]

            text = text.replace('&', '')

        # Manda el mensaje:
        if len(text) >= 3000:
            textcropped = text[:1000] + ' [...] ' + text[-1000:]
        else:
            textcropped = text

        try:
            m = bot.send_message(self.id, textcropped, reply_to_message_id=reply_message_id)
        except telegram.error.Unauthorized:
            print(f'Can\'t send message. Unauthorized. Probably blocked by user {self.id}.')
            m = None
        except telegram.error.BadRequest as e:
            if 'Message to reply not found' in str(e):
                m = bot.send_message(self.id, textcropped)

        # May point to each extra message_id
        if reply_message_ids is not None:
            i = 1
            for message_id in reply_message_ids:
                if message_id != reply_message_id:
                    bot.send_message(self.id, '👆' * i, reply_to_message_id=message_id)
                    i += 1

        # Pone los last para la proxima
        self.lastmessage = m
        self.lastnewtext = temp

        return m

    def clarify_edit_r(self, r, showtime=True):
        self.actual_r = r

        s = ''
        if showtime:
            if r.seg != -1:
                s = u'⏳ in {}\n'.format(seg_to_str(r.how_much_left()))
            else:
                s = u'⌛️ no ring\n'

        debug_info = f'debug[{str(r.text)}]'

        self.clarify(s + debug_info + EDITS, siosi=True, rec=r, reply_message_id=r.message_id, reply_message_ids=r.message_ids)

    def recordatorio_from_message(self, message_id):
        for r in self.recordatorios:
            if r.message_id == message_id:
                return r
        return None

    def new_rec(self, message):
        r = recordatorios.Recordatorio(message, self.lastuid + 1, self)
        self.lastuid += 1
        self.recordatorios.append(r)
        return r

    def rec_from_uid(self, uid):
        for r in self.recordatorios:
            if r.uid == uid:
                return r
        return None
