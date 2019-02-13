#!/usr/bin/python3

import pandas as pd
import sqlite3 as sq
import configparser, os, time
from itertools import product
from progress.bar import IncrementalBar

pohl = [ "m", "z"]
roky = range(1977, 2017)
veky = range(1, 19)
zije = [0, 1]
umrti = [0, 1]
tnm_t = ["0", "1", "2", "3", "4", "A", "S", "X"]
tnm_n = ["0", "1", "2", "3", "4", "X"]
tnm_m = ["0", "1", "X"]
stadia = ["X", "1", "2", "3", "4"]
#kraje = ["PHA", "STC", "JHC", "PLK", "KVK", "ULK", "LBK", "HKK", "PAK", "OLK", "MSK", "JHM", "ZLK", "VYS"]
kraje = ["PHA"]
#mkn = ["C00", "C01", "C02", "C03", "C04", "C05", "C06", "C07", "C08", "C09", "C10", "C11", "C12", "C13", "C14", "C15", "C16", "C17", "C18", "C19", "C20", "C21", "C22", "C23", "C24", "C25", "C26", "C30", "C31", "C32", "C33", "C34", "C37", "C38", "C39", "C40", "C41", "C43", "C44", "C45", "C46", "C47", "C48", "C49", "C50", "C51", "C52", "C53", "C54", "C55", "C56", "C57", "C58", "C60", "C61", "C62", "C63", "C64", "C65", "C66", "C67", "C68", "C69", "C70", "C71", "C72", "C73", "C74", "C75", "C76", "C77", "C78", "C79", "C80", "C81", "C82", "C83", "C84", "C85", "C86", "C88", "C90", "C91", "C92", "C93", "C94", "C95", "C96", "C97", "D03"]
mkn = ["C00"]


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
    "vek_od" : "16",
    "vek_do" : "16",
    "zobrazeni" : "table",
    "incidence" : "1",
    "mortalita" : "1",
    "mi" : "0",
    "vypocet" : "a",
    "obdobi_od" : "2016",
    "obdobi_do" : "2016",
    "stadium" : "",
    "t" : "",
    "n" : "",
    "m" : "",
    "zije" : "",
    "umrti" : "",
    "lecba" : ""
}

class SvodMaster:
    def __init__(self, filename):
        self.cfg = configparser.ConfigParser()
        self.cfg.read(filename)
        self._initDb()

    def _initDb(self):
        dbname = self.cfg["database"]["filename"]
        if (os.path.exists(dbname)):
                os.remove(dbname)
        self.db = sq.connect(dbname)
        self.c = self.db.cursor()

        self._createTable()

    def download(self):
        #bar = IncrementalBar('Downloading', max=self.getTaskCount())
        for x in product(pohl, mkn, veky, stadia, kraje, tnm_t, tnm_n, tnm_m, roky, zije, umrti):
            url = self._getUrl(self._getUrlOpts(x))
            incmort = self._processUrl(url)
            self._saveToDb(x, incmort)
        #    bar.next()
            # break
        #bar.finish()

    def _processUrl(self, url):
        try:
            tables = pd.read_html(url, skiprows=[3,7])
            incmort = self._parseSingleYearTable(tables)
        except:
            incmort = (-1.0, -1.0)
            # print("TED BY TO MELO VRATIT NULL")
        return incmort

    def _createTable(self):
        query = "create table %s (" % self.cfg["database"]["tablename"]
        query += "id INTEGER PRIMARY KEY"
        for col in self.cfg.options("database.columns"):
            query += ", %s %s" % (self.cfg["database.columns"][col], self.cfg["database.types"][col])
        query += ")"
        self.c.execute(query)
        self.db.commit()

    def _saveToDb(self, opts, incmort):
        opts = list(opts)
        opts[2] = vekDb(opts[2])
        opts.extend(list(incmort))
        self.c.execute(sql_query, opts)
        self.db.commit()
        
    def _getUrlOpts(self, c):
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

    def _getUrl(self, options):
        url = "http://www.svod.cz/graph/?"

        suffix = ""
        for (key, value) in options.items():
            suffix += str(key) + "=" + str(value) + "&"
        url += suffix
        return url

    def _parseSingleYearTable(self, tables):
        df = tables[0].transpose()
        df = pd.DataFrame(df.values[1:,4:])
        return (df.values[0,0], df.values[0,1])

    def testOpt(self, opt):
        url = self._getUrl(opt)
        print(url)
        incmort = self._processUrl(url)
        print(incmort)

    def getTaskCount(self):
        return len(pohl) * len(mkn) * len(veky) * len(stadia) * len(kraje) * len(tnm_t) * len(tnm_n) * len(tnm_m) * len(roky) * len(zije) * len(umrti)

def main():
    svod = SvodMaster("config.ini")
    svod.download()
    # svod.testOpt(options)
    
if __name__ == "__main__":
    main()
