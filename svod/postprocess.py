
def vek_format(i):
    return (int(i) - 1) * 5


def pohlavi_format(pohl):
    if pohl == "m":
        return 1
    elif pohl == "z":
        return 2
    else:
        return "NULL"

