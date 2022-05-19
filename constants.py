# Esto es por si la zona hoursria del server difiere de lo que vos necesitas
CURRENT_TIME_SHIFT_HOURS = -3

with open('token', 'r') as f:
    TOKEN = f.readline().strip()

MIN = 60
HOUR = 60 * MIN
DAY = HOUR * 24

PRIVATEWELCOME = '''Hi. You may tell me what do you want to do and I will help you.
/help para ver comandos especiales.'''

GROUPWELCOME = PRIVATEWELCOME

HELP = '''
' /list ' Show list of reminders.
' /mode ' Configuration.
' /list X ' Show list of reminders that contains X.
' /next ' The next reminder.

Created by @agusavior /debughelp
'''

DEBUGHELP = '''
/save
/ping
/chatid
/userid
/start
'''

CHATSFILENAME = 'chats.pickle'

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
PROB_DE_APAGADO = 24

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
' /mode0 ' [modo silencioso] Send few messages.
' /mode1 ' [modo ignorador] Deprecated.
' /mode2 ' [modo limpiador] Delete own messages.'''