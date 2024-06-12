import os
import dotenv
dotenv.load_dotenv()

# Esto es por si la zona hoursria del server difiere de lo que vos necesitas
CURRENT_TIME_SHIFT_HOURS = -3

TELEGRAM_BOT_TOKEN = os.environ['TELEGRAM_BOT_TOKEN']

MIN = 60
HOUR = 60 * MIN
DAY = HOUR * 24

PRIVATEWELCOME = '''Hi. You may tell me what do you want to do and I will help you.
/help para ver comandos especiales.'''

GROUPWELCOME = PRIVATEWELCOME


HELP = ''' 
' /show ' show the X card
' /add <URL> ' import card from Trello by URL
' /done<X> ' stop the X card
' /list ' Show list of reminders.
' /names ' show list of card names
' /sec<secs> ' set seconds to the selected card
' /min<mins> ' set minutes to the selected card
' /hour<hours> ' set hours to the selected card
' /day<days> ' set days to the selected card
' /clean ' unimport all cards
' /mode <"off" or "all" or "@"<username> assigned to cards> ' set mode
' /debug_help ' debug help.
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
' /mode @<username> ' add all cards of the board that have the member specified
' /mode all ' add all cards of the board
' /mode off ' no mode
'''

TRELLO_CALL_CMD = "/tengoquebot"

NAME_LIMIT = 120

DEFAULT_TIME = 4*HOUR