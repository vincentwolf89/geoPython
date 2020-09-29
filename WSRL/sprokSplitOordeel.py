import arcpy
import pandas as pd
import numpy as np
from itertools import groupby

# from basisfuncties import*

arcpy.env.workspace = r'D:\Projecten\WSRL\sterreschans_heteren\GIS\kaartmateriaal.gdb'
gdb = r'D:\Projecten\WSRL\sterreschans_heteren\GIS\kaartmateriaal.gdb'
arcpy.env.overwriteOutput = True

puntenOordeel ="dijkbasisregel" #invoer uitvoerpunten
outputOordeelLijn = "oordeel_dijkbasisregel" # uitvoer gesplitte trajectlijn
profielen = "profielen_sh"
minTrajectLengte = 50
trajectLijn = "trajectlijn_sh"
veldenOordeelPunten = ['Eindoordeel','profielnummer']
veldenProfielen = ['profielnummer','eindoordeelPiping']
lijstOnvoldoende = ["IVv", "Vv", "VIv","Voldoet niet vanwege dijkbasisregel"]

outputPunten = "OordeelProfielNummer"


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

def eindOordeel(trajectLijn, profielen, outputOordeelLijn, minTrajectLengte):
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
    arcpy.Dissolve_management("splitTussenOordeel", "tempDissolve", "eindoordeelPiping", "", "MULTI_PART", "DISSOLVE_LINES")

    # unmerge de twee lijnen om trajecten kleiner dan 50 m eruit te halen
    arcpy.FeatureVerticesToPoints_management("tempDissolve", "tempDissolvePoints", "START")

    # split dissolved oordeellijn op dissolvepunten
    arcpy.SplitLineAtPoint_management("tempDissolve", "tempDissolvePoints", "tempDissolveSplit", 1)

    # maak feature class met alleen lijndelen die aan lengte-eis voldoen
    arcpy.CopyFeatures_management('tempDissolveSplit', 'tempDissolveSplitLang')
    with arcpy.da.UpdateCursor("tempDissolveSplitLang", ['SHAPE@LENGTH']) as cursor:
        for row in cursor:
            if row[0] < minTrajectLengte:
                cursor.deleteRow()
            else:
                pass
    del cursor

    # maak feature class met alleen lijndelen die niet aan de lengte-eis voldoen
    with arcpy.da.UpdateCursor("tempDissolveSplit", ['SHAPE@LENGTH']) as cursor:
        for row in cursor:
            if row[0] >= minTrajectLengte:
                cursor.deleteRow()
            else:
                pass
    del cursor

    # join elk kort lijndeel aan dichtstbijzijnde lange lijndeel en neem oordeel over
    arcpy.Near_analysis("tempDissolveSplit", "tempDissolveSplitLang", "", "NO_LOCATION", "NO_ANGLE", "PLANAR")

    # join eindoordeel van dichtstbijzijnde lange lijndeel
    arcpy.JoinField_management("tempDissolveSplit", "NEAR_FID", "tempDissolveSplitLang", "OBJECTID", "eindoordeelPiping")
    arcpy.AlterField_management("tempDissolveSplit", "eindoordeelPiping", "eindoordeelPipingKort")
    arcpy.AlterField_management("tempDissolveSplit", "eindoordeelPiping_1", "eindoordeelPiping")

    # merge lijnen
    arcpy.Merge_management(["tempDissolveSplit", "tempDissolveSplitLang"], "tempTotaalMerge")

    # dissolve op oordeel
    arcpy.Dissolve_management("tempTotaalMerge", outputOordeelLijn, "eindoordeelPiping", "", "MULTI_PART",
                              "DISSOLVE_LINES")


    print "Eindoordeel voor trajectlijn bepaald"

koppelingPunten(puntenOordeel,profielen,outputPunten)
oordeelProfiel(outputPunten, veldenOordeelPunten, lijstOnvoldoende,profielen, veldenProfielen)
eindOordeel(trajectLijn,profielen,outputOordeelLijn,minTrajectLengte)

