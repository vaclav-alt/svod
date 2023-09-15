#!/usr/bin/python3
'''
Copyright [02/2019] Vaclav Alt, vaclav.alt@utf.mff.cuni.cz
'''

import pandas as pd
import sqlite3 as sq
import csv
import configparser, os, time, sys

from datetime import datetime
from math import isnan
from shutil import copyfile

from optmgr import OptMaster

class SvodMaster:
    def __init__(self, filename):
        self.cfg = configparser.ConfigParser()
        self.cfg.read(filename)

        self.wd = self._createFolder()
        copyfile("opts.ini", os.path.join(self.wd, "opts.ini"))
        dbpath = os.path.join(self.wd, self.cfg["database"]["sql_filename"])

        self._initDb(dbpath)
        
        self.opt = OptMaster()
        self.opt.load()

    def _initDb(self, dbpath):
        self.db = sq.connect(dbpath)
        self.c = self.db.cursor()

        self._createTable()
        self.insertQuery = self._insertQueryTemplate()

    def _createFolder(self):
        mydir = os.path.join(
            os.getcwd(), 
            datetime.now().strftime('%Y-%m-%d_%H-%M-%S'))
        os.makedirs(mydir)
        return mydir

    def download(self):
        task_count = self.opt.getTaskCount()
        error = False

        error_path = os.path.join(self.wd, self.cfg["database"]["error_filename"])
        with open(error_path, 'w', newline='') as logfile:
            i = 1
            for x in self.opt.optIterator():
                print("Stahování %d/%d..." % (i, task_count), end='')
                opts = self.opt._getUrlOpts(x)
                url = self.opt._getUrl(opts)

                try:
                    table = self._downloadYearTable(url)
                except:
                    csv_out = csv.writer(logfile)
                    if not error:
                        header = list(opts.keys())
                        for i in range(len(header)):
                            header[i] = self.opt.opt_names[header[i]]
                        header.append("url")
                        csv_out.writerow(header)
                        error= True
                    values = list(opts.values())
                    values.append(url)
                    csv_out.writerow(values)
                    continue

                self._changeFormats(opts)
                for index, row in table.iterrows():
                    if isnan(row['Rok']):
                        continue
                    opts["c_rok"] = row['Rok']
                    opts["c_inc"] = row['Incidence']
                    opts["c_mor"] = row['Mortalita']

                    self._saveToDb(opts)
                self.db.commit()

                print("hotovo")
                i += 1
        self.writeCsv()
        if error:
            print("Došlo k chybám. Pro konfigurace v errors.csv se nepodařilo stáhnout žádná data.")

        input("Stisknutím klávesy Enter ukončíte chod programu")

    def writeCsv(self):
        csv_path = os.path.join(self.wd, self.cfg["database"]["csv_filename"])
        print("Ukládám %s" % self.cfg["database"]["csv_filename"])

        sql3_cursor = self.db.cursor()
        sql3_cursor.execute('SELECT * FROM %s' % self.cfg["database"]["tablename"])
        with open(csv_path,'w', newline='') as out_csv_file:
            csv_out = csv.writer(out_csv_file)
            csv_out.writerow([d[0] for d in sql3_cursor.description])
            for result in sql3_cursor:
                csv_out.writerow(result)

    def _changeFormats(self, opts):
        opts["c_vek"] = self._vekFormat(opts["c_vek"])
        opts["c_gen"] = self._pohlFormat(opts["c_gen"])

    def _vekFormat(self, i):
        return (int(i) - 1) * 5

    def _pohlFormat(self, pohl):
        if (pohl == "m"):
            return 1
        elif (pohl == "z"):
            return 2
        else:
            return "NULL"

    def _insertQueryTemplate(self):
        query = "insert into %s (" % self.cfg["database"]["tablename"]
        for col in self.cfg.options("database.columns"):
            query += "%s, " % self.cfg["database.columns"][col]
        query = query[:-2]
        query += ") values ("
        for col in self.cfg.options("database.columns"):
            query += "'{%s}', " % col
        query = query[:-2]
        query += ")"
        return query

    def _composeQuery(self, opts):
        for index, val in opts.items():
            if val == '':
                opts[index] = "NULL"
        return (self.insertQuery.format(**opts))

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

        return pd.concat([df1, df2]).reset_index(drop=True)

    def _processTable(self, table):
        for index, row in table.iterrows():
            rowDict = {
                    "rok" : row['Rok'],
                    "incidence" : row['Incidence'],
                    "mortalita" : row['Mortalita']
                    }
            print(rowDict)

def main():
    svod = SvodMaster("config.ini")
    svod.download()
    
if __name__ == "__main__":
    main()
