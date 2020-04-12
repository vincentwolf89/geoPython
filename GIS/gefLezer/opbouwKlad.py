import os
import pandas as pd
from itertools import cycle
files = r'C:\Users\Vincent\Desktop\testmapBoringen'

soortenGrofGef = ['Z','G']
maxGrof = 5
for file in os.listdir(files):
    naam = file.split('.txt')[0]
    ingef = os.path.join(files, file)
    gef = open(ingef, "r")

    # remove blank lines
    lines = (line.rstrip() for line in gef)
    lines = list(line for line in lines if line)

    # lijst voor meetgedeelte
    lijstMetingen = []

    # ophalen benodigde data
    for item in lines:

        if item.startswith('#'):
            # bepalen separator
            if item.startswith('#COLUMNSEP'):
                sep = sep = item.strip()[-1:]

            # ophalen locatiegegevens
            if item.startswith('#XYID'):
                coLocs = item.split(',')
                x = float(coLocs[1])
                y = float(coLocs[2])

            if item.startswith('#ZID'):
                zMv = float(item.split(',')[1])

        else:
            lijstMetingen.append(item)



    index = 0
    deklaag = 0
    groveLaag = 0
    indexLijst = []
    indexLijstGrof = []
    grovelaagNummer = 0


    bovenkantLijst = []
    onderkantLijst = []
    soortenLijst = []

    dct = {}

    for item in lijstMetingen:
        onderdelen = item.split(sep)
        bovenkant = float(onderdelen[0])
        onderkant = float(onderdelen[1])
        soort = (onderdelen[2])[1]

        indexLijst.append(index)
        bovenkantLijst.append(bovenkant)
        onderkantLijst.append(onderkant)
        soortenLijst.append(soort)
        index+=1

    del bovenkant, onderkant,soort, index



    # opbouw pandas df
    dict = {'index': indexLijst,'bovenkant': bovenkantLijst, 'onderkant': onderkantLijst, 'soort': soortenLijst}
    df = pd.DataFrame(dict)
    df['laagDikte'] = abs(df['bovenkant']-df['onderkant'])

    testdct = {}

    indexlijstGrof = []
    laagNummerLijstGrof = []
    bovenkantLijstGrof = []
    laagdikteLijstGrof = []
    for index, row in df.iterrows():
        bovenkant = df.iloc[index]['bovenkant']
        onderkant = df.iloc[index]['onderkant']
        soort = df.iloc[index]['soort']
        laagDikte = df.iloc[index]['laagDikte']


        if soort in soortenGrofGef:
            indexLijstGrof.append(index)
            groveLaag+= laagDikte

            # testdct[index] = grovelaagNummer, bovenkant
            # indexLijstGrof.append(index)
            laagNummerLijstGrof.append(grovelaagNummer)
            bovenkantLijstGrof.append(bovenkant)
            laagdikteLijstGrof.append(groveLaag)

        if soort not in soortenGrofGef:
            grovelaagNummer += 1
            groveLaag = 0




        # dct[grovelaagNummer] = groveLaag, grovelaagNummer, bovenkant


    testdct = {'index': indexLijstGrof,'laagNummer': laagNummerLijstGrof, 'bovenkant': bovenkantLijstGrof,'laagdikte':laagdikteLijstGrof}
    testdf = pd.DataFrame(testdct)


    # print testdf

    grouped = testdf.groupby('laagNummer')

    for group in grouped:
        if group[1]['laagdikte'].max() > maxGrof:
            print group[1]['laagdikte'].max(), group[1]['bovenkant'].min()
            begrenzing = True
            break
        else:
            begrenzing = False

    print begrenzing, file






