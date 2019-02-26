#!/usr/bin/python3

import pandas as pd
import sqlite3 as sq
import configparser, os, time
from progress.bar import IncrementalBar
from math import isnan
import sys

from optmgr import OptMaster

def vekDb(i):
    k = (int(i) - 1)*5
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
    "obdobi_od" : "1977",
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
        self.opt = OptMaster()
        
        self.opt.load()

    def _initDb(self):
        dbname = self.cfg["database"]["filename"]
        if (os.path.exists(dbname)):
                os.remove(dbname)
        self.db = sq.connect(dbname)
        self.c = self.db.cursor()

        self._createTable()

    def download(self):
        bar = IncrementalBar('Downloading', max=self.opt.getTaskCount())
        for x in self.opt.optIterator():
            opts = self.opt._getUrlOpts(x)
            url = self.opt._getUrl(opts)
            #print(url)
            table = self._downloadYearTable(url)
            # try:
            #     table = self._downloadYearTable(url)
            # except Exception as e:
            #     print(sys.exc_info())
            #     print("Error at url %s\n" % url)
            #     print(str(e))
            #     print(table)
            #     bar.next()
            #     continue
            opts["vek_od"] = vekDb(opts["vek_od"])
            opts["vek_do"] = vekDb(opts["vek_do"])
            for index, row in table.iterrows():
                if isnan(row['Rok']):
                    continue
                opts["rok"] = row['Rok']
                opts["incidence"] = row['Incidence']
                opts["mortalita"] = row['Mortalita']

                self._saveToDb(opts)
            self.db.commit()

            bar.next()
            break
        bar.finish()

    def _composeQuery(self, opts):
        for index, val in opts.items():
            if val == '':
                opts[index] = "NULL"
        sql_query = '''insert into incmort (pohlavi, mkn, vek, stadium, region, t, n, m, rok, zije, umrti, inc, mort) values ('{pohl}', '{diag}', '{vek_do}', '{stadium}', '{kraj}', '{t}', '{n}', '{m}', '{rok}', '{zije}', '{umrti}', '{incidence}', '{mortalita}')'''
        return (sql_query.format(**opts))

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

    def _saveToDb(self, opts):
        sql_query = self._composeQuery(opts)
        self.c.execute(sql_query)

    def _parseSingleYearTable(self, tables):
        df = tables[0].transpose()
        df = pd.DataFrame(df.values[1:,4:])
        return (df.values[0,0], df.values[0,1])

    def _downloadYearTable(self, url):
        tables = pd.read_html(url, skiprows=[3,7])
        df = tables[0].transpose()
        headers = df.iloc[0,:3]

        df1 = pd.DataFrame(df.values[1:,:3], columns=headers)
        df2 = pd.DataFrame(df.values[1:,3:], columns=headers)

        df = df1.append(df2).reset_index(drop=True)
        return df

    def _processTable(self, table):
        for index, row in table.iterrows():
            rowDict = {
                    "rok" : row['Rok'],
                    "incidence" : row['Incidence'],
                    "mortalita" : row['Mortalita']
                    }
            print(rowDict)

    def testOpt(self, opts):
        url = self._getUrl(opts)
        print(url)
        table = self._downloadYearTable(url)
        opts["vek_od"] = vekDb(opts["vek_od"])
        opts["vek_do"] = vekDb(opts["vek_do"])
        for index, row in table.iterrows():
            opts["rok"] = row['Rok']
            opts["incidence"] = row['Incidence']
            opts["mortalita"] = row['Mortalita']

            self._saveToDb(opts)

def main():
    svod = SvodMaster("config.ini")
    svod.download()
    #svod.testOpt(options)
    
if __name__ == "__main__":
    main()
