import arcpy
import matplotlib.pyplot as plt 
import pandas as pd
import numpy as np


arcpy.env.workspace = r'D:\Projecten\WW\test.gdb'
arcpy.env.overwriteOutput = True
profielen = r"D:\Projecten\WW\test.gdb\punten_profielen_z"

buitenMax = -50
binnenMax = 50
# min_voorland = -25
# max_achterland = 75
# min_achterland = 25

### AANTEKENINGEN ###
# koppeling gemaakt met bgt waterlopen, profielen afgesneden indien ze kruisen met een waterloop

array = arcpy.da.FeatureClassToNumPyArray(profielen, ('OBJECTID','profielnummer','dijktraject', 'afstand', 'z_ahn','BGTPlusType'))
df = pd.DataFrame(array)
# df = df.dropna()
sorted = df.sort_values(['profielnummer', 'afstand'], ascending=[True, True])
grouped = sorted.groupby('profielnummer')

for name, group in grouped:

    

    # maximale hoogte
    max_kruin = max(group['z_ahn'])
    afstand = group['afstand']
    
    # buitenkant afsnijden
    group = group.mask(afstand < buitenMax)
    group = group.dropna()

    # binnenkant afsnijden
    group = group.mask(afstand > binnenMax)
    group = group.dropna()


    
    landzijde = group.sort_values(['afstand'], ascending=False) #afnemend, landzijde
    rivierzijde = group.sort_values(['afstand'], ascending=True) #toenemend, rivierzijde

    for index, row in rivierzijde.iterrows():
        soortWaarde = (str(row['BGTPlusType']))

        if soortWaarde == "None":
            pass
        elif soortWaarde is not "None" and row['afstand'] > 0:
            
            group = group.mask(afstand >= row['afstand'])
            pointsLand = group.dropna()
            break
    
    for index, row in landzijde.iterrows():
        soortWaarde = (str(row['BGTPlusType']))

        if soortWaarde == "None":
            pass
        elif soortWaarde is not "None" and row['afstand'] < 0:
            
            group = group.mask(afstand <= row['afstand'])
            group = group.dropna()
        
            break
    # gemiddelde maaiveldhoogte voor en achterland
    voorland = group.mask(group['afstand'] < 0)
    voorland = voorland.dropna()
    minVoorland = min(voorland['z_ahn'])

    achterland = group.mask(group['afstand'] > 0)
    achterland = achterland.dropna()
    minAchterland = min(achterland['z_ahn'])





    # but
    landzijde = group.sort_values(['afstand'], ascending=False)
    verschilLijst = []
    for index, row in landzijde.iterrows():
        afstand = row['afstand']
        hoogte = row['z_ahn']

        verschilLijst.append(abs(hoogte-minVoorland))
    
    minVerschil = min(verschilLijst)
    maxVerschil = max(verschilLijst)
    
    # zoek naar geldige waarde voor maximaal verschil
    waarde = 0.4
    

    for index, row in landzijde.iterrows():
        afstand = row['afstand']
        hoogte = row['z_ahn']
        verschil = abs(hoogte-minVoorland)

        if afstand < 0 and verschil < waarde:
            but = afstand
            print afstand, "poging 1", name
            plt.plot(afstand, hoogte, 'ro', markersize=6)
            break
        else:
            but = None

    while but is None:
        waarde +=0.1
        for index, row in landzijde.iterrows():
            afstand = row['afstand']
            hoogte = row['z_ahn']
            verschil = abs(hoogte-minVoorland)

            if afstand < 0 and verschil < waarde:
                but = afstand
                print afstand, "poging 2", name
                plt.plot(afstand, hoogte, 'ro', markersize=6)
                break
            else:
                but = None

    # bit
    rivierzijde = group.sort_values(['afstand'], ascending=True)
    verschilLijst = []
    for index, row in rivierzijde.iterrows():
        afstand = row['afstand']
        hoogte = row['z_ahn']

        verschilLijst.append(abs(hoogte-minAchterland))
    
    minVerschil = min(verschilLijst)
    maxVerschil = max(verschilLijst)
    
    # zoek naar geldige waarde voor maximaal verschil
    waarde = 0.2
    

    for index, row in rivierzijde.iterrows():
        afstand = row['afstand']
        hoogte = row['z_ahn']
        verschil = abs(hoogte-minAchterland)

        if afstand > 0 and verschil < waarde:
            bit = afstand
            print afstand, "poging 1", name
            plt.plot(afstand, hoogte, 'ro', markersize=6)
            break
        else:
            bit = None

    while bit is None:
        waarde +=0.1
        for index, row in landzijde.iterrows():
            afstand = row['afstand']
            hoogte = row['z_ahn']
            verschil = abs(hoogte-minVoorland)

            if afstand > 0 and verschil < waarde:
                bit = afstand
                print afstand, "poging 2", name
                plt.plot(afstand, hoogte, 'ro', markersize=6)
                break
            else:
                bit = None


        
    
    plt.plot(group['afstand'],group['z_ahn'])
    plt.show()



