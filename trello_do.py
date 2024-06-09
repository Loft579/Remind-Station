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

class PassReturn:
    def __init__(self):
        self.is_last_edited = False
        self.sec_set = None
        self.card_collected = None
        self.code_collected = None
        self.names_message = ""
        self.is_card_done = False
        self.is_add_cmd_done = False

def clarify(chat_id, text):
    try:
        bot.send_message(chat_id, text)
    except telegram.error.Unauthorized:
        print("message unauthorized to send")
    except telegram.error.BadRequest as e:
        print("BadRequest\n" + str(e))
        

def get_available_id(simple_ids):
        i = 1
        while i != False:
            if not (i in simple_ids):
                return i
                i = False
            else:
                i+=1

#important function
def refresh_pass(target_chat,
set_last_card = False,
get_card = False,
modify_sec = False,
clarify_list = False,
collect_names = False,
done_card = False,
add_cmd = False,
clean = False):

    
    cards_need_add = dict()

    return_info = PassReturn()

    if set_last_card == -1:
        set_last_card = False

    if target_chat != None:
        if target_chat in chats_last_card:
            if set_last_card == False:
                set_last_card = chats_last_card[target_chat]
    
    chats_ids = dict()
    
    #check list

    tengoque_lists[0] = None
    tengoque_lists[1] = None
    
    lists = get_all_lists_from_board(board_id)
    if lists != None:
        for list_ in lists:
            if '[' + TRELLO_CALL_CMD + ']' in list_['name']:
                tengoque_lists[0] = list_['id']
            if '[' + TRELLO_CALL_CMD + ' done]' in list_['name']:
                tengoque_lists[1] = list_['id']
    
    if clean == True:
        return_info.names_message += "deleted:\n"

    cards_updated = update_cards()
    if cards_updated != None:
        for card in cards_updated:
            u_card = card
            card_chats = []
            for command_set in get_commands_set(card["desc"]): 
                ignore_cmd_set = False
                try:
                    code = trello_str_to_list(command_set)
                except:
                    code = None
                if code != None:

                    #collect every chat_id assigned to the card in order to check if the card needs to be added when the card read is over.
                    card_chats.append(code[0])

                    if code[1] != 0:

                        if int(time.time()) > (code[2] + code[3]):
                            old_cmd = "[" + TRELLO_CALL_CMD + " " + command_set + "]"
                            if old_cmd in u_card["desc"]:
                                new_cmd = "["+ TRELLO_CALL_CMD + " " + str(code[0]) + " " + str(code[1]) + " " + str(int(time.time())) + " " + str(code[3] * 2) + "]"
                                edition = edit_from_desc(u_card, old_cmd, new_cmd)
                                if edition != None:
                                    u_card = edition
                                    command_set = new_cmd
                                    code = trello_str_to_list(get_commands_set(new_cmd)[0])
                                    chats_last_card[code[0]] = code[1]
                                    clarify(code[0], "/see" + str(code[1]) + " " + str(u_card["name"]) + "\n" + u_card["url"])

                        #collect all simple_id info in order to add a card with a not-used simple_id when all cards are read.
                        if not code[0] in chats_ids:
                            chats_ids[code[0]] = list()
                        chats_ids[code[0]].append(code[1])

                        if code[0] == target_chat:

                            #with argument clean
                            if clean == True:
                                edition = edit_from_desc(u_card, "[" + TRELLO_CALL_CMD + " " + command_set + "]", "")
                                if edition != None:
                                    ignore_cmd_set = True
                                    u_card = edition

                            if ignore_cmd_set:
                                continue

                            #with argument done_card
                            if done_card != False:
                                if (done_card == -1 and set_last_card == code[1]) or done_card == code[1]:
                                    new_cmd = "[" + TRELLO_CALL_CMD + " " + str(code[0]) + " 0 " + str(code[2]) + " " + str(code[3])  + "]"
                                    edition = edit_from_desc(u_card, "[" + TRELLO_CALL_CMD + " " + command_set + "]", new_cmd)
                                    if edition != None:
                                        ignore_cmd_set = True #assert imaginario: no debe haber nada después de ["if code[1] != 0:" y lo de dentro] hasta que termine el elemento command_set del "for"
                                        u_card = edition
                                        if tengoque_lists[1] != None:
                                            edition_2 = change_card_list(u_card["id"], tengoque_lists[1])
                                            if edition_2 != None:
                                                u_card = edition_2
                                        return_info.is_card_done = True
                            if ignore_cmd_set:
                                continue
                            
                            #with argument modify_sec
                            if modify_sec != False and modify_sec != -1:
                                if code[1] == set_last_card:
                                    new_cmd = "[" + TRELLO_CALL_CMD + " " + str(code[0]) + " " + str(code[1]) + " " + str(int(time.time())) + " " + str(modify_sec) + "]"
                                    edition = edit_from_desc(u_card,"[" + TRELLO_CALL_CMD + " " + command_set + "]", new_cmd)
                                    if edition != None:
                                        command_set = new_cmd
                                        u_card = edition
                                        code = trello_str_to_list(get_commands_set(new_cmd)[0])
                                        return_info.sec_set = modify_sec

                            #with argument collect_names
                            if collect_names == True:
                                return_info.names_message += "/see" + str(code[1]) + " " + str(u_card["name"]) + '\n'

                            #with argument clarify_list
                            if clarify_list == True:
                                clarify(target_chat, str(u_card))

                            #with argument set_last_card
                            if target_chat in chats_last_card:
                                if set_last_card != chats_last_card[target_chat]:
                                    if set_last_card == code[1]:
                                        chats_last_card[target_chat] = set_last_card
                                        return_info.is_last_edited = True
                            
                            

                            #with argument get_card
                            if get_card != False:
                                if get_card == -1:
                                    if code[1] == set_last_card:
                                        return_info.card_collected = u_card
                                        return_info.code_collected = code
                                elif get_card == code[1]:
                                    return_info.card_collected = u_card
                                    return_info.code_collected = code
                        
                        #add last_card if there is no last_card
                        if not code[0] in chats_last_card:
                            chats_last_card[code[0]] = code[1]


            #collect info in order to add the card. check if the card needs to be added
            chats_check_empty = []
            if add_cmd != False and add_cmd == u_card["id"]:
                chats_check_empty.append(target_chat)
            
            #automatically add the card
            for adj_chat in chats_mode:
                if chats_mode[adj_chat] in u_card["idMembers"] or chats_mode[adj_chat] == "all":
                    chats_check_empty.append(adj_chat)

            for chat_id in chats_check_empty:
                if chat_id not in card_chats:
                    if not chat_id in cards_need_add:
                        cards_need_add[chat_id] = []
                    cards_need_add[chat_id].append(u_card)
                
        laid = {} #in order to check the last available id added to the bot Telegram chat
        for chat_id in cards_need_add:
            for card in cards_need_add[chat_id]:
                if not chat_id in chats_ids:
                    chats_ids[chat_id] = list()
                available_id = get_available_id(chats_ids[chat_id])
                edition = add_to_desc(card, "[" + TRELLO_CALL_CMD + " " + str(chat_id) + " " + str(available_id) + " " + str(int(time.time())) + " " + str(DEFAULT_TIME) + "]" )
                if edition != None:
                    chats_ids[chat_id].append(available_id)
                    laid[chat_id] = available_id
                    if add_cmd != False and add_cmd != -1 and card["id"] == add_cmd:
                        return_info.is_add_cmd_done = True

        for chat_id in laid:
            clarify(chat_id, "/see" + str(laid[chat_id]))
        
        return return_info
