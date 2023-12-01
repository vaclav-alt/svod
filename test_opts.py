import tomli

with open("opts_test.ini", "rb") as f:
    data = tomli.load(f)
    print(data)
