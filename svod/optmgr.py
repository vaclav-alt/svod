'''
Copyright [02/2019] Vaclav Alt, vaclav.alt@utf.mff.cuni.cz
'''

from pathlib import Path
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

URLBASE = "http://www.svod.cz/graph/"

BASEOPTS = {
    "sessid": "slr1opn84pssncqr5hekcj6d87",
    "typ": "incmor",
    "zobrazeni": "table",
    "incidence": "1",
    "mortalita": "1",
    "mi": "0",
    "vypocet": "a",
    "lecba": ""
}


def parse_range(s: str) -> list[int]:
    numbers = []
    tokens = s.split(',')

    if s.strip() == "":
        return numbers

    for entry in tokens:
        entry = entry.strip()
        if re.search(r"^\d+-\d+$", entry):
            a, b = entry.split("-")
            for x in range(int(a), int(b) + 1):
                numbers.append(x)
        else:
            numbers.append(int(entry))
    return numbers


def parse_mkn(s, prefix):
    return [f"{prefix}{num:02d}" for num in parse_range(s)]


def collect_mkn(c_inp: str, d_inp: str, spec_inp: str) -> list[str]:
    mkn = []
    mkn += [f"C{num:02d}" for num in parse_range(c_inp)]
    mkn += [f"D{num:02d}" for num in parse_range(d_inp)]
    special = spec_inp

    if special:
        mkn.append(special)

    if not mkn:
        mkn.append("")
    return mkn


urlmap = {
    "c_gen": "pohl",
    "c_mkn": "diag",
    "c_vod": "vek_od",
    "c_vdo": "vek_do",
    "c_std": "stadium",
    "c_rgn": "kraj",
    "c_clt": "t",
    "c_cln": "n",
    "c_clm": "m",
    "c_rok": "rok",
    "c_cnd": "zije",
    "c_dth": "umrti",
    "c_inc": "inc",
    "c_mor": "mort",
    "c_rod": "obdobi_od",
    "c_rdo": "obdobi_do",
}


class OptMaster:
    def __init__(self, filename: str | Path = None):
        if filename is None:
            filename = Path(__file__).parent / "cfg" / "opts.ini"
        self.cfg = configparser.ConfigParser()
        self.cfg.read(filename)

    def load(self):
        a = int(self.cfg["vek"]["start"])
        b = int(self.cfg["vek"]["end"])
        conf = {
            "c_gen": self.cfg["obecne"]["pohlavi"].split(','),
            "c_cnd": self.cfg["obecne"]["zije"].split(','),
            "c_dth": self.cfg["obecne"]["umrti"].split(','),
            "c_rgn": self.cfg["obecne"]["kraje"].split(','),
            "c_std": self.cfg["obecne"]["stadium"].split(','),
            "c_vek": list(range(a, b + 1)),
            "c_clt": self.cfg["tnm"]["t"].split(','),
            "c_cln": self.cfg["tnm"]["n"].split(','),
            "c_clm": self.cfg["tnm"]["m"].split(','),
            "c_mkn": collect_mkn(self.cfg["mkn"]["C"], self.cfg["mkn"]["D"], self.cfg["mkn"]["special"])
        }
        return conf

    def __len__(self):
        return len(list(self.iterator()))

    def url(self, conf: dict):
        return "&".join([URLBASE] + [f"{urlmap[key]}={val}" for key, val in conf.items()])

    def iterator(self):
        conf = self.load()
        d = {
            "c_rod": int(self.cfg["roky"]["start"]),
            "c_rdo": int(self.cfg["roky"]["end"]),
        }
        gen = (
            dict(zip(conf, x))
            for x in product(*conf.values())
        )
        for o in gen:
            od = o.pop("c_vek")
            o["c_vdo"] = od
            o["c_vod"] = od
            yield dict(**o, **d)


