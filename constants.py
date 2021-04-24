# Esto es por si la zona horaria del server difiere de lo que vos necesitas
CURRENT_TIME_SHIFT_HOURS = -3

with open("token", 'r') as f:
    TOKEN = f.readline().strip()

MIN = 60
HORA = 60 * MIN
DIA = HORA * 24

PRIVATEWELCOME = """Hola. Puedes decirme todo lo que tengas que hacer, y yo te lo recordaré.
/help para ver comandos especiales."""

GROUPWELCOME = """Hola. Voy a recordar cada mensaje que contenga un "tengo que".
/help para ver comandos especiales."""

HELP = """
' /info ' Para ver la lista de recordatorios.
' /modo ' Para cambiar los modos.
' /info ' Para ver la lista de todos los recordatorios.
' /info X ' Para mostrar solo los recodatorios que contengan X.
' /next ' Para ver el recordatorio mas cercano en el tiempo.
' /periodicX ' Convierte el recordatorio X en periódico, haciendo que suene cada cierto tiempo constante, una y otra vez.
' /alarmX ' Convierte el recordatorio X en una alarma, que sonará mucho más veces hasta que se apague.

Bot creado por @agusavior /debughelp
"""

DEBUGHELP = """
/save
/ping
/chatid
/userid
/start
"""

CHATSFILENAME = "chats.pickle"

ADMIN_USER_ID = 43759228
ADMIN_CHAT_ID = 43759228

RECORDARTEXT = """¿Hiciste esto?
/editar{} &| /horas | /dias &| /borrar{}
"""

REC_AGREGADO = """/editar{} | /borrar{}&
/hora2 | /dia1 | /dia3&"""

EDITS = """/borrar{}
&/min30 | /hora4
/hora12 | /dia2
/dia5 | /dia30
/periodic{}
/alarm{}&"""

# Si este numero es 1, guardara 1 vez por dia.
# Si es 48, guardara 48 veces por dia.
PROB_DE_APAGADO = 24

PERIODICHELP = """Listo, es periodicó.& Ahora elige un período si quieres: /hora8 /dia1 /dia7 ... etc&"""

ALARMHELP = """Listo."""

AUN_NO_HAY_RECS = """Este chat no tiene recordatorios.
"""

MUTED = 0
ONLYTQ = 1
CLEANER = 2

# Adjetivos:
AUTOSET = 0  # Si su timer fue seteado automaticamente
PERIODIC = 1
ALARM = 2

MODOSHELP = """
' /modo0 ' [modo silencioso] manda pocos mensajes.
' /modo1 ' [modo ignorador] ignora los 'tengo que'.
' /modo2 ' [modo limpiador] borra mensajes propios."""