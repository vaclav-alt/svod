# SVOD Data Downloader

Jednouchý, částečně konfigurovatelný program sloužící k hromadnému stahování epidemiologických dat ÚZIS ČR prezentovaných na webu SVOD [1].

## Motivace

ÚZIS ČR je ze zákona povinen zveřejňovat sesbíráná epidemiologická data. Ovšem forma, kterou zvolil je poněkud nešťastná, neboť neumožňuje efektivní přístup k většímu množství dat.

Tento program stahuje všechna data dle zadaných kritérií a ukládá je do lokální `sqlite` databáze, která již umožňuje vykonávání běžných operací s většími objemy dat.

## Instalace

Program je napsán v Python 3, stáhnout zdrojové kódy, nainstalovat potřebné balíčky a program je připraven k použití. Prozatím schází `setup.py` a je tedy nutno instalovat všechny prerekvizity ručně. Jendá se o moduly

- `csv`
- `progress`
- `pandas`
- `sqlite3`
- `itertools`

Testováno na systémech Ubuntu 16.10, Ubuntu 18.04, Debian Stretch a Windows 10.

## Použití

Chod programu je řízen dvěma konfiguračními soubory: `config.ini` a `opts.ini`. O nich pojednávají příslušné sekce.

Program se spouští skriptem `download_svod.py` (na Windows dvojklikem).Po spuštění program vytvoří adresář pojmenovaný dle aktuálního data a času (ochrana před nechtěným přemazáním stažených dat). Do toho adresáře zkopíruje vstupní konfigurační soubor `opts.ini`. Stažená data se ukládají do SQLite souboru `data.sqlite` a do CSV souboru `data.csv`.

Pokud v průběhu dojde k "očekávané" chybě (SVOD interface nezobrazí data pro některé konfigurace parametrů, často pozorované pro rozsah od roku 1977), program uloží do souboru `errors.csv` aktuální parametry a odkaz na stránku, ze které měla být data stažena (na té stránce bývá typicky slovy formulované shrnutí zvolených parametrů).

### `config.ini`

Tento soubor slouží ke konfiguraci databáze, konkrétně k pojmenování výsledného souboru, jednotlivých sloupců v databázi a volbě jejich typu. V zásadě zde není nutné nic měnit.

```ini
[database]
sql_filename	=	data.sqlite		# název souboru s uloženými daty
csv_filename	=	data.csv		# název souboru s uloženými daty
eror_filename	=	error.csv		# název souboru s uloženými daty
tablename	=	incmort			# název SQL tabulky

[database.columns]				# pojmenováni sloupců v tabulce
c_gen	=	pohlavi				# pohlaví
c_mkn	=	mkn					# diagnóza
c_vek	=	vek					# věková skupina
c_std	=	stadium				# stádium
c_rgn	=	region				# region, resp. kraj
c_clt	=	t					# tnm klasifikace
c_cln	=	n
c_clm	=	m
c_rok	=	rok					# rok
c_cnd	=	zije				# stav pacienta - žije/nežije
c_dth	=	umrti				# úmrtí na diagnózu
c_inc	=	inc					# incidence
c_mor	=	mort				# mortalita

[database.types]				# datové typy sloupců
c_mkn	=	TEXT
c_vek	=	INTEGER
c_std	=	TEXT
c_rgn	=	TEXT
c_clt	=	TEXT
c_cln	=	TEXT
c_clm	=	TEXT
c_rok	=	INTEGER
c_cnd	=	INTEGER
c_dth	=	INTEGER
c_inc	=	REAL
c_mor	=	REAL
```

### `opts.ini`

V tomto souboru se definují parametry dat, která mají být stažena a je tak ústředním bodem celého programu. Jednotlivé parametry odpovídají volbám v rozhraní na webu SVOD. Níže uvedená konfigurace ukazuje všechny přípustné paramatery (kromě `mkn`). Program potom stáhne data pro všechny (opakuji __všechny__) kombinace těchto parametrů.

Parametry jsou zde zadávány trojím způsobem, který je __nutno__ dodržovat:

- __výčet__: `stadium=X,1,2,3,4` značí, že program postupně stáhne data pro stadium X, 1, 2 atd. Vynechaný výčet, tj. `stadium=`, znamená, že stádium nebude zohledněno a program tak stáhne součty přes všechna stádia (v online rozhraní tomu odpovídá volba "Vše"). Jednotlivé prvky výčtu jsou odděleny čárkami a bez mezer.
- __rozmezí__: sekce s poli `start` a `end`, např. roky. Program postupně projde celé rozmezí s krokem 1, včetně krajních hodnot.
- __diagnózy__: vyžadují zvláštní zacházení. V polích `C` a `D` lze kombinovat výběr a rozmezí, tj. `C=50,30-34,43` odpovídá seznamu diagnóz C50, C30, C31, C32, C33, C34, C43. Některé diagnózy jsou však v rozhraní SVOD sloučeny a je jim přiřazeno označení ve formátu, na který se nelze spolehnout. Ke stažení těchto dat slouží pole `special=C09,C10,C12-C14`, do kterého je nutno vepsat označení tak, jak ho produkuje rozhraní SVOD. V tomto příkladě stáhne program sumární data pro skupinu "ZN jiných částí hltanu"

```ini
[obecne]
pohlavi=m,z
zije=0,1
umrti=0,1
kraje=PHA,STC,JHC,PLK,KVK,ULK,LBK,HKK,PAK,OLK,MSK,JHM,ZLK,VYS
stadium=X,1,2,3,4
[roky]
start=1977
end=2016
[vek]
start=1
end=18
[tnm]
t=0,1,2,3,4,A,S,X
n=0,1,2,3,4,A
m=0,1,X
[mkn]
C=50,30-34,43
D=20
special=C09,C10,C12-C14
```

---

__Jednoduchý příklad__:

```ini
[obecne]
pohlavi=m,z
zije=
umrti=
kraje=PHA,JHC
stadium=
[roky]
start=1990
end=2016
[vek]
start=5
end=18
[tnm]
t=
n=
m=
[mkn]
C=71
D=
special=
```

stáhne program incidenci a mortalitu pro diagnózu C71 - ZN mozku, v letech 1990-2016, s rozlišením pohlaví, od 5. do 18. věkové skupiny, za Prahu a Jihočeský kraj. Data budou součty přes stádia, stav pacienta i tnm klasifikaci.

### Věkové skupiny

Pro konfiguraci používá program stejné kódování věkových skupin jako rozhraní SVOD, tj. 1-18. V databázi ovšem značí věkové skupiny jejich počátečním rokem.

| SVOD | SQL | skupina |
|:---: |:---:|  :---:  |
|  1   |  0  |   0-4   |
|  2   |  5  |   5-9   |
|  3   |  10  |   10-14   |
|  4   |  15  |   15-19   |
|  5   |  20  |   20-24   |
|  6   |  25  |   25-29   |
|  7   |  30  |   30-34   |
|  8   |  35  |   35-39   |
|  9   |  40  |   40-44   |
|  10   |  45  |   45-49   |
|  11   |  50  |   50-54   |
|  12   |  55  |   55-59   |
|  13   |  60  |   60-64   |
|  14   |  65  |   65-69   |
|  15   |  70  |   70-74   |
|  16   |  75  |   75-79   |
|  17   |  80  |   80-84   |
|  18   |  85  |   85-   |

\pagebreak 

## Problémy

Prozatím jsou známy, ale nevyřešeny, následující problémy

- občas program během stahování z neznámých příčin selže. Jde o poměrně vzácný problém, což komplikuje jeho odchycení a nápravu. Většinou stačí program spustit znovu a chyba se pravděpodobně neobjeví.
- program neumí spolehlivě nakládat s chybami v konfiguračních souborech a jejich správnost nekontroluje. Chyba může vést v lepším případě k ukončení běhu programu, v horším případě ke stažení nesmyslných dat.

## Výhled
V nejbližší době lze počítat s následujícími kroky:

- zavedení `setup.py` pro Linux, Mac OS a Windows

## Autor

- Václav Alt, <vaclav.alt@utf.mff.cuni.cz>

## Licence

Program je veden pod licencí MIT License.


## Reference

[1] DUŠEK Ladislav, MUŽÍK Jan, KUBÁSEK Miroslav, KOPTÍKOVÁ Jana, ŽALOUDÍK Jan, VYZULA Rostislav. Epidemiologie zhoubných nádorů v České republice [online]. Masarykova univerzita, [2005], [cit. 2019-3-06]. Dostupný z WWW: [http://www.svod.cz](http://www.svod.cz). Verze 7.0 [2007], ISSN 1802 – 8861.
