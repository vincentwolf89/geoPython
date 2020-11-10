import arcpy
from arcpy.sa import *
sys.path.append('.')
import pandas as pd
import math
from itertools import groupby
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as plticker
from matplotlib.ticker import MaxNLocator
import matplotlib

from basisfuncties import average, locate_existing_points,copy_trajectory_lr
arcpy.env.workspace = r"D:\Projecten\WSRL\safe\hoekenPrio.gdb"


arcpy.env.overwriteOutput = True

dijkpalen = r'D:\GoogleDrive\WSRL\safe_basis.gdb\dijkpalen_safe'
trajectlijn = r'D:\GoogleDrive\WSRL\safe_basis.gdb\buitenkruinlijn_safe_wsrl'
code = 'traject'
profielen = 'profielenPriovakken'
puntenZ = 'hoekPuntenAfstandZ'
puntenZClean = 'hoekPuntenAfstandZClean'
velden_profielen = ['OBJECTID', 'SHAPE', 'SHAPE_Length','Shape','Shape_Length',code,'profielnummer','Vaknaam_2020','afstand','z_ahn']
velden_uitvoer = ['Vaknaam_2020','z_ahn','afstand','profielnummer','soort']

figure = r'C:\Users\Vincent\Desktop\hoekenPriovakken.png'

## functies
# copy_trajectory_lr(trajectlijn,code,10)
#locate_existing_points(profielen,puntenZ,velden_profielen,trajectlijn,code,velden_uitvoer)


# filterpoints
def filterPoints(puntenZ, puntenZClean, velden_uitvoer):

    arcpy.CopyFeatures_management(puntenZ, puntenZClean)
    filterCursor = arcpy.da.UpdateCursor(puntenZClean, velden_uitvoer)

    # zoek bermen 
    listBerm = []

    for k, g in groupby(filterCursor, lambda x: x[3]):

       

        for row in g:
            if row[4] =='insteekberm':
                listBerm.append(int(k))
    
    del filterCursor


    deleteCursor = arcpy.da.UpdateCursor(puntenZClean, velden_uitvoer)
    for k, g in groupby(deleteCursor, lambda x: x[3]):

        for row in g:
            if (row[4] =='bit' and int(k) in listBerm):
                deleteCursor.deleteRow()
            else:
                pass
    
    del deleteCursor


            
            

def calculateAngle(puntenZClean,velden_uitvoer,profielen):

    profieldDict = {}

    angleCursor = arcpy.da.SearchCursor(puntenZClean, velden_uitvoer)
    for k, g in groupby(angleCursor, lambda x: x[3]):

        profielnummer = int(k)

        for row in g:
            if row[4] =='bit':
                zOnder = row[1]
                aOnder = row[2]
            if row[4] =='insteekberm':
                zOnder = row[1]
                aOnder = row[2]
            if row[4] =='bik':
                zBoven = row[1]
                aBoven = row[2]

            
        try:
            zOnder,aOnder,zBoven,aBoven
            
            difY = abs(zOnder-zBoven)
            difX = abs(aOnder-aBoven)
           

            angle = difX/difY
            profieldDict[profielnummer] = angle



        except NameError:
            pass
            
    
    del angleCursor
    
    if bool(profieldDict) == False:
        print "Geen geldige waardes gevonden"
    if bool(profieldDict) == True:
        # veld voor angle toevoegen
        currentFields = [f.name for f in arcpy.ListFields(profielen)]
        
        for item in currentFields:

            if "angle" in currentFields:
                pass
            else:
                arcpy.AddField_management(profielen,"angle","DOUBLE", 2, field_is_nullable="NULLABLE")

        profielCursor = arcpy.da.UpdateCursor(profielen, ['profielnummer','angle'])

        for row in profielCursor:
            profiel = int(row[0])
            if profiel in profieldDict:
                row[1] = profieldDict[profiel]
                profielCursor.updateRow(row)
            else:
                pass




        

def plot(dijkpalen,profielen):

    dp = []
    dp_MEAS = []

    array_dp =arcpy.da.FeatureClassToNumPyArray(dijkpalen, ('RFTIDENT','afstand','z_ahn'))
    df_dp = pd.DataFrame(array_dp)
    sort_dp = df_dp.sort_values(['afstand'], ascending=[True])

    array_profielen = arcpy.da.FeatureClassToNumPyArray(profielen, ('afstand','angle'))
    df_profielen = pd.DataFrame(array_profielen)
    sort_profielen = df_profielen.sort_values(['afstand'], ascending=[True])

    # define plot
    plt.style.use('seaborn-whitegrid') #seaborn-ticks
    fig = plt.figure(figsize=(110, 5))

    ax1 = fig.add_subplot(111, label ="1",frame_on=True)
    ax1.plot(sort_profielen['afstand'],sort_profielen['angle'],'bo',markersize=2)
    
    # opbouwen nieuwe dataframe en plot dijkpalen
    for index, row in sort_dp.iterrows():

        dp.append(row['RFTIDENT'])
        dp_MEAS.append(row['afstand'])


    df_dp = pd.DataFrame(
        {'dp': dp,
        'afstand': dp_MEAS})

    df_dp = df_dp[::5]

    dp_lijst = df_dp['dp'].tolist()
    dp_MEAS_lijst = df_dp['afstand'].tolist()

    # ax2.vlines(x=dp_MEAS_lijst, ymin=0, ymax=0, color='black', linewidth=2.5, linestyle = '-', label = "Beta 4,8")

    # grafiek netjes maken
    # ax1.axes.get_xaxis().set_visible(False)
    # ax1.axes.get_yaxis().set_visible(False)

    # ax2 = ax1.twiny()
    ax1.set_xticks(dp_MEAS_lijst)
    ax1.set_xticklabels(dp_lijst,rotation=45)
    ax1.set_ylabel('Talud [1:..]')
    ax1.set_xlabel('Dijkpaal')


    # ax1.plot(sort_profielen['afstand'],sort_profielen['angle'],'bo',markersize=5,color='red',label="Profielhelling")

    # plt.show()
    plt.savefig(figure, pad_inches=0.02, dpi=300, bbox_inches='tight')
    del fig




# calculateAngle(puntenZClean,velden_uitvoer,profielen)
plot(dijkpalen,profielen)







