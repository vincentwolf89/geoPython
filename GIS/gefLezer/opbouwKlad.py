import os
import pandas as pd
from itertools import cycle
files = r'C:\Users\Vincent\Desktop\testmap'

soortenGrofGef = ['Z','G']
maxGrof = 1.5
for file in os.listdir(files):
    naam = file.split('.txt')[0]
    ingef = os.path.join(files, file)
    gef = open(ingef, "r")


    lines = (line.rstrip() for line in gef)
    lines = list(line for line in lines if line)  # Non-blank lines in a list


    lijstMetingen = []


    for item in lines:
        if item.startswith('#'):
            if item.startswith('#COLUMNSEP'):
                sep = sep = item.strip()[-1:]
            else:
                pass
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

    del bovenkant, onderkant,soort

    # print indexLijst

    # opbouw pandas df
    dict = {'index': indexLijst,'bovenkant': bovenkantLijst, 'onderkant': onderkantLijst, 'soort': soortenLijst}
    df = pd.DataFrame(dict)
    df['soortOnder'] = df['soort'].shift(-1)
    df['onderkantOnder'] = df['onderkant'].shift(1)
    df['laagDikte'] = abs(df['bovenkant']-df['onderkant'])
    df['indexOnder'] = df['index'].shift(-1)
    df['indexDif'] = abs(df['index'] - df['indexOnder'])

    for index, row in df.iterrows():

        soort = df.iloc[index]['soort']
        laagDikte = df.iloc[index]['laagDikte']
        if soort in soortenGrofGef:
            condition = True
            groveLaag+= laagDikte

        if soort not in soortenGrofGef:
            grovelaagNummer += 1
            condition = False
            groveLaag = 0

        dct[grovelaagNummer] = groveLaag, index
    for i in dct:

        if dct[i][0] is 0:
            pass
        else:
            laag = dct[i][0]
            loc = dct[i][1]
            if laag > maxGrof:
                print loc, laag
                break







    # row_iterator = df.iterrows()
    # _, last = row_iterator.next()  # take first item from row_iterator
    # for i, row in row_iterator:
    #     # print(row['soort'])
    #     print(last['bovenkant']), i, last['onderkant']
    #     last = row

    # # print df
    # for index, row in df.iterrows():
    #
    #     # vervang laatste NaN soortwaarde
    #     if pd.isna(row['soortOnder']):
    #         value = row['soort']
    #         # df.set_value(index,'soortOnder', value)
    #         df.at[index,'soortOnder']= value
    #
    #     # if pd.isna(row['indexOnder']):
    #     #     value = row['index']+1
    #     #     df.at[index, 'indexOnder'] = value
    #
    #     # huidige regel
    #     soort = df.iloc[index]['soort']
    #     soortV = df.iloc[index]['soortOnder']
    #     bovenkant = df.iloc[index]['bovenkant']
    #     onderkant = df.iloc[index]['onderkant']
    #     laagDikte = df.iloc[index]['laagDikte']
    #
    #
    #     if soort in soortenGrofGef:
    #         groveLaag+= laagDikte
    #         indexLijstGrof.append(index)
    #         print groveLaag
    #
    #
    #     elif soortV not in soortenGrofGef:
    #         groveLaag = 0
    #
    # print groveLaag


    #     if soort in soortenGrofGef:
    #         groveLaag+= laagDikte
    #         dct[grovelaagNummer] = groveLaag
    #
    #
    #     elif soort not in soortenGrofGef:
    #
    #         groveLaag = 0
    #         indexLijstGrof = []
    #
    #
    # print dct


    #
    #     if soort in soortenGrofGef and laagDikte > maxGrof:
    #         groveLaag = laagDikte
    #         print laagDikte
    #         topzandIndex = index
    #         topzand = df.iloc[index-1]['bovenkant']
    #         break
    #
    #     elif soort in soortenGrofGef and soortV in soortenGrofGef:
    #         groveLaag+= laagDikte
    #         indexLijstGrof.append(float(index))
    #
    #     else:
    #         groveLaag = 0
    #         indexLijstGrof = []
    #
    # if groveLaag is not 0 and groveLaag > maxGrof:
    #     try:
    #         topzandIndex
    #         print "Grove laag met laagdikte groter dan toegestaan gevonden, topzand: {}m".format(topzand)
    #     except NameError:
    #         topzandIndex = int(min(indexLijstGrof))
    #         topzand = df.iloc[topzandIndex]['bovenkant']
    #         print "Aaneengesloten grove lagen met laagdikte groter dan toegestaan gevonden, topzand: {}m".format(topzand), indexLijstGrof
    #
    # else:
    #     print "Geen grove laag gevonden groter dan {}m".format(maxGrof)
    #
    # print df