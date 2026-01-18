# -*- coding: utf-8 -*-
# Creo que funciona con 3.8
# python-telegram-bot~=13.1
# telegram~=0.0.1

import argparse
import dotenv
import log

# Define how the command will be used in Terminal/Bash/Shell Script/Command Line
parser = argparse.ArgumentParser(description="Tengo Que Bot")
parser.add_argument('-e', '--env-file', type=str, required=False, help='The name of the environment file to load.')

# Get the arguments from command line
args = parser.parse_args()

if args.env_file:
    # Load env variables from file
    dotenv.load_dotenv(args.env_file)

import logging
from random import randint
import time
from time import sleep
from customstdout import change_original_stdout
from utils import *
from constants import *
#from whisperbot import openai_whisper_api
import adapter as adapter
import traceback
from trello_do import *
from imageutils import ImageUtils
from threading import Lock

# V3: Este archivo reemplaza al dispatcher de Telegram.
# Aquí definimos cómo "escuchar" mensajes y despacharlos a los handlers.
# Podés enchufar cualquier otra fuente de mensajes (consola, HTML, API REST).

def main():
    print("Remind-Station V3 iniciado...")
    while True:
        try:
            text = input(">> ")
            adapter_any(0, text)
        except Exception as e:
            adapter.error_handler(e)

if __name__ == "__main__":
    main()


logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

updater = None
dispatcher = None
botname = 'tengo_que_bot'

# Los seconds que se pospone el recordatorio la primera vez que se
# crea.
def get_defualt_seconds():
    return randint(HOUR * 6, HOUR * 8)



