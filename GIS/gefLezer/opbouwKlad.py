import os
import pandas as pd
from itertools import cycle
files = r'C:\Users\Vincent\Desktop\testmap'

soortenGrofGef = ['Z','G']
maxGrof = 2
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




    deklaag = 0
    groveLaag = 0
    indexLijstGrof = []


    bovenkantLijst = []
    onderkantLijst = []
    soortenLijst = []

    for item in lijstMetingen:
        onderdelen = item.split(sep)
        bovenkant = float(onderdelen[0])
        onderkant = float(onderdelen[1])
        soort = (onderdelen[2])[1]

        bovenkantLijst.append(bovenkant)
        onderkantLijst.append(onderkant)
        soortenLijst.append(soort)

    del bovenkant, onderkant,soort


    # opbouw pandas df
    dict = {'bovenkant': bovenkantLijst, 'onderkant': onderkantLijst, 'soort': soortenLijst}
    df = pd.DataFrame(dict)
    df['soortOnder'] = df['soort'].shift(-1)
    df['onderkantOnder'] = df['onderkant'].shift(1)
    df['laagDikte'] = abs(df['bovenkant']-df['onderkant'])


    # print df
    for index, row in df.iterrows():

        # vervang laatste NaN soortwaarde
        if pd.isna(row['soortOnder']):
            value = row['soort']
            # df.set_value(index,'soortOnder', value)
            df.at[index,'soortOnder']= value



        # huidige regel
        soort = df.iloc[index]['soort']
        soortV = df.iloc[index]['soortOnder']
        bovenkant = df.iloc[index]['bovenkant']
        onderkant = df.iloc[index]['onderkant']
        laagDikte = df.iloc[index]['laagDikte']




        # if soort in soortenGrofGef and soortV in soortenGrofGef:
        #     if groveLaag+laagDikte <= maxGrof:
        #         indexLijstGrof.append(index)
        #         groveLaag += laagDikte
        #         dekLaag = onderkant
        #
        # if groveLaag <

        if soort in soortenGrofGef and soortV in soortenGrofGef:
            groveLaag+= laagDikte
            indexLijstGrof.append(float(index))

    if groveLaag > maxGrof:
        print groveLaag, indexLijstGrof
        topzandIndex = int(min(indexLijstGrof))
        print df.iloc[topzandIndex]['bovenkant']

