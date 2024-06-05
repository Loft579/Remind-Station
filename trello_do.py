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
    try:
        bot.send_message(chat_id, text)
    except telegram.error.Unauthorized:
        print("message unauthorized to send")
    except telegram.error.BadRequest as e:
        print("BadRequest\n" + str(e))
        

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
set_last_card = False,
get_card = False,
modify_sec = False,
clarify_list = False,
collect_names = False,
done_card = False,
add_cmd = False,
clean = False):

    
    cards_need_add = dict()

    return_info = pass_return()

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
        for card in update_cards():
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
                            if old_cmd in card["desc"]:
                                new_cmd = "["+ TRELLO_CALL_CMD + " " + str(code[0]) + " " + str(code[1]) + " " + str(int(time.time())) + " " + str(code[3] * 2) + "]"
                                edition = edit_from_desc(card, old_cmd, new_cmd)
                                if edition != None:
                                    code = trello_str_to_list(get_commands_set(new_cmd)[0])
                                    chats_last_card[code[0]] = code[1]
                                    clarify(code[0], "/see" + str(code[1]) + " " + str(edition["name"]) + "\n" + edition["url"])

                        #collect all simple_id info in order to add a card with a not-used simple_id when all cards are read.
                        if not code[0] in chats_ids:
                            chats_ids[code[0]] = list()
                        chats_ids[code[0]].append(code[1])

                        if code[0] == target_chat:

                            #with argument clean
                            if clean == True:
                                edition = edit_from_desc(card, "[" + TRELLO_CALL_CMD + " " + command_set + "]", "")
                                ignore_cmd_set = True
                                return_info.names_message += str(code[1]) + " " + str(card["name"]) + '\n'
                            if ignore_cmd_set:
                                continue

                            #with argument done_card
                            if done_card != False:
                                if (done_card == -1 and set_last_card == code[1]) or done_card == code[1]:
                                    new_name = "[" + TRELLO_CALL_CMD + " " + str(code[0]) + " 0 " + str(code[2]) + " " + str(code[3])  + "]"
                                    edition = edit_from_desc(card, "[" + TRELLO_CALL_CMD + " " + command_set + "]", new_name)
                                    ignore_cmd_set = True
                                    if tengoque_lists[1] != None:
                                        change_card_list(card["id"], tengoque_lists[1])
                                    if edition != None:

                                        return_info.is_card_done = True
                            if ignore_cmd_set:
                                continue
                            
                            #with argument modify_sec
                            if modify_sec != False and modify_sec != -1:
                                if code[1] == set_last_card:
                                    new_cmd = "[" + TRELLO_CALL_CMD + " " + str(code[0]) + " " + str(code[1]) + " " + str(int(time.time())) + " " + str(modify_sec) + "]"
                                    edition = edit_from_desc(card,"[" + TRELLO_CALL_CMD + " " + command_set + "]", new_cmd)
                                    if edition != None:
                                        code = trello_str_to_list(get_commands_set(new_cmd)[0])
                                        return_info.sec_set = modify_sec


                            #with argument collect_names
                            if collect_names == True:
                                return_info.names_message += "/see" + str(code[1]) + " " + str(card["name"]) + '\n'

                            #with argument clarify_list
                            if clarify_list == True:
                                clarify(target_chat, str(card))

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
                                        return_info.card_collected = card
                                        return_info.code_collected = code
                                elif get_card == code[1]:
                                    return_info.card_collected = card
                                    return_info.code_collected = code
                        
                        #add last_card if there is no last_card
                        if not code[0] in chats_last_card:
                            chats_last_card[code[0]] = code[1]


            #collect info in order to add the card. check if the card needs to be added
            chats_check_empty = []
            if add_cmd != False and add_cmd == card["id"]:
                chats_check_empty.append(target_chat)
            
            #automatically add the card
            for adj_chat in chats_mode:
                if chats_mode[adj_chat] in card["idMembers"] or chats_mode[adj_chat] == "all":
                    chats_check_empty.append(adj_chat)

            for chat_id in chats_check_empty:
                if chat_id not in card_chats:
                    if not chat_id in cards_need_add:
                        cards_need_add[chat_id] = []
                    cards_need_add[chat_id].append(card) 
                
        
        for chat_id in cards_need_add:
            for card in cards_need_add[chat_id]:
                if not chat_id in chats_ids:
                    chats_ids[chat_id] = list()
                avaliable_id = get_avaliable_id(chats_ids[chat_id])
                edition = add_to_desc(card, "[" + TRELLO_CALL_CMD + " " + str(chat_id) + " " + str(avaliable_id) + " " + str(int(time.time())) + " " + str(DEFAULT_TIME) + "]" )
                if edition != None:
                    chats_ids[chat_id].append(avaliable_id)
                    if add_cmd != False and add_cmd != -1 and card["id"] == add_cmd:
                        return_info.is_add_cmd_done = True

        return return_info



        
