#!/usr/bin/env python3
'''
Copyright [08/2023] Vaclav Alt, vaclav.alt@utf.mff.cuni.cz
'''

import configparser
import csv
import os
from datetime import datetime
from math import isnan
from shutil import copyfile

import pandas as pd

from svod.optmgr import OptMaster
from db import Database


class SvodMaster:
    def __init__(self, filename):
        self.cfg = configparser.ConfigParser()
        self.cfg.read(filename)

        self.wd = create_folder()
        copyfile("svod/cfg/opts.ini", os.path.join(self.wd, "opts.ini"))
        dbpath = os.path.join(self.wd, self.cfg["database"]["sql_filename"])

        c = {s: dict(self.cfg.items(s)) for s in self.cfg.sections()}
        self.db = Database(dbpath, c, c["database"]["tablename"])

        self.opt = OptMaster()
        self.opt.load()

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

                    self.db.save_to_db(opts)
                self.db.db.commit()

                print("hotovo")
                i += 1
        self.db.write_csv(self.cfg["database"]["csv_filename"])
        if error:
            print("Došlo k chybám. Pro konfigurace v errors.csv se nepodařilo stáhnout žádná data.")

        input("Stisknutím klávesy Enter ukončíte chod programu")


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

    def _parseSingleYearTable(self, tables):
        df = tables[0].transpose()
        df = pd.DataFrame(df.values[1:,4:])
        return (df.values[0,0], df.values[0,1])

    def _downloadYearTable(self, url):
        tables = pd.read_html(url, skiprows=[3,7], encoding='Windows-1252')
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


def create_folder():
    mydir = os.path.join(
        os.getcwd(),
        datetime.now().strftime('%Y-%m-%d_%H-%M-%S'))
    os.makedirs(mydir)
    return mydir


def main():
    svod = SvodMaster("svod/cfg/config.ini")
    svod.download()


if __name__ == "__main__":
    main()
