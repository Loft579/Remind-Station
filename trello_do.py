import pickle
import traceback

from typing import List

import telegram
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
import html
from datetime import datetime
from utils import *
from datetime import datetime
from constants import *
from trello import *
from telegram import Bot
import time

bot = Bot(token=TELEGRAM_BOT_TOKEN)
chats_last_card = dict()
chats_mode = dict()
chat_map = dict()
mute = dict()
last_preview = dict()
inject_start_args = dict()

def ini_chats_mode(chat_id):
    if not chat_id in chats_mode:
        chats_mode[chat_id] = {"boards_all" : [], "boards_members" : {}}
        for board_id in get_whitelist_boards_id():
            chats_mode[chat_id]["boards_members"][board_id] = list()

class PassReturn:
    def __init__(self):
        self.is_last_edited = False
        self.sec_set = None
        self.card_collected = None
        self.code_collected = None
        self.cards_extract = list()
        self.sorted_cards = ""
        self.is_card_done = False
        self.is_add_cmd_done = False
        self.hashtags_collected = []

def clarify(chat_id, text, parse_mode = "", reply_markup = None):
    try:
        return bot.send_message(chat_id, text[-4000:], parse_mode = parse_mode, reply_markup = reply_markup)
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

def little_show(name):
    little = name
    if len(name) > NAME_LIMIT:
        little = name[:NAME_LIMIT-3] + "..."
    return little.replace('\n', ' ')

#important function of loop-modify architecture
def refresh_pass(target_chat,
set_last_card = False,
get_card = False,
modify_sec = False,
inject_start = None, #with algebra, stablish the start value
clarify_list = False,
sort_by = False,
collect_times = False,
done_card = False,
add_cmd = False,
clean = False,
find = False,
collect_hashtags = False,
find_desc = False):
    if inject_start == None:
        inject_start = modify_sec
    else:
        inject_start = inject_start

    print("new refresh_pass")
    
    cards_need_add = dict()

    return_info = PassReturn()

    if set_last_card == -1:
        set_last_card = False

    if target_chat != None:
        if target_chat in chats_last_card:
            if set_last_card == False:
                set_last_card = chats_last_card[target_chat]
    
    chats_ids = dict()
    
    #check Trello lists
    lists = get_all_lists_from_boards()
    for list_ in lists:
        for code_str in get_commands_set(list_["name"]):
            if code_str != "done":
                try:
                    code_int = int(code_str)
                except:
                    code_int = None
                if code_int != None:
                    chat_map[code_int] = {"idBoard" : list_["idBoard"], "list_id" : list_["id"], "done_list_id" : None}
    for list_ in lists:
        for code_str in get_commands_set(list_["name"]):
            if code_str == "done":
                for chat_id in chat_map:
                    if chat_map[chat_id]["idBoard"] == list_["idBoard"]:
                        chat_map[chat_id]["done_list_id"] = list_["id"]

    see_args_remind = [] #values of remind if time passes.
    

    cards_updated = get_all_cards_from_boards()
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

                    # check if the bot is muted
                    global mute
                    if not code[0] in mute.keys():
                        mute[code[0]] = list()
                    is_muted = False
                    now = datetime.now(TIMEZONE)
                    seconds_of_day = now.hour * HOUR + now.minute * MIN + now.second
                    for time_range in mute[code[0]]:
                        if time_range[0] <= seconds_of_day <= time_range[1]:
                            is_muted = True
                    
                        if code[1] != 0 and not is_muted:
                            if int(time.time()) > (code[2] + code[3]):
                                old_cmd = "[" + TRELLO_CALL_CMD + " " + command_set + "]"
                                if old_cmd in u_card["desc"]:
                                    new_cmd = "["+ TRELLO_CALL_CMD + " " + str(code[0]) + " " + str(code[1]) + " " + str(code[2] + abs(code[3]) * int(max((time.time() - code[2]) / abs(code[3]),1))) + " " + str(abs(code[3])) + "]"
                                    edition = edit_from_desc(u_card, old_cmd, new_cmd)
                                    u_card = edition
                                    command_set = get_commands_set(new_cmd)[0]
                                    code = trello_str_to_list(command_set)
                                    chats_last_card[code[0]] = code[1]
                                    see_args_remind.append([code[0],code[1]])

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
                                        if target_chat in chat_map:
                                            if chat_map[target_chat]["done_list_id"] != None:
                                                edition_2 = change_card_list(u_card["id"], chat_map[target_chat]["done_list_id"])
                                                if edition_2 != None:
                                                    u_card = edition_2
                                        return_info.is_card_done = True
                            if ignore_cmd_set:
                                continue
                            
                            #with argument modify_sec
                            if inject_start != modify_sec:
                                modify_sec = code[3]
                            if not isinstance(modify_sec,bool) and modify_sec != False:
                                if code[1] == set_last_card:
                                    if inject_start >= 0:
                                        inject_start = inject_start - modify_sec
                                    else:
                                        inject_start = inject_start
                                    new_cmd = "[" + TRELLO_CALL_CMD + " " + str(code[0]) + " " + str(code[1]) + " " + str(int(time.time()) + inject_start) + " " + str(modify_sec) + "]"
                                    edition = edit_from_desc(u_card,"[" + TRELLO_CALL_CMD + " " + command_set + "]", new_cmd)
                                    if edition != None:
                                        u_card = edition
                                        command_set = get_commands_set(new_cmd)[0]
                                        code = trello_str_to_list(command_set)
                                        return_info.sec_set = modify_sec


                            #with argument sort_by
                            if sort_by != False:
                                collect_this_name = False
                                if (find == False and find_desc == False):
                                    collect_this_name = True
                                if type(find) is str:
                                    if find in u_card["name"]:
                                        collect_this_name = True
                                if type(find_desc) is str:
                                    if find_desc in u_card["desc"]:
                                        collect_this_name = True
                                if collect_this_name:
                                    time_str = ""
                                    if collect_times == True:
                                        time_str = datetime.fromtimestamp(code[2] + code[3] +ADJUST_UTC*HOUR).strftime('%Y-%m-%d %H:%M:%S') + " - " + seg_to_str((int(code[2]) + int(code[3])) - int(time.time())) + "\n"
                                    elif collect_times == "ago":
                                        time_str = seg_to_str(int(time.time()) - int(code[2])) + " ago started\n"
                                    return_info.cards_extract.append({"date": code[2] + code[3], "start_date": code[2], "msg_part":f'/done{code[1]} /selecteds{code[1]} /see{code[1]} {time_str}{little_show(str(u_card["name"]))}\n'})

                            if collect_hashtags == True:
                                parts = u_card["desc"]
                                parts = parts.split("/#")
                                parts.pop(0)
                                for part in parts:
                                    hashtag_name = part.split(".")[0]
                                    if not hashtag_name in return_info.hashtags_collected:
                                        return_info.hashtags_collected.append(hashtag_name)

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
            for chat_id in chats_mode:
                if (u_card["idBoard"] in chats_mode[chat_id]["boards_all"]) or any(item in u_card["idMembers"] for item in chats_mode[chat_id]["boards_members"][u_card["idBoard"]]):
                    chats_check_empty.append(chat_id)

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
        call_values_i = 0
        for call_values in see_args_remind:
            see(call_values[0], call_values[1], is_reminded = True, call_values_i = call_values_i)
            call_values_i += 1
        for chat_id in laid:
            see(chat_id, laid[chat_id])
        
        # getting information to create code free of “loop-modify architecture”, now the processed info as return_info.
        if sort_by == "earliest_reminded":
            return_info.cards_extract.sort(key=lambda x: x["start_date"], reverse=False)
        if sort_by == "earliest":
            return_info.cards_extract.sort(key=lambda x: x["date"], reverse=False)
        if sort_by == "latests":
            return_info.cards_extract.sort(key=lambda x: x["date"], reverse=True)
        if clean == True:
            return_info.sorted_cards += "deleted:\n"
        for dict_ in return_info.cards_extract:
            return_info.sorted_cards += dict_["msg_part"]

        return return_info

