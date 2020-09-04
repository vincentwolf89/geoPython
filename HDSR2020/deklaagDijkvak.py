import arcpy
from arcpy.sa import *
import sys
sys.path.append('.')
import pandas as pd

from basisfuncties import average, copy_trajectory_lr

arcpy.env.workspace = r'D:\Projecten\HDSR\2020\gisData\basisData.gdb'

arcpy.env.overwriteOutput = True

dijkvakken = 'RWK_areaal_2024'
raster = r"D:\Projecten\HDSR\2019\data\hoogteData.gdb\AHN3grondfilter"







with arcpy.da.UpdateCursor(dijkvakken,['SHAPE@','Naam','gemDeklaag','minDeklaag']) as dijkvakcursor:
    for row in dijkvakcursor:
        
        # parallellijn
        dijkvak = row[0]
        dijkvakNaam = row[1]
        arcpy.CopyFeatures_management(dijkvak,"parallellijn")
        copy_trajectory_lr("parallellijn",code,10)
        arcpy.Delete_management("river")

        # profielen dijkvak selecteren
        lyr = arcpy.MakeFeatureLayer_management(profielen, 'profielenLyr') 
        where = '"' + "Naam" + '" = ' + "'" + dijkvakNaam + "'"
        selected = arcpy.SelectLayerByAttribute_management(lyr, "NEW_SELECTION", where)
        arcpy.CopyFeatures_management(selected,"profielen_dijkvak")

        # intersect met parallellijn
        arcpy.Intersect_analysis(["profielen_dijkvak","land"], "deklaagPuntenTemp", "ALL", "", "POINT")

        # extract values to deklaagPunten
        arcpy.FeatureToPoint_management("deklaagPuntenTemp", "deklaagPunten", "")
        ExtractValuesToPoints("deklaagPunten", raster, "deklaagPuntenZ", "INTERPOLATE", "VALUE_ONLY")
        

        # terugkoppeling
        # with arcpy.da.SearchCursor("deklaagPuntenZ",['SHAPE@','Naam']) as dijkvakcursor:
        arcpy.Statistics_analysis("deklaagPuntenZ", "deklaagTableMin", "RASTERVALU MIN", "")
        arcpy.Statistics_analysis("deklaagPuntenZ", "deklaagTableGem", "RASTERVALU MEAN", "")



        with arcpy.da.SearchCursor("deklaagTableMin",['MIN_RASTERVALU']) as dmincursor:
            for item in dmincursor:
                deklaagMin = item[0]
                print deklaagMin
        
        
        with arcpy.da.SearchCursor("deklaagTableGem",['MEAN_RASTERVALU']) as dgemcursor:
            for item in dgemcursor:
                deklaagGem = item[0]
                


        try:
            deklaagGem, deklaagMin
            if deklaagGem == None:
                pass
            else:
                row[2] = round(deklaagGem,2)
                row[3] = round(deklaagMin,2)
        except NameError:
            print "geen waardes"
            pass



       
        dijkvakcursor.updateRow(row)
        # arcpy.Delete_management("deklaagPuntenZ")

        print dijkvakNaam

        # break