def adapter_any(bot, message):
    adapter.receive_message(bot, message)

    global inject_start_args
    if not message.chat.id in inject_start_args:
        inject_start_args[message.chat.id] = False
    text = message.text

    is_message_from_whisper_op = message.from_user.id == 43759228 or message.from_user.id == 424819435 or message.from_user.id == 80627582

    # If there is an image, download it
    if message.photo != []:
        file = message.photo[-1].get_file()
        image_filename = str(message.chat.id) + '_received_image.jpg'
        file.download(image_filename)
        logging.info("Image downloaded")
    else:
        image_filename = None

    if not text and message.caption:
        text = message.caption
    
    is_text_from_msg = True
    if not text and message.voice and is_message_from_whisper_op:
        filename = f'{message.chat.id}_received_audio.ogg'
        file = bot.getFile(message.voice.file_id)
        file.download(filename)
        assert os.path.exists(filename)
        text = openai_whisper_api(local_filepath=filename)
        is_text_from_msg = False

    if not text and image_filename is not None:
        text = ImageUtils.extract_text_from_image(image_path=image_filename)
        is_text_from_msg = False
    
    if not text:
        clarify(message.chat.id, "No text in message. Please send a message with text or a voice message.")
        return
    try:
        if inject_start_args[message.chat.id] == 2:
            inject_start_args[message.chat.id] = 1
        elif inject_start_args[message.chat.id] == 1:
            inject_start_args[message.chat.id] = False
    except:
        pass

    global mute

    # sub-index o sea, el X tal que /dayX, pero del mensaje enviado por el usuario
    subindex = -1

    temp = ''
    for c in text:
        if c == ' ':
            break
        elif c in map(str, list(range(10))):
            temp += c
    if temp != '':
        subindex = int(temp)

    # analiza el caso...
    if text == '/help':
        clarify(message.chat.id, HELP)
    elif text == '/hardcode':
        print("chats_mode:", chats_mode)
    elif text == '/mode' or text == '/mode ':
        clarify(message.chat.id, MODOSHELP)
    elif text == '/mode off':
        del chats_mode[message.chat.id]
        clarify(message.chat.id, "modes cleaned")
    elif text.startswith('/mode '):
        board_id = get_board_from_url(text.split(" ")[1])["id"]
        adj = text.split(" ")[2]
        print("adj:", adj)
        ini_chats_mode(message.chat.id)
        if adj == "all":
            chats_mode[message.chat.id]["boards_all"].append(board_id)
            clarify(message.chat.id, "all cards will be added in " + str(board_id))
        elif adj.startswith("@"):
            adj = adj[1:]
            user_id = get_user_id_by_name(adj)
            if user_id != None:
                chats_mode[message.chat.id]["boards_members"][board_id].append(user_id)
                clarify(message.chat.id, "mode settled in member " + str(user_id))
            else:
                clarify(message.chat.id, "cannot get the user")
        else:
            clarify(message.chat.id, "error: unknow mode")

    elif text.startswith('/see'):
        see(message.chat.id, subindex)
    elif text.startswith('/show'):
        the_pass = refresh_pass(message.chat.id, set_last_card = subindex, get_card = subindex)
        if the_pass.card_collected != None:
            the_card = the_pass.card_collected
            clarify(message.chat.id, "name:\n" + str(the_card["name"]))
            clarify(message.chat.id, "desc:\n" + str(the_card["desc"]))
            clarify(message.chat.id, "url:\n" + str(the_card["url"]))
            clarify(message.chat.id, "labels:\n" + str(the_card["labels"]))
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
        the_pass = refresh_pass(message.chat.id, sort_by = "latests")
        if the_pass.sorted_cards != "":
            clarify(message.chat.id, the_pass.sorted_cards)
        else:
            clarify(message.chat.id, "No names to view")
    elif text.startswith('/#') or text == "p" or text == "P":
        keyword = text.split(" ")[0] + "."
        if text == "p" or text == "P":
            keyword = PENDING_STR
        the_pass = refresh_pass(message.chat.id, sort_by = "latests", find_desc = keyword)
        if the_pass.sorted_cards != "":
            clarify(message.chat.id, the_pass.sorted_cards)
        else:
            clarify(message.chat.id, "No names to view")
    elif text == '/remove_hashtag_' or text == "/remove" or text == "/remove_hashtag" or text == "/remove hashtag":
        clarify(message.chat.id, "you must specify text to use 'remove_hashtag_<hashtag>'")
    elif text.startswith('/remove_hashtag_'):
        str_to_remove = text.split("_",2)[2].replace(str(subindex),"",1)
        str_to_remove = "/#" + str_to_remove + "."
        the_pass = refresh_pass(message.chat.id, set_last_card = subindex, get_card = subindex)
        edition = None
        if str_to_remove in the_pass.card_collected["desc"]:
            edition = edit_from_desc(the_pass.card_collected, str_to_remove, "")
        if edition != None:
            clarify(message.chat.id, "“" + str_to_remove + "” hashtag removed from the card")
        else:
            clarify(message.chat.id, "error in removing “" + str_to_remove + "” from the card description")
    elif text == '/times':
        the_pass = refresh_pass(message.chat.id, sort_by = "latests", collect_times = True)
        if the_pass.sorted_cards != "":
            clarify(message.chat.id, the_pass.sorted_cards)
        else:
            clarify(message.chat.id, "No times to view")
    elif text == '/clean':
        clarify(message.chat.id, "loading...")
        refresh_pass(message.chat.id, clean = True)
        clarify(message.chat.id, "clean done")
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
            clarify(message.chat.id, "couldn't be done to the specified card")
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
    elif text == '/inject_start':
        inject_start_args[message.chat.id] = 2
        clarify(message.chat.id, "hacked start date time for the next command")
    elif text.startswith('/sec'):
        modify_sec = subindex
        inject_start = None
        if inject_start_args[message.chat.id] != False:
            inject_start = modify_sec
            modify_sec = False
            clarify(message.chat.id, "argument injected")
        the_pass = refresh_pass(message.chat.id, modify_sec = modify_sec, inject_start = inject_start)
        if the_pass.sec_set != None:
            clarify(message.chat.id, "the card will be reminded in " + seg_to_str(the_pass.sec_set))
        else:
            clarify(message.chat.id, "error in changing time")
    elif text.startswith('/min'):
        modify_sec = subindex*MIN
        inject_start = None
        if inject_start_args[message.chat.id] != False:
            inject_start = modify_sec
            modify_sec = False
            clarify(message.chat.id, "argument injected")
        the_pass = refresh_pass(message.chat.id, modify_sec = modify_sec, inject_start = inject_start)
        if the_pass.sec_set != None:
            clarify(message.chat.id, "the card will be reminded in " + seg_to_str(the_pass.sec_set))
        else:
            clarify(message.chat.id, "error in changing time")
    elif text.startswith('/hour'):
        modify_sec = subindex*HOUR
        inject_start = None
        if inject_start_args[message.chat.id] != False:
            inject_start = modify_sec
            modify_sec = False
            clarify(message.chat.id, "argument injected")
        the_pass = refresh_pass(message.chat.id, modify_sec = modify_sec, inject_start = inject_start)
        if the_pass.sec_set != None:
            clarify(message.chat.id, "the card will be reminded in " + seg_to_str(the_pass.sec_set))
        else:
            clarify(message.chat.id, "error in changing time")
    elif text.startswith('/day'):
        modify_sec = subindex*DAY
        inject_start = None
        if inject_start_args[message.chat.id] != False:
            inject_start = modify_sec
            modify_sec = False
            clarify(message.chat.id, "argument injected")
        the_pass = refresh_pass(message.chat.id, modify_sec = modify_sec, inject_start = inject_start)
        if the_pass.sec_set != None:
            clarify(message.chat.id, "the card will be reminded in " + seg_to_str(the_pass.sec_set))
        else:
            clarify(message.chat.id, "error in changing time")
    elif text.startswith('/year'):
        modify_sec = subindex*YEAR
        inject_start = None
        if inject_start_args[message.chat.id] != False:
            inject_start = modify_sec
            modify_sec = False
            clarify(message.chat.id, "argument injected")
        the_pass = refresh_pass(message.chat.id, modify_sec = modify_sec, inject_start = inject_start)
        if the_pass.sec_set != None:
            clarify(message.chat.id, "the card will be reminded in " + seg_to_str(the_pass.sec_set))
        else:
            clarify(message.chat.id, "error in changing time")
    elif text.startswith("/stop"):
        modify_sec = DAY*35600
        inject_start = None
        if inject_start_args[message.chat.id] != False:
            inject_start = modify_sec
            modify_sec = False
            clarify(message.chat.id, "argument injected")
        the_pass = refresh_pass(message.chat.id, set_last_card = subindex, modify_sec = modify_sec, inject_start = inject_start, get_card=subindex)
        if the_pass.sec_set != None:
            clarify(message.chat.id, "the card will be reminded in " + seg_to_str(the_pass.sec_set) + "\nyou can also use: /remove_hashtag_" + SELECTED_STR.replace("/#","",1).replace(".","") + str(the_pass.code_collected[1]))
        else:
            clarify(message.chat.id, "error in changing time.\nyou can also use: /remove_hashtag_" + SELECTED_STR.replace("/#","",1).replace(".","") + str(the_pass.code_collected[1]))
    elif text == "/date":
        clarify(message.chat.id, "/date<month> <optional, days> etc")
    elif text.startswith("/date"):
        text_split = text.split(" ")
        month = subindex
        day = 1
        hour = 0
        minutes = 0
        try:
            day = int(text_split[1])
            hour = int(text_split[2])
            minutes = int(text_split[3])
        except:
            pass
        date = calculate_start_date(month) + ((day - 1) * DAY + hour * HOUR + minutes * MIN)

        modify_sec = date - int(time.time())
        inject_start = None
        if inject_start_args[message.chat.id] != False:
            inject_start = modify_sec
            modify_sec = False
            clarify(message.chat.id, "argument injected")
        
        the_pass = refresh_pass(message.chat.id, modify_sec = modify_sec, inject_start = inject_start)
        if the_pass.sec_set != None:
            clarify(message.chat.id, "the card will be reminded in " + seg_to_str(the_pass.sec_set))
        else:
            clarify(message.chat.id, "error in changing time")
    elif text == "/unmute":
        mute[message.chat.id] = list()
        clarify(message.chat.id, "mute time cleared")
    elif text.startswith("/mute"):
        if not message.chat.id in mute.keys():
            mute[message.chat.id] = list()
        text_split = text.split(" ")
        start = [0,0,0]
        end = [0,0,0]
        try:
            start_ = text_split[1].split(":")
            try:
                start[0] = int(start_[0])
                start[1] = int(start_[1])
                start[2] = int(start_[2])
            except:
                pass
        except:
            start = [0,0,0]
        try:
            end_ = text_split[2].split(":")
            try:
                end[0] = int(end_[0])
                end[1] = int(end_[1])
                end[2] = int(end_[2])
            except:
                pass
        except:
            end = [0,0,0]
        mute[message.chat.id].append((HOUR * start[0] + MIN * start[1] + start[2], HOUR * end[0] + MIN * end[1] + end[2]))

        start[1] = str(start[1])
        start[2] = str(start[2])
        if len(start[1]) == 1:
            start[1] = "0" + start[1]
        if len(start[2]) == 1:
            start[2] = "0" + start[2]
        end[1] = str(end[1])
        end[2] = str(end[2])
        if len(end[1]) == 1:
            end[1] = "0" + end[1]
        if len(end[2]) == 1:
            end[2] = "0" + end[2]
        clarify(message.chat.id, f"mute time now covering {start[0]}:{start[1]}:{start[2]} to {end[0]}:{end[1]}:{end[2]}")
    elif text.startswith("/track"):
        clarify(message.chat.id, "ok! use /help for tracking help.")
        the_pass = refresh_pass(message.chat.id, get_card = subindex)
        filename = f"track_{message.from_user.id}.txt"
        if "undo" in text:
            log.undo_last_log(filename)
        if "fade" in text:
            log.add_question_mark(filename)
        if not "undo" in text and not "fade" in text:
            log.activity(the_pass.card_collected["url"], filename)
    elif text.startswith("/") or text.startswith("/ "):
        addition = text.replace("/","",1)
        addition = addition.replace(str(subindex),"",1)
        if not text.startswith("/ "):
            addition = "/#" + addition.replace(" ", "") + "."
        the_pass = refresh_pass(message.chat.id, set_last_card = subindex, get_card = subindex)
        edition = None
        try:
            if not text.startswith("/ "):
                if not addition in the_pass.card_collected["desc"]:
                    edition = add_to_desc(the_pass.card_collected, addition)
                else:
                    clarify(message.chat.id, "hashtag already exists. are you sure you want to use /remove_hashtag_" + addition.replace("/#","",1).replace(".","") + str(the_pass.code_collected[1]) + " ?")
                    edition = "edition cancelled"
            else:
                edition = add_to_name(the_pass.card_collected, addition)
        except:
            pass
        if edition != None:
            if edition != "edition cancelled":
                clarify(message.chat.id, "“" + addition + "” added to card")
        else:
            clarify(message.chat.id, "error in adding “" + addition + "”")
    elif not text.startswith("/"):
        # Create a new card
        
        parts_text = ["",""]

        parts_text[0] = text

        if message.chat.id in chat_map:
            new_card = create_card(chat_map[message.chat.id]["list_id"], parts_text[0])
        else:
            clarify(message.chat.id, "please, create a list in Trello with this in his name:\n`[" + TRELLO_CALL_CMD + " " + str(message.chat.id) + "]`", parse_mode = "MarkdownV2")
            return

        if parts_text[1] != "":
            add_to_desc(new_card, parts_text[1])
        
        if image_filename is not None:
            add_image_to_card(new_card["id"], image_filename)

        the_pass = refresh_pass(message.chat.id, add_cmd = new_card["id"])
        if the_pass.is_add_cmd_done == True:
            clarify(message.chat.id, "card added")
        


if __name__ == '__main__':
    print('Starting...')
    change_original_stdout()

    # Using adapter bot instead of Telegram updater
    bot = adapter.bot
    any_message_lock = Lock()

    def any_update(update): #executed locally
        if update.message and update.message.text and update.message.text == '/exit' and update.message.from_user.id == ADMIN_USER_ID:
            bot.send_message(update.message.chat.id, 'bye bye')
            print('Bot killed by /exit')
            exit()
        elif hasattr(update, 'edited_message') and update.edited_message != None:
            pass # Nothing. Ignore in edited messages.
        else:
            try:
                with any_message_lock:
                    any_message(bot, update.message)
            except BaseException as e:
                print(f"Error in any_update: {e}")
                bot.send_message(update.message.chat.id, "code error: " + str(e))

    try:
        print('Press Ctrl+C to exit.')
        print('Local adapter mode - no Telegram polling')
        while True:
            try:
                refresh_pass(None)
            except BaseException as e:
                print(f"Error in refresh_pass: {e}")
            print("---\nchats_last_card:", chats_last_card,"\nchat_map:",chat_map,"\ntime:",time.time())
            sleep(10)
    except KeyboardInterrupt:
        print('\nCtrl+C detected. Bye bye.')

    print('Local adapter closed')