def see(chat_id, subindex, is_reminded = "", ignore_time_left = False, call_values_i = 0):
    the_pass = refresh_pass(chat_id, set_last_card = subindex, get_card = subindex, collect_hashtags = True, collect_times=True, find_desc = SELECTED_STR, sort_by="earliest_reminded")
    if the_pass.card_collected != None:

        # Create button with the link to the card of Trello
        '''
        button = InlineKeyboardButton(the_pass.card_collected["name"], url=the_pass.card_collected["url"])
        button2 = InlineKeyboardButton("🔄 Actualizar Estado", callback_data="actualizar_estado")
        button3 = InlineKeyboardButton("❌ Eliminar Carta", callback_data="eliminar_carta")
        keyboard = InlineKeyboardMarkup([[button]])'''

        preview =  "/sec" + str(int(int(the_pass.code_collected[3]) * 2)) + " /min144 /hour1 /hour2 /hour4 /hour6 /hour8 /hour12 /day1 /day2 /day4 /day7 /inject_start /date0 🚂\n"
        for hashtag in the_pass.hashtags_collected:
            preview += "/" + hashtag + str(the_pass.code_collected[1]) + " "
        if is_reminded == True:
            is_reminded = "\n⏰ /see" + str(the_pass.code_collected[1]) + "\n"
            preview = the_pass.sorted_cards + "\n" + preview
        card_name = html.escape(the_pass.card_collected["name"])
        card_url = html.escape(the_pass.card_collected["url"])
        name = f'<blockquote><a href="{card_url}">{card_name}</a></blockquote>'
        time_left = " | " + seg_to_str((int(the_pass.code_collected[2]) + int(the_pass.code_collected[3])) - int(time.time()))
        if ignore_time_left:
            time_left = ""
        if call_values_i == 0:
            if chat_id in last_preview:
                try:
                    bot.delete_message(chat_id, last_preview[chat_id])
                except:
                    pass
            last_preview[chat_id] = clarify(chat_id, preview).message_id
        clarify(chat_id, "/track" + str(the_pass.code_collected[1]) + " /track_fade" + " /track_undofade\n" + "/done" + str(the_pass.code_collected[1]) + " /selecteds" + str(the_pass.code_collected[1]) + " /stop" + str(the_pass.code_collected[1]) + " " + is_reminded + name + seg_to_str(int(the_pass.code_collected[3])) + time_left, parse_mode="HTML")

    else:
        if the_pass.is_last_edited == False:
            clarify(chat_id, "not card found, try using a valid ID.")
