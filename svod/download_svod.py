"""
Copyright [08/2023] Vaclav Alt, vaclav.alt@utf.mff.cuni.cz
"""

import argparse
import configparser
import csv
from datetime import datetime
from io import StringIO
from pathlib import Path
from shutil import copyfile

import pandas as pd
import requests
from bs4 import BeautifulSoup

from svod.optmgr import OptMaster, urlmap, URLBASE, BASEOPTS


def download_year_table(params: dict) -> pd.DataFrame:
    response = requests.get(URLBASE, params=dict(**BASEOPTS, **params))
    if response.status_code != 200:
        raise ConnectionError(response.status_code)

    soup = BeautifulSoup(response.content, 'html.parser')
    tables = pd.read_html(StringIO(str(soup)), encoding='Windows-1250')
    df = tables[0].transpose()
    headers = ["c_rok", "c_int", "c_inc"]

    df1 = pd.DataFrame(df.values[1:, :3], columns=headers)
    df2 = pd.DataFrame(df.values[1:, 4:7], columns=headers)
    table = pd.concat([df1, df2]).reset_index(drop=True)
    table = table.astype({c: int for c in headers})

    return table


def process_table(table: pd.DataFrame) -> list[dict]:
    return table.to_dict('records')


class SvodMaster:
    def __init__(self, filename, optsfile):
        self.cfg = configparser.ConfigParser()
        self.cfg.read(filename)

        self.wd = create_folder()
        copyfile(optsfile, self.wd / "opts.ini")

        self.opt = OptMaster(self.wd / "opts.ini")
        self.opt.load()

    def download(self):
        task_count = len(self.opt)

        had_error = False
        header_done = False

        error_path = self.wd / self.cfg["database"]["error_filename"]
        result_path = self.wd / "results.csv"

        with open(error_path, 'w', newline='') as errfile, \
             open(result_path, "w") as resfile:
            res_out = csv.writer(resfile)
            err_out = csv.writer(errfile)

            for i, opts in enumerate(self.opt.iterator(), start=1):
                if not header_done:
                    header = list(opts.keys())
                    for j in range(len(header)):
                        header[j] = urlmap[header[j]]
                    res_out.writerow(header)
                    header.append("url")
                    err_out.writerow(header)
                    header_done = True

                print("Stahování %d/%d..." % (i, task_count), end='')
                url = self.opt.url(opts)

                try:
                    table = download_year_table({urlmap[key]: val for key, val in opts.items()})
                except:
                    values = list(opts.values())
                    values.append(url)
                    err_out.writerow(values)
                    continue

                records = process_table(table)
                for record in records:
                    tmp = dict(**opts, **record)
                    res_out.writerow(tmp.values())

                print("hotovo")
        if had_error:
            print("Došlo k chybám. Pro konfigurace v errors.csv se nepodařilo stáhnout žádná data.")

        input("Stisknutím klávesy Enter ukončíte chod programu")


def create_folder() -> Path:
    mydir = Path.cwd() / datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    mydir.mkdir()
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
