#!/usr/bin/python3

import configparser 
import re

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

        self.mkn.extend(self._parseMkn(self.cfg["mkn"]["C"], 'C'))
        self.mkn.extend(self._parseMkn(self.cfg["mkn"]["D"], 'D'))
        self.mkn.append(self.cfg["mkn"]["special"])

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
        for x in self._parseRange(s):
            mkn.append(pref + str(x))
        return mkn


def main():
    opt = OptMaster()
    opt.load()
    print(opt.pohlavi)
    print(opt.zije)
    print(opt.umrti)
    print(opt.kraje)
    print(opt.stadium)
    print(opt.yearStart)
    print(opt.yearEnd)
    print(opt.vek)
    print(opt.t)
    print(opt.n)
    print(opt.m)
    print(opt.mkn)


if __name__ == "__main__":
    main()

