import re
import random
from datetime import datetime, date, time, timedelta
from calendar import monthrange
from tengoquev0.datetimetools import add_one, change, next, prev, get, getfirst

CATEGORIAS = ["sec", "min", "hora", "dia", "mes", "dsec", "dmin", "dhora", "ddia", "dmes", "dano"]
cortapalabras = ",.;/ "
HORAS = [str(i) for i in range(0, 24)] #de 0 a 23
MESES = [str(i) for i in range(1, 13)]
DIAS = [str(i) for i in range(1, 32)] #de 0 al 31
MESDICT = {"enero" : 1, "febrero" : 2, "marzo" : 3, "abril" : 4, "mayo" : 5, "junio" : 6, "julio" : 7, "agosto" : 8, "septiembre" : 9, "octubre" : 10, "noviembre" : 11, "diciembre" : 12}
DIADICT = { "lunes" : 0, "martes" : 1, "miercoles" : 2, "jueves" : 3, "viernes" : 4, "sabado" : 5, "domingo" : 6}
HSAMPM = ["hs", "am", "pm"]
MINS = [str(i) for i in range(0, 61)] + ["0" + str(i) for i in range(0, 10)]

#Agrega guiones bajos para juntar palabras
def juntar(string):
    def replace(string, cosa):
        cosa2 = cosa.replace(' ', '_')
        return string.replace(cosa, cosa2)
    string = replace(string, "pasado mañana")
    string = replace(string, "medio dia")
    return string

#Cambia algunas palabras
def cambiar(string):
    string = string.replace(" un ", " 1 ")
    string = string.replace(" una ", " 1 ")
    string = string.replace(" un par de ", " 2 ")
    unos = " " + str(random.randint(2, 4)) + " "
    string = string.replace(" unas ", unos)
    string = string.replace(" unos ", unos)

    #Dias
    #hoy = str(datetime.now())
    #hoy = hoy[8:10] + "/" + hoy[5:7] + "/" + hoy[0:4]
    #string = string.replace(" hoy ", hoy)

    #Horas
    string = string.replace(" de la tarde ", " pm ")
    string = string.replace(" de la mañana ", " am ")
    string = string.replace(" a la madrugada ", " 4hs ")
    string = string.replace(" a la mañana ", " 8hs ")
    string = string.replace(" al mediodia ", " 12hs ")
    string = string.replace(" a la tarde ", " 18hs ")
    string = string.replace(" a la noche ", " 16hs ")

    #Minutos
    string = string.replace(" y media ", " 30' ")
    string = string.replace(" y cuarto ", " 15' ")
    string = string.replace(" a la madrugada ", " 4hs ")
    return string

#Agrega espacios donde falten
def inflar(string):
    def search(expression, string):
        espaciosindexs = []
        for m in re.finditer(expression, string):
            espaciosindexs.append(m.start(1))
            espaciosindexs.append(m.end(1))
        for e in reversed(espaciosindexs):
            string = string[:e] + ' ' + string[e:]
        return string
    string = search("([,:.'])", string)
    string = search("[0-9](am|pm|hs)", string)
    string = search("($)[0-9]", string)
    
    return string

def elimina_tildes(s):
    s = s.replace("á","a")
    s = s.replace("é","e")
    s = s.replace("í","i")
    s = s.replace("ó","o")
    s = s.replace("ú","u")
    return s

#"Ejecutar" horas pm
def pmex(morfo, partes, reportes):
    for i in range(len(partes)):
        if partes[i] == "pm":
            while i > 0:
                i -= 1
                if morfo[i] == "hora":
                    try:
                        partes[i] = str(int(partes[i]) + 12)
                        assert partes[i] in HORAS
                    except:
                        reportes.append("La hora '{0}' no se entiende como hora 'pm'.".format(partes[i]))
                    return

def getparte(partes, index):
    if index < 0:
        return "BEGIN"
    if index >= len(partes):
        return "END"
    else: return partes[index]

#Empacar info
#Retorna una lista de datetimes
def pack(info, reportes):
    retorno = []

    def forain(info, actual, fechai, deltai, porhacer, datetimes):
        mods = info["mod"]
        if porhacer == []:
            if "antes" in mods:
                datetimes.append(fechai - deltai)
            else:
                datetimes.append(fechai + deltai)
            return

        key = porhacer.pop()
        for a in info[key]:
            fecha = fechai
            delta = deltai
            if key == "dsec":
                delta += timedelta(seconds=int(a))
            elif key == "dmin":
                delta += timedelta(minutes=int(a))
            elif key == "dhora":
                delta += timedelta(hours=int(a))
            elif key == "ddia":
                delta += timedelta(days=int(a))
            elif key == "dmes":
                delta += timedelta(days=int(a * 30))
            elif key == "dano":
                delta += timedelta(days=int(a * 365))
            else:
                defecto = False
                if a == "NOW":
                    defecto = True
                    a = get(actual, key)
                elif match("\d+", a):
                    a = int(a)
                elif a in MESDICT:
                    a = MESDICT[a]
                elif a == "hoy":
                    a = actual.day
                elif a == "mañana":
                    a = (actual + timedelta(days = 1)).day
                elif a == "pasado_mañana":
                    a = (actual + timedelta(days = 2)).day
                elif a in DIADICT:
                    weekday = DIADICT[a]
                    fecha += timedelta(days = 1)
                    while fecha.weekday() != weekday:
                        fecha += timedelta(days = 1)
                    a = fecha.day
                else:
                    print("COMPLETAR: " + str(a))
                
                #Todo lo de abajo que tenga NOW ponerlo en 0
                if not defecto:
                    temp = prev(key)
                    while temp != None:
                        if info[temp][0] == "NOW":
                            info[temp] = [str(getfirst(temp))]
                        temp = prev(temp)
                
                #Warning: si ya paso, sumar uno
                if change(fecha, key, a) < actual:
                    fecha = add_one(fecha, next(key))
                    reportes.append("Se cambio de " + next(key))
                fecha = change(fecha, key, a)
            #Luego de haber modificado una caracteristica de la fecha
            #seguir con la siguiente.
            forain(info, actual, fecha, delta, porhacer[:], retorno)
            
    forain(info, datetime.now(), datetime.now(), timedelta(), CATEGORIAS[:], retorno)

    #print "Un pack: " + str(retorno)
    return retorno

