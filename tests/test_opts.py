import unittest

from svod.optmgr import OptMaster, parse_range, parse_mkn

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
