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

EDITS = '''/done{}
&/min30 | /hour4
/hour12 | /day2
/day5 | /day30&'''

# Si este numero es 1, guardara 1 vez por dia.
# Si es 48, guardara 48 veces por dia.
PROB_DE_APAGADO = 24

PERIODICHELP = '''Listo, es periodicó.& Ahours elige un período si quieres: /hour8 /day1 /day7 ... etc&'''

ALARMHELP = '''Listo.'''

AUN_NO_HAY_RECS = '''Este chat no tiene recordatorios.
'''

MUTED = 0
ONLYTQ = 1
CLEANER = 2

# Adjetivos:
AUTOSET = 0  # Si su timer fue seteado automaticamente
PERIODIC = 1
ALARM = 2

MODOSHELP = '''
' /mode0 ' [modo silencioso] manda pocos mensajes.
' /mode1 ' [modo ignorador] ignora los 'tengo que'.
' /mode2 ' [modo limpiador] borra mensajes propios.'''