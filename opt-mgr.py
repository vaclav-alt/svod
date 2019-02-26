#!/usr/bin/python3
'''
Copyright [02/2019] Vaclav Alt, vaclav.alt@mff.cuni.cz
'''

import configparser 
import re
from itertools import product

'''
pohl = [ "m", "z"]
veky = range(1, 19)
zije = [0, 1]
umrti = [0, 1]
tnm_t = ["0", "1", "2", "3", "4", "A", "S", "X"]
tnm_n = ["0", "1", "2", "3", "4", "X"]
tnm_m = ["0", "1", "X"]
stadia = ["X", "1", "2", "3", "4"]
kraje = ["PHA", "STC", "JHC", "PLK", "KVK", "ULK", "LBK", "HKK", "PAK", "OLK", "MSK", "JHM", "ZLK", "VYS"]
mkn = ["C01"]
'''

class OptMaster:
    def __init__(self, filename="opts.ini"):
        self.cfg = configparser.ConfigParser()
        self.cfg.read(filename)

        # obecne
        self.pohlavi = []
        self.zije = []
        self.umrti = []
        self.kraje = []
        self.stadium = []
        self.mkn = []

        # roky
        self.yearStart = 0
        self.yearEnd = 0

        # vek
        self.vek = []

        # tnm
        self.t = []
        self.n = []
        self.m = []

    def load(self):
        self.pohlavi.extend(self.cfg["obecne"]["pohlavi"].split(','))
        self.zije.extend(self.cfg["obecne"]["zije"].split(','))
        self.umrti.extend(self.cfg["obecne"]["umrti"].split(','))
        self.kraje.extend(self.cfg["obecne"]["kraje"].split(','))
        self.stadium.extend(self.cfg["obecne"]["stadium"].split(','))

        self.yearStart = int(self.cfg["roky"]["start"])
        self.yearEnd = int(self.cfg["roky"]["end"])

        a = int(self.cfg["vek"]["start"])
        b = int(self.cfg["vek"]["end"])
        self.vek = list(range(a, b+1))

        self.t.extend(self.cfg["tnm"]["t"].split(','))
        self.n.extend(self.cfg["tnm"]["n"].split(','))
        self.m.extend(self.cfg["tnm"]["m"].split(','))

        self.mkn = self._collectMkn()

    def optIterator(self):
        return product(self.pohlavi,
                    self.mkn,
                    self.vek,
                    self.stadium,
                    self.kraje,
                    self.t,
                    self.n,
                    self.m,
                    self.zije,
                    self.umrti)

    def getTaskCount(self):
        return len(self.pohlavi) * \
                    len(self.mkn) * \
                    len(self.vek) * \
                    len(self.stadium) * \
                    len(self.kraje) * \
                    len(self.t) * \
                    len(self.n) * \
                    len(self.m) * \
                    len(self.zije) * \
                    len(self.umrti) 


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
            "obdobi_od" : self.yearStart,
            "obdobi_do" : self.yearEnd,
            "stadium" : c[3],
            "t" : c[5],
            "n" : c[6],
            "m" : c[7],
            "zije" : c[8],
            "umrti" : c[9],
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

    def _parseRange(self, s):
        mkn = []
        for d in s.split(','):
            if re.search("\d+[-]{1}\d+", d):
                a = int(re.search("^\d+", d).group(0))
                b = int(re.search("\d+$", d).group(0))
                for x in range(a,b+1):
                    mkn.append(x)
            else:
                mkn.append(d)
        return mkn

    def _parseMkn(self, s, pref):
        mkn = []
        if s == "":
            return mkn
        for x in self._parseRange(s):
            mkn.append(pref + str(x))
        return mkn

    def _collectMkn(self):
        mkn = []
        mkn.extend(self._parseMkn(self.cfg["mkn"]["C"], 'C'))
        mkn.extend(self._parseMkn(self.cfg["mkn"]["D"], 'D'))
        special = self.cfg["mkn"]["special"]
        if special != "":
            mkn.append(special)
        if mkn == []:
            mkn.append("")
        return mkn
        
def main():
    opt = OptMaster()
    opt.load()
    for o in opt.optIterator():
        dic = opt._getUrlOpts(o)
        print(opt._getUrl(dic))


if __name__ == "__main__":
    main()

