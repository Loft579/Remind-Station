import os
import dotenv
import sys
import argparse

# Esto es por si la zona hoursria del server difiere de lo que vos necesitas
CURRENT_TIME_SHIFT_HOURS = -3

TELEGRAM_BOT_TOKEN = os.environ['TELEGRAM_BOT_TOKEN']
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY', default=None)

MIN = 60
HOUR = 60 * MIN
DAY = HOUR * 24
YEAR = DAY * 365

ADJUST_UTC = -3

PRIVATEWELCOME = '''Hi. You may tell me what do you want to do and I will help you.
/help para ver comandos especiales.'''

GROUPWELCOME = PRIVATEWELCOME


HELP = '''
'<message>' create a new card and import to the bot
' /add <URL> ' import a card from Trello by URL
' /done<X> ' done the X card
' /names ' show list of card names
' /times ' show list of times with card names
' /sec<secs> ' set seconds to the selected card
' /min<mins> ' set minutes to the selected card
' /hour<hours> ' set hours to the selected card
' /day<days> ' set days to the selected card
' /stop ' stop card's reminding
' / <text> ' add text to the end of the card name
' /selecteds ' just the hashtag's command, add card to the selecteds list
advanced:
' /mute <hh:mm:ss> <hh:mm:ss> ' mute card between time range of the day
' /mute clear ' clear mute time ranges
' /date <month of the year> <optional, day of the month> <h of the day> <min of the hour> ' put date to the selected card
' /<hashtag><X> ' set the hashtag
' /#<hashtag> ' show list of all cards with the hashtag specified
' /clean ' unimport all cards. ⚠️ be careful, this will reset the bot for you.
' /mode ' mode command help
' "P"/"p" ' show list of all cards with the hashtag #Pending.
' /track ' for statistics, end the last tracking and start tracking the X Trello card now
' /track_fade ' set unknown end for the tracked card, the last one tracked
' /track_undo_fade ' undo the last tracked card and set unknown end for remaining last card
' /debug_help ' debug help.
' /list ' show list of reminders.
' /show<X>' show the X card
'''

DEBUGHELP = '''
/ping
/chat_id
/my_user_id
/version
'''

ADMIN_USER_ID = 43759228
ADMIN_CHAT_ID = 43759228

RECORDARTEXT = '''👆
/edit{} &| /hours | /days &| /done{}
'''

REC_AGREGADO = '''/edit{} | /done{}&
/hour2 | /day1 | /day3&'''

EDITS = '''
👌 /done{}&

Postpone:
/min5 | /min10 | /min15 | /min45
/hour2 | /hour3 | /hour5 | /hour8
/hour13 | /day1 | /day2  | /day3
/day5 | /day8 | /day13 | /day21
/day34| /day55 | /day89 | /day365&'''

# Si este numero es 1, guardara 1 vez por day.
# Si es 48, guardara 48 veces por day.
PROB_DE_APAGADO = 24 * 60

PERIODICHELP = '''Done, it is periodic now& Now pick a period: /hour8 /day1 /day7 ... etc&'''

ALARMHELP = '''Done.'''

AUN_NO_HAY_RECS = '''This chat has no reminders.
'''

MUTED = 0
ONLYTQ = 1
CLEANER = 2

# Adjetivos:
AUTOSET = 0  # Si su timer fue seteado automaticamente
PERIODIC = 1
ALARM = 2

MODOSHELP = '''
' /mode <board_url> all ' set mode to add all cards from the board, ⚠️ this will add all cards from the board, be careful
' /mode <board_url> @<username> ' set mode to add all cards from the board that have the member specified, ⚠️ this will add all these cards from the board, be careful
' /mode off ' clean the modes
'''

TRELLO_CALL_CMD = "/tengoquebot"

NAME_LIMIT = 60

DEFAULT_TIME = 4*HOUR

PENDING_STR = "/#Pending."
SELECTED_STR = "/#selecteds."