import arcpy
import pandas as pd
import numpy as np
from itertools import groupby

# from basisfuncties import*

arcpy.env.workspace = r'D:\GoogleDrive\WSRL\sprok_sterrenschans.gdb'
gdb = r'D:\GoogleDrive\WSRL\sprok_sterrenschans.gdb'
arcpy.env.overwriteOutput = True

puntenOordeel ="OutputAggregatiePerUittredepunt"
profielen = "profielen_ss"
veldenOordeelPunten = ['Eindoordeel','profielnummer']
veldenProfielen = ['profielnummer','eindoordeelPiping']
lijstOnvoldoende = ["IIIv","Ivv","Vv","VIv","Voldoet niet vanwege dijkbasisregel"]

outputPunten = "OordeelProfielNummer"

def koppelingPunten(puntenOordeel,profielen,outputPunten):
    # koppel profielnummer aan punten, dichtstbijzijnde
    arcpy.SpatialJoin_analysis(puntenOordeel, profielen, outputPunten, "JOIN_ONE_TO_ONE", "KEEP_ALL","",match_option="CLOSEST")

def oordeelProfiel(outputPunten, veldenOordeelPunten, lijstOnvoldoende,profielen, veldenProfielen):
    df = pd.DataFrame(columns=['profielnummer','eindoordeel'])
    index = 0

    with arcpy.da.SearchCursor(outputPunten, veldenOordeelPunten) as cursor:
        for row in cursor:
            if row[0] in lijstOnvoldoende:
                profielnummer = row[1]
                oordeel = "onvoldoende"
                df.loc[index, 'eindoordeel'] = oordeel
                df.loc[index, 'profielnummer'] = profielnummer
                index += 1


            else:
                pass

    df_clean = df.drop_duplicates(subset="profielnummer", keep='first', inplace=False)
    lijstOnvoldoendePD = df_clean['profielnummer'].tolist()



    # koppel oordeel aan profielen
    with arcpy.da.UpdateCursor(profielen, veldenProfielen) as cursor:
        for row in cursor:
            if row[0] in lijstOnvoldoendePD:
                row[1] = "onvoldoende"
            else:
                row[1] = "voldoende"
            cursor.updateRow(row)

# isects trajectlijn profielen
# split trajectlijn at isects
# midpoints splits
# koppel oordeel splits, merge splits met zelfde oordeel!

