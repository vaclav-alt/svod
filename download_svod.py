#!/usr/bin/python3

import pandas as pd
import sqlite3 as sq
from itertools import product

pohl = [ "m", "z"]
roky = range(1977, 2017)
veky = range(1, 19)
zije = [0, 1]
umrti = [0, 1]
tnm_t = ["0", "1", "2", "3", "4", "A", "S", "X"]
tnm_n = ["0", "1", "2", "3", "4", "X"]
tnm_m = ["0", "1", "X"]
stadia = ["X", "1", "2", "3", "4"]
kraje = ["PHA", "STC", "JHC", "PLK", "KVK", "ULK", "LBK", "HKK", "PAK", "OLK", "MSK", "JHM", "ZLK", "VYS"]
mkn = ["C00", "C01", "C02", "C03", "C04", "C05", "C06", "C07", "C08", "C09", "C10", "C11", "C12", "C13", "C14", "C15", "C16", "C17", "C18", "C19", "C20", "C21", "C22", "C23", "C24", "C25", "C26", "C30", "C31", "C32", "C33", "C34", "C37", "C38", "C39", "C40", "C41", "C43", "C44", "C45", "C46", "C47", "C48", "C49", "C50", "C51", "C52", "C53", "C54", "C55", "C56", "C57", "C58", "C60", "C61", "C62", "C63", "C64", "C65", "C66", "C67", "C68", "C69", "C70", "C71", "C72", "C73", "C74", "C75", "C76", "C77", "C78", "C79", "C80", "C81", "C82", "C83", "C84", "C85", "C86", "C88", "C90", "C91", "C92", "C93", "C94", "C95", "C96", "C97", "D03"]


sql_query = '''insert into incmort (pohlavi, mkn, vek, stadium, region, t, n, m, rok, zije, umrti, inc, mort) values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)'''

def vekDb(i):
    k = (i - 1)*5
    return "v_%d" % k

options = {
    "sessid" : "slr1opn84pssncqr5hekcj6d87",
    "typ" : "incmor",
    "diag" : "C53",
    "pohl" : "z",
    "kraj" : "",
    "vek_od" : "1",
    "vek_do" : "1",
    "zobrazeni" : "table",
    "incidence" : "1",
    "mortalita" : "1",
    "mi" : "0",
    "vypocet" : "w",
    "obdobi_od" : "1977",
    "obdobi_do" : "1977",
    "stadium" : "",
    "t" : "",
    "n" : "",
    "m" : "",
    "zije" : "",
    "umrti" : "",
    "lecba" : ""
}

def getUrlOpts(c):
    opts = {
        "sessid" : "slr1opn84pssncqr5hekcj6d87",
        "typ" : "incmor",
        "diag" : c[1],
        "pohl" : c[0],
        "kraj" : c[4],
        "vek_od" : c[2],
        "vek_do" : c[2],
        "zobrazeni" : "table",
        "incidence" : "1",
        "mortalita" : "1",
        "mi" : "0",
        "vypocet" : "a",
        "obdobi_od" : c[8],
        "obdobi_do" : c[8],
        "stadium" : c[3],
        "t" : c[5],
        "n" : c[6],
        "m" : c[7],
        "zije" : c[9],
        "umrti" : c[10],
        "lecba" : ""
    }
    return opts

def getUrl(options):
    url = "http://www.svod.cz/graph/?"

    suffix = ""
    for (key, value) in options.items():
        suffix += key + "=" + value + "&"
    url += suffix
    return url

def parseSingleYearTable(tables):
    df = tables[0].transpose()
    # headers = df.iloc[0,:3]
    df = pd.DataFrame(df.values[1:,4:])
    return (df.values[0,0], df.values[0,1])

def main():
    try:
        tables = pd.read_html(getUrl(options), skiprows=[3,7])
        incmort = parseSingleYearTable(tables)
    except:
        incmort = (0.0, 0.0)
        print("ANI HOVNO")
    print("incidence: %.2f\tmortalita: %.2f" % incmort)

# sql_query = '''insert into incmort (pohlavi, mkn, vek, stadium, region, t, n, m, rok, zije, umrti, inc, mort) values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)'''
    for x in product(pohl, mkn, veky, stadia, kraje, tnm_t, tnm_n, tnm_m, roky, zije, umrti):
        print(getUrl(getUrlOpts(x)))
        combo = list(x)
        combo[2] = vekDb(combo[2])
        print(combo) 
        break

# db = sq.connect("svod.sqlite")
# cursor  = db.cursor()
# cursor.execute(sql_query, (pohl[0], vekDb(10), stadia[0], kraje[1], "", "", "", 1989, "1", "0", 0.45, 0.34))
# db.commit()
if __name__ == "__main__":
    main()
