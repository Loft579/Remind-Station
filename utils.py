from datetime import datetime, timedelta
from constants import *


def ill_remember_text_builder(cantidad, tipo):
    return u'I will remember it in ' + str(cantidad) + u' ' + tipo


def calculate_start_date(month):
    # Adjusts years if month is greater than 12
    actual_year = datetime.now().year
    adjusted_year = actual_year + (month - 1) // 12
    adjusted_month = (month - 1) % 12 + 1
    start_date = datetime(adjusted_year, adjusted_month, 1)
    return int(start_date.timestamp()) 

def seg_to_str(seg):
    ret = ''

    showseg = True
    if seg > DAY:
        ret += '{} days '.format(int(seg / DAY))
        seg = seg % DAY
        showseg = False
    if seg > HOUR:
        ret += '{} hours '.format(int(seg / HOUR))
        seg = seg % HOUR
        showseg = False
    if seg > MIN:
        ret += '{} minutes '.format(int(seg / MIN))
        seg = seg % MIN
    if showseg != False:
        ret += str(int(seg)) + ' seconds'
    if ret and ret[-1] == " ":
        ret = ret[:-1]
    return ret


def datetimenow():
    return datetime.now() + timedelta(hours=CURRENT_TIME_SHIFT_HOURS)
