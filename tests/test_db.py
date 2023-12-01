import configparser
from svod.db import Database


def main():
    cfg = configparser.ConfigParser()
    cfg.read("config.ini")

    c = {s: dict(cfg.items(s)) for s in cfg.sections()}

    db = Database(":memory:", c)
    print(db.insertQuery)


if __name__ == "__main__":
    main()
