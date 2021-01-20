from datetime import datetime, timedelta
from constants import *


def te_lo_recordare_en(cantidad, tipo):
    if cantidad == None:
        cantidad = "unos"
        tipo += "s"
    elif cantidad > 1:
        tipo += "s"
    return u"Te lo recordaré en " + str(cantidad) + u" " + tipo


def seg_to_str(seg):
    ret = ""

    showseg = True
    if seg > DIA:
        ret += "{} dias ".format(int(seg / DIA))
        seg = seg % DIA
        showseg = False
    if seg > HORA:
        ret += "{} horas ".format(int(seg / HORA))
        seg = seg % HORA
        showseg = False
    if seg > MIN:
        ret += "{} minutos ".format(int(seg / MIN))
        seg = seg % MIN
    if showseg and seg != 0:
        ret += str(int(seg)) + " segundos"
    return ret


def datetimenow():
    return datetime.now() + timedelta(hours=CURRENT_TIME_SHIFT_HOURS)
