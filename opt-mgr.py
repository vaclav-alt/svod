#!/usr/bin/python3

import configparser 

class OptMaster:
    def __init__(self, filename="opts.ini"):
        self.cfg = configparser.ConfigParser()
        self.cfg.read(filename)

    def getMkn(self):
        print(self.cfg.options("mkn"))

def main():
    prd = OptMaster()
    prd.getMkn()

if __name__ == "__main__":
    main()

