import arcpy
import pandas as pd
import numpy as np
from itertools import groupby

# from basisfuncties import*

arcpy.env.workspace = r'D:\GoogleDrive\WSRL\sprok_sterrenschans.gdb'
gdb = r'D:\GoogleDrive\WSRL\sprok_sterrenschans.gdb'
arcpy.env.overwriteOutput = True

puntenOordeel ="ga_topzand"
profielen = "profielen_ss"
trajectLijn = "trajectlijn"
veldenOordeelPunten = ['Eindoordeel','profielnummer']
veldenProfielen = ['profielnummer','eindoordeelPiping']
lijstOnvoldoende = ["IVv", "Vv", "VIv","Voldoet niet vanwege dijkbasisregel"]

outputPunten = "OordeelProfielNummer"
outputOordeelLijn = "oordeel_ga_topzand_v2"

def koppelingPunten(puntenOordeel,profielen,outputPunten):
    # koppel profielnummer aan punten, dichtstbijzijnde
    arcpy.SpatialJoin_analysis(puntenOordeel, profielen, outputPunten, "JOIN_ONE_TO_ONE", "KEEP_ALL","",match_option="CLOSEST")

    print "Oordeel van punten gekoppeld aan profielnummers"

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

    print "Oordeel van punten per profiel vastgesteld"

def eindOordeel(trajectLijn, profielen, outputOordeelLijn):
    # isects trajectlijn profielen
    arcpy.Intersect_analysis([trajectLijn,profielen], "tempIsect", "ALL", "", "POINT")


    # split trajectlijn at isects
    arcpy.SplitLineAtPoint_management(trajectLijn, "tempIsect", 'splitProfielen', 1)

    # midpoints splits
    arcpy.FeatureVerticesToPoints_management("splitProfielen", "splitProfielenPunten", "MID")

    # split trajectlijn tussen profielen
    arcpy.SplitLineAtPoint_management(trajectLijn, "splitProfielenPunten", 'splitTussen', 1)
    # koppel oordeel splits
    arcpy.SpatialJoin_analysis('splitTussen', profielen, "splitTussenOordeel", "JOIN_ONE_TO_ONE", "KEEP_ALL","",match_option="CLOSEST")
    # dissolve op eindoordeel
    arcpy.Dissolve_management("splitTussenOordeel", outputOordeelLijn, "eindoordeelPiping", "", "MULTI_PART", "DISSOLVE_LINES")

    print "Eindoordeel voor trajectlijn bepaald"

koppelingPunten(puntenOordeel,profielen,outputPunten)
oordeelProfiel(outputPunten, veldenOordeelPunten, lijstOnvoldoende,profielen, veldenProfielen)
eindOordeel(trajectLijn,profielen,outputOordeelLijn)

