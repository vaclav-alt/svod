import urllib.request
import chardet

url = 'http://www.svod.cz/graph/?sessid=slr1opn84pssncqr5hekcj6d87&typ=incmor&diag=C50&pohl=z&kraj=&vek_od=10&vek_do=10&zobrazeni=table&incidence=1&mortalita=1&mi=0&vypocet=a&obdobi_od=1978&obdobi_do=2021&stadium=&t=&n=&m=&zije=&umrti=&lecba='

u = chardet.UniversalDetector()
u.feed(urllib.request.urlopen(url).read())

ret = u.close()
print(ret)