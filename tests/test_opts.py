import unittest
import tempfile

from svod.optmgr import OptMaster, parse_range, parse_mkn, collect_mkn

test_cfg = """[obecne]
pohlavi=m,z
zije=
umrti=
kraje=
stadium=X,1,2,3,4
[roky]
start=1978
end=2016
[vek]
start=1
end=2
[tnm]
t=
n=
m=
[mkn]
C=50
D=
special=
"""

range_tests = [
    ("50,30-34,43", [50, 30, 31, 32, 33, 34, 43]),
    ("50", [50]),
    ("1-12", [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]),
    ("10, 20, 30", [10, 20, 30]),
    ("", []),
]


class TestOptMaster(unittest.TestCase):
    def test_parse_range(self):
        for inp, expected in range_tests:
            with self.subTest(inp=inp):
                self.assertListEqual(parse_range(inp), expected)

    def test_parse_mkn(self):
        for inp, expected in range_tests:
            with self.subTest(inp=inp):
                expected = [f"C{num:02d}" for num in expected]
                self.assertListEqual(parse_mkn(inp, "C"), expected)

    def test_collect_mkn(self):
        mkn_tests = [
            (("30,32-34", "50-51,54", "C09,C10,C12-C14"),
             ['C30', 'C32', 'C33', 'C34', 'D50', 'D51', 'D54', 'C09,C10,C12-C14']),
            (("", "50-51,54", "C09,C10,C12-C14"), ['D50', 'D51', 'D54', 'C09,C10,C12-C14']),
            (("30,32-34", "", "C09,C10,C12-C14"), ['C30', 'C32', 'C33', 'C34', 'C09,C10,C12-C14']),
            (("30,32-34", "50-51,54", ""), ['C30', 'C32', 'C33', 'C34', 'D50', 'D51', 'D54']),
            (("", "", ""), [""]),
        ]
        for (c_inp, d_inp, spec_inp), expected in mkn_tests:
            with self.subTest(c_inp=c_inp, d_inp=d_inp, spec_inp=spec_inp):
                self.assertListEqual(collect_mkn(c_inp, d_inp, spec_inp), expected)

    def test_load(self):
        with tempfile.NamedTemporaryFile(mode="wt", delete=False) as fp:
            fp.write(test_cfg)
            fp.close()

            opt = OptMaster(filename=fp.name)
            conf = opt.load()
            url = "www.svod.cz/graph/?sessid=slr1opn84pssncqr5hekcj6d87&typ=incmor&zobrazeni=table&incidence=1&mortalita=1&mi=0&vypocet=a&lecba=&pohl=m&zije=&umrti=&kraj=&stadium=X&t=&n=&m=&diag=C50&vek_do=1&vek_od=1&obdobi_od=1978&obdobi_do=2016"
            for x in opt.iterator(conf):
                self.assertEqual(opt.url(x), url)
                break
