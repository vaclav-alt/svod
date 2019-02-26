#!/usr/bin/python3

import pandas as pd
import sqlite3 as sq
import configparser, os, time
from itertools import product
from progress.bar import IncrementalBar

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
    # TODO(vaclav): SvodMaster should iterate over URLs, which should be handled only by optmgr

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
        i = 1
        # bar = IncrementalBar('Downloading', max=100)
        bar = IncrementalBar('Downloading', max=self.getTaskCount())
        for x in product(pohl, mkn, veky, stadia, kraje, tnm_t, tnm_n, tnm_m, roky, zije, umrti):
            url = self._getUrl(self._getUrlOpts(x))
            incmort = self._processUrl(url)
            self._saveToDb(x, incmort)

            bar.next()

            if (i % 100) == 0:
                self.db.commit()
            i += 1
        bar.finish()

    def _processUrl(self, url):
        try:
            tables = pd.read_html(url, skiprows=[3,7])
            incmort = self._parseSingleYearTable(tables)
        except:
            incmort = (None, None)
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
        
    # TODO(vaclav): move to opt-mgr
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

    # TODO(vaclav): move to opt-mgr
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

    # TODO(vaclav): move to opt-mgr
    def getTaskCount(self):
        return len(pohl) * len(mkn) * len(veky) * len(stadia) * len(kraje) * len(tnm_t) * len(tnm_n) * len(tnm_m) * len(roky) * len(zije) * len(umrti)

def main():
    svod = SvodMaster("config.ini")
    svod.download()
    #svod.testOpt(options)
    
if __name__ == "__main__":
    main()