def match(expression, string):
    return re.match(expression, string) != None

#Main function
def to_list_of_datetime(text):
    reportes = []

    #Mod 1: lowerear
    text = text.lower()
    #Mod 2: quitar acentos
    text = elimina_tildes(text)
    #Mod 2.3: agregar 2 espacios
    text = " " + text + " "
    #Mod 2.5: cambiar algunas palabras
    text = cambiar(text)
    #Mod 3: juntar
    text = juntar(text)
    #Mod 4: inflar
    text = inflar(text)
    #Mod 5: split
    partes = text.split()

    #Generar morfo
    morfo = []
    for p in partes:
        morfo.append("desc")

    modificado = True
    #Repite hasta que no se deduzca nada nuevo
    while modificado:
        modificado = False
        for i in range(len(partes)):
            p = partes[i]
            m = morfo[i]
            if m != "desc":
                continue
            tipo = "desc"
            ante = getparte(partes, i - 1)
            ante2 = getparte(partes, i - 2)
            desp = getparte(partes, i + 1)
            desp2 = getparte(partes, i + 2)
            anteM = getparte(morfo, i - 1)
            ante2M = getparte(morfo, i - 2)
            despM = getparte(morfo, i + 1)
            desp2M = getparte(morfo, i + 2)
            if p in HORAS and (
                desp in HSAMPM or
                getparte(partes, i + 3) in HSAMPM or
                match("las?", ante)
                ):
                tipo = "hora"
            elif p in MINS and (
                (desp == "'" and desp2 != "'") or
                (ante in ":;y" and ante2M == "hora")
                ):
                tipo = "min"
            elif p in MESDICT:
                tipo = "mes"
            elif p in MESES and ante in "/-":
                tipo = "mes"
            elif match("20\d\d", p) and ante in "/-":
                tipo = "ano"
            elif p in DIAS and desp in "/-":
                #..y ademas no es mes por el elif
                tipo = "dia"
            elif p in DIAS and desp2M == "mes":
                tipo = "dia"
            elif p in DIADICT or p in ["mañana", "pasado_mañana", "hoy"]:
                tipo = "dia"
            elif p[0] in cortapalabras or p == "y":
                tipo = "punto"
            elif match("\d+", p) and match("años?", desp):
                tipo = "dano"
            elif match("\d+", p) and (desp == "mes" or desp == "meses"):
                tipo = "dmes"
            elif match("\d+", p) and match("dias?", desp):
                tipo = "ddia"
            elif match("\d+", p) and match("horas?", desp):
                tipo = "dhora"
            elif match("\d+", p) and (match("minutos?", desp) or desp == "min"):
                tipo = "dmin"
            elif match("\d+", p) and (match("segundos?", desp) or desp == "seg"):
                tipo = "dsec"
            elif p == "antes":
                tipo = "mod"
                
            #Si macheo uno, cambiar
            if tipo != "desc":
                morfo[i] = tipo
                modificado = True

        #Imprimir morfo
        #for i, m in zip(partes, morfo):
        #    print(i + " :- " + m)

    #Ejecutar los pm
    pmex(morfo, partes, reportes)

    #Deduce algunos desc
    morfo = morfo #Terminar

    #Generar info
    retorno = []
    used = dict()
    info = dict()
    categorias = CATEGORIAS + ["mod"]
    #CATEGORIAS.expand(["diadelta", "mesdelta", "horadelta", "mindelta"])
    #CATEGORIAS.expand([])

    for c in categorias:
        info[c] = []
        used[c] = True

    info["dia"] = ["NOW"]
    info["mes"] = ["NOW"]
    info["hora"] = ["NOW"]
    info["min"] = ["NOW"]
    info["sec"] = ["NOW"]

    info["dsec"] = ["0"]
    info["dmin"] = ["0"]
    info["dhora"] = ["0"]
    info["ddia"] = ["0"]
    info["dmes"] = ["0"]
    info["dano"] = ["0"]

    ultimoTipo = ""
    for i in range(len(partes)):
        m = morfo[i]
        p = partes[i]

        if m in info:
            if ultimoTipo == m:
                #Agregar
                info[m].append(p)
            else:
                #Se empieza a dar una posible lista
                #de datos, asi que se debe guardar y fijarse
                #si es hora de actuar con lo que ya se sabe
                if not used[m]:
                    #Si no esta usado el dato, es porque el tipo
                    #ya esta hablando de otra cosa, y por lo tanto
                    #debe hacer lo dicho anteriormente
                    retorno.extend(pack(info, reportes))
                    for k in categorias:
                        used[k] = True
                
                #Puede pisar la info tranquilo
                info[m] = [p,]
                ultimoTipo = m

                #Y ahora pasa a ser no usado
                used[m] = False
    retorno.extend(pack(info, reportes))
    return (retorno, reportes)

if __name__ == "__main__":
    print("Testeo:")
    print(to_list_of_datetime(input("Ingrese un recordatorio en leng. natural: ")))

