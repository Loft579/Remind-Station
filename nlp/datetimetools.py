from datetime import datetime, date, time, timedelta

ORDEN = [None, "sec", "min", "hora", "dia", "mes", "ano", None]

def add_one_month(t):
    diaactual = t.day
    un_dia = timedelta(days = 1)
    t += un_dia
    while True:
        if diaactual == t.day:
            break
        t += un_dia
    return t

def add_one(fecha, key):
    if key == "min":
        fecha += timedelta(minutes = 1)
    elif key == "hora":
        fecha += timedelta(hours = 1)
    elif key == "dia":
        fecha += timedelta(days = 1)
    elif key == "mes":
        fecha = add_one_month(fecha)
    elif key == "ano":
        fecha = fecha.replace(year = fecha.year + 1)
    else:
        assert False
    return fecha

def change(fecha, key, value):
    if key == "sec":
        return fecha.replace(second = value)
    elif key == "min":
        return fecha.replace(minute = value)
    elif key == "hora":
        return fecha.replace(hour = value)
    elif key == "dia":
        return fecha.replace(day = value)
    elif key == "mes":
        return fecha.replace(month = value)
    elif key == "ano":
        return fecha.replace(year = value)
    else:
        assert False

def get(fecha, key):
    if key == "sec":
        return fecha.second
    elif key == "min":
        return fecha.minute
    elif key == "hora":
        return fecha.hour
    elif key == "dia":
        return fecha.day
    elif key == "mes":
        return fecha.month
    elif key == "ano":
        return fecha.year
    else:
        assert False

def next(key):
    for i in range(len(ORDEN)):
        if ORDEN[i] == key:
            return ORDEN[i + 1]
    assert False

def prev(key):
    for i in range(len(ORDEN)):
        if ORDEN[i] == key:
            return ORDEN[i - 1]
    assert False

def getfirst(key):
    if key == "sec":
        return 0
    elif key == "min":
        return 0
    elif key == "hora":
        return 0
    elif key == "dia":
        return 1
    elif key == "mes":
        return 1
    else:
        assert False
    
