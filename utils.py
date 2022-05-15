from datetime import datetime, timedelta
from constants import *


def ill_remember_text_builder(cantidad, tipo):
    return u'I will remember it in ' + str(cantidad) + u' ' + tipo


def seg_to_str(seg):
    ret = ''

    showseg = True
    if seg > DAY:
        ret += '{} dias '.format(int(seg / DAY))
        seg = seg % DAY
        showseg = False
    if seg > HOUR:
        ret += '{} hours '.format(int(seg / HOUR))
        seg = seg % HOUR
        showseg = False
    if seg > MIN:
        ret += '{} minutes '.format(int(seg / MIN))
        seg = seg % MIN
    if showseg and seg != 0:
        ret += str(int(seg)) + ' seconds'
    return ret


def datetimenow():
    return datetime.now() + timedelta(hours=CURRENT_TIME_SHIFT_HOURS)
