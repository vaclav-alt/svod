from svod.download_svod import download_year_table, urlmap
import unittest

sample_table = {
    'c_rok': {0: 1978, 1: 1979, 2: 1980, 3: 1981, 4: 1982, 5: 1983, 6: 1984, 7: 1985, 8: 1986, 9: 1987, 10: 1988,
              11: 1989, 12: 1990, 13: 1991, 14: 1992, 15: 1993, 16: 1994, 17: 1995, 18: 1996, 19: 1997, 20: 1998,
              21: 1999, 22: 2000, 23: 2001, 24: 2002, 25: 2003, 26: 2004, 27: 2005, 28: 2006, 29: 2007, 30: 2008,
              31: 2009, 32: 2010, 33: 2011, 34: 2012, 35: 2013, 36: 2014, 37: 2015, 38: 2016, 39: 2017},
    'c_int': {0: 3, 1: 12, 2: 4, 3: 7, 4: 5, 5: 7, 6: 7, 7: 6, 8: 8, 9: 9, 10: 0, 11: 3, 12: 4, 13: 7, 14: 3, 15: 1,
              16: 4, 17: 8, 18: 2, 19: 7, 20: 7, 21: 6, 22: 6, 23: 5, 24: 12, 25: 9, 26: 13, 27: 7, 28: 10, 29: 9,
              30: 5, 31: 4, 32: 15, 33: 9, 34: 10, 35: 7, 36: 14, 37: 9, 38: 10, 39: 14},
    'c_inc': {0: 0, 1: 2, 2: 1, 3: 3, 4: 4, 5: 4, 6: 8, 7: 4, 8: 3, 9: 0, 10: 6, 11: 2, 12: 1, 13: 2, 14: 1, 15: 4,
              16: 3, 17: 1, 18: 4, 19: 10, 20: 2, 21: 3, 22: 2, 23: 3, 24: 3, 25: 2, 26: 4, 27: 6, 28: 5, 29: 3, 30: 1,
              31: 0, 32: 1, 33: 3, 34: 5, 35: 3, 36: 2, 37: 4, 38: 1, 39: 3}}


class TestDownload(unittest.TestCase):
    def test_download(self):
        conf = {
            "c_gen": "m",
            "c_mkn": "C50",
            "c_vod": "15",
            "c_vdo": "15",
            "c_std": "",
            "c_rgn": "",
            "c_clt": "",
            "c_cln": "",
            "c_clm": "",
            "c_cnd": "",
            "c_dth": "",
            "c_rod": "1978",
            "c_rdo": "2017",

        }
        table = download_year_table({urlmap[key]: val for key, val in conf.items()})
        self.assertDictEqual(table.to_dict(), sample_table)