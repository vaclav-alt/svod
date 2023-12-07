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
import argparse
from pathlib import Path
from bs4 import BeautifulSoup
import requests

import pandas as pd
from io import StringIO
from svod.db import Database
from svod.optmgr import OptMaster, urlmap


def download_year_table(url: str) -> pd.DataFrame:
    response = requests.get(url)
    if response.status_code != 200:
        raise ConnectionError(response.status_code)

    soup = BeautifulSoup(response.content, 'html.parser')
    tables = pd.read_html(StringIO(str(soup)), encoding='Windows-1250')
    df = tables[0].transpose()
    headers = ["c_rok", "c_int", "c_inc"]

    df1 = pd.DataFrame(df.values[1:, :3], columns=headers)
    df2 = pd.DataFrame(df.values[1:, 4:7], columns=headers)

    return pd.concat([df1, df2]).reset_index(drop=True)


def process_table(table: pd.DataFrame) -> list[dict]:
    return table.to_dict('records')


class SvodMaster:
    def __init__(self, filename, optsfile):
        self.cfg = configparser.ConfigParser()
        self.cfg.read(filename)

        self.wd = create_folder()
        copyfile(optsfile, os.path.join(self.wd, "opts.ini"))
        dbpath = os.path.join(self.wd, self.cfg["database"]["sql_filename"])

        c = {s: dict(self.cfg.items(s)) for s in self.cfg.sections()}
        self.db = Database(dbpath, c, c["database"]["tablename"])

        self.opt = OptMaster(os.path.join(self.wd, "opts.ini"))
        self.opt.load()

    def download(self):
        task_count = len(self.opt)
        error = False

        error_path = os.path.join(self.wd, self.cfg["database"]["error_filename"])

        with open(error_path, 'w', newline='') as logfile, \
             open("results.csv", "w") as resfile:
            res_out = csv.writer(resfile)
            for i, opts in enumerate(self.opt.iterator(), start=1):
                print("Stahování %d/%d..." % (i, task_count), end='')
                url = self.opt.url(opts)

                try:
                    table = download_year_table(url)
                except:
                    csv_out = csv.writer(logfile)
                    if not error:
                        header = list(opts.keys())
                        for i in range(len(header)):
                            header[i] = urlmap[header[i]]
                        header.append("url")
                        csv_out.writerow(header)
                        error= True
                    values = list(opts.values())
                    values.append(url)
                    csv_out.writerow(values)
                    continue

                records = process_table(table)
                for record in records:
                    tmp = dict(**opts, **record)
                    res_out.writerow(tmp.values())

                print("hotovo")
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


def create_folder():
    mydir = os.path.join(
        os.getcwd(),
        datetime.now().strftime('%Y-%m-%d_%H-%M-%S'))
    os.makedirs(mydir)
    return mydir


def main():
    parser = argparse.ArgumentParser(prog="SVOD")
    parser.add_argument("--config", default=Path(__file__).parent / "cfg" / "config.ini")
    parser.add_argument("--opts", default=Path(__file__).parent / "cfg" / "opts.ini")
    args = parser.parse_args()
    svod = SvodMaster(args.config, args.opts)
    svod.download()


if __name__ == "__main__":
    main()
