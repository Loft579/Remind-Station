import pickle
import traceback

from typing import List

import telegram
from utils import seg_to_str
from constants import *
from trello import *
from telegram import Bot
import time

bot = Bot(token=TELEGRAM_BOT_TOKEN)
chats_last_card = dict()
chats_mode = dict()
tengoque_lists = [None, None]

class pass_return:
    def __init__(self):
        self.is_last_edited = False
        self.sec_set = None
        self.card_collected = None
        self.code_collected = None
        self.names_message = ""
        self.is_card_done = False
        self.is_add_cmd_done = False

def clarify(chat_id, text):
    # Manda el mensaje:
    if len(text) >= 3000:
        textcropped = text[:1000] + ' [...] ' + text[-1000:] #possible trello mod
    else:
        textcropped = text

    try:
        m = bot.send_message(chat_id, textcropped)
    except telegram.error.Unauthorized:
        print(f'Can\'t send message. Unauthorized. Probably blocked by user {chat_id}.')
        m = None
    except telegram.error.BadRequest as e:
        if 'Message to reply not found' in str(e):
            m = bot.send_message(chat_id, textcropped)
    return m

def get_avaliable_id(simple_ids):
        i = 1
        while i != False:
            if not (i in simple_ids):
                return i
                i = False
            else:
                i+=1

#important function
def refresh_pass(target_chat,
first_pass = False,
set_last_card = False,
get_card = False,
modify_sec = False,
clarify_list = False,
collect_names = False,
done_card = False,
add_cmd = False):


    cards_need_add = dict()

    return_info = pass_return()
    if target_chat != None:
        
        #if there is no cards
        if not target_chat in chats_last_card and first_pass == False:
            pass #mod

        if set_last_card == False or set_last_card == -1:
            set_last_card = chats_last_card[target_chat]
    
    chats_ids = dict()
    
    #check list

    tengoque_lists[0] = None
    tengoque_lists[1] = None
    
    lists = get_all_lists_from_board(board_id)
    for list_ in lists:
        if '[' + TRELLO_CALL_CMD + ']' in list_['name']:
            tengoque_lists[0] = list_['id']
        if '[' + TRELLO_CALL_CMD + ' done]' in list_['name']:
            tengoque_lists[1] = list_['id']
    
    for card in update_cards():
        card_chats = []
        for command_set in get_commands_set(card["desc"]): 
            try:
                code = trello_str_to_list(command_set)
            except:
                code = None
            if code != None:

                #collect every chat_id assigned to the card in order to check if the card needs to be added when the card read is over.
                card_chats.append(code[0])

                if code[1] != 0:

                    #collect all simple_id info in order to add a card with a not-used simple_id when all cards are read.
                    if not code[0] in chats_ids:
                        chats_ids[code[0]] = list()
                    chats_ids[code[0]].append(code[1])

                    

                    if code[0] == target_chat:

                        #with argument done_card
                        if done_card != False:
                            if (done_card == -1 and set_last_card == code[1]) or done_card == code[1]:
                                new_name = "[" + TRELLO_CALL_CMD + " " + str(code[0]) + " 0 " + str(code[2]) + " " + str(code[3])  + "]"
                                edition = edit_from_desc(card, "[" + TRELLO_CALL_CMD + " " + command_set + "]", new_name)
                                if tengoque_lists[1] != None:
                                    change_card_list(card["id"], tengoque_lists[1])
                                if edition != None:
                                    return_info.is_card_done = True

                        #with argument collect_names
                        if collect_names == True:
                            return_info.names_message += "/show_plus" + str(code[1]) + " " + str(card["name"]) + '\n'

                        #with argument clarify_list
                        if clarify_list == True:
                            clarify(target_chat, str(card))

                        #with argument set_last_card
                        if set_last_card != chats_last_card[target_chat]:
                            if set_last_card == code[1]:
                                chats_last_card[target_chat] = set_last_card
                                return_info.is_last_edited = True
                        
                        #with argument modify_sec
                        if modify_sec != False and modify_sec != -1:
                            if code[1] == set_last_card:
                                edition = edit_from_desc(card,"[" + TRELLO_CALL_CMD + " " + command_set + "]","[" + TRELLO_CALL_CMD + " " + str(code[0]) + " " + str(code[1]) + " " + str(int(time.time())) + " " + str(modify_sec) + "]")
                                if edition != None:
                                    return_info.sec_set = modify_sec

                        #with argument get_card
                        if get_card != False:
                            if get_card == -1:
                                if code[1] == set_last_card:
                                    return_info.card_collected = card
                                    return_info.code_collected = code
                            elif get_card == code[1]:
                                return_info.card_collected = card
                                return_info.code_collected = code

                    #with argument first_pass
                    if first_pass:
                        if not code[0] in chats_last_card:
                            chats_last_card[code[0]] = code[1]

                    if int(time.time()) > (code[2] + code[3]):
                        old_str = "[" + TRELLO_CALL_CMD + " " + command_set + "]"
                        if old_str in card["desc"]:
                            edition = edit_from_desc(card, old_str, "["+ TRELLO_CALL_CMD + " " + str(code[0]) + " " + str(code[1]) + " " + str(int(time.time())) + " " + str(code[3] * 2) + "]")
                            if edition != None:
                                chats_last_card[code[0]] = code[1]
                                clarify(code[0], "/show_plus" + str(code[1]) + " " + str(edition["name"]) + "\n" + edition["url"])
        
        #collect info in order to add the card. check if the card needs to be added
        chats_check_empty = []
        if add_cmd != False and add_cmd == card["id"]:
            chats_check_empty.append(target_chat)
        idMembers = card["idMembers"]
        for chat_id in chats_check_empty:
            if chat_id not in card_chats:
                if not chat_id in cards_need_add:
                    cards_need_add[chat_id] = []
                cards_need_add[chat_id].append(card)
            
    
    for chat_id in cards_need_add:
        for card in cards_need_add[chat_id]:
            avaliable_id = get_avaliable_id(chats_ids[chat_id])
            edition = add_to_desc(card, "[" + TRELLO_CALL_CMD + " " + str(chat_id) + " " + str(avaliable_id) + " " + str(int(time.time())) + " " + str(DEFAULT_TIME) + "]" )
            if edition != None:
                chats_ids[chat_id].append(avaliable_id)
                if add_cmd != False and add_cmd != -1 and card["id"] == add_cmd:
                    return_info.is_add_cmd_done = True

    return return_info



    
