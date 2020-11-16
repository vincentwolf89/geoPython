import arcpy
from arcpy.sa import *
from itertools import groupby
import pandas as pd

sys.path.append('HDSR2020')
from basisRWK2020 import generate_profiles, copy_trajectory_lr, split_profielen

arcpy.env.overwriteOutput = True
arcpy.env.workspace = r"D:\Projecten\HDSR\2020\gisData\geomToets.gdb"
workspace = r"D:\Projecten\HDSR\2020\gisData\geomToets.gdb"






trajectenHDSR = "testTraject2"
afstandKruinSegment = 0.5 
minKruinBreedte = 1.5
code_hdsr = "Naam"
toetsniveaus = "th2024"
waterlopenBGTBoezem = "bgt_waterdeel_boezem"
rasterWaterstaatswerk = "WWBAG2mPlusWaterlopenAHN3"

def maak_profielen(trajectlijn,code,toetsniveau,profielen,bgt_waterdeel_boezem):
    # lange profielen maken 
    generate_profiles(profiel_interval=25,profiel_lengte_land=40,profiel_lengte_rivier=1000,trajectlijn=trajectlijn,code=code,
    toetspeil=toetsniveau,profielen=profielen)

    # profielen knippen buitenzijde: BAG
    copy_trajectory_lr(trajectlijn=trajectlijn,code=code)
    split_profielen(profielen=profielen,trajectlijn=trajectlijn,code=code)

    # snijpunten van rivierzijde profieldelen en boezemwaterlopen
    arcpy.Intersect_analysis(["profieldeel_rivier",bgt_waterdeel_boezem], "tempSplitBoezem", "ALL", "", "POINT")
    arcpy.SplitLineAtPoint_management(profielen, "tempSplitBoezem", "tempProfielenSplit", "1 Meters")
    arcpy.MakeFeatureLayer_management("tempProfielenSplit", "tempProfiellayer") 
   
    arcpy.SelectLayerByLocation_management("tempProfiellayer", "INTERSECT", trajectlijn, "", "NEW_SELECTION", "NOT_INVERT")
    arcpy.CopyFeatures_management("tempProfiellayer", "tempProfielen")

    profielCursor = arcpy.da.UpdateCursor("tempProfielen", ["van","tot","SHAPE@LENGTH"])
    for row in profielCursor:
        lengte = row[2]
        row[0] = 0
        row[1] = lengte
        profielCursor.updateRow(row)

    
    del profielCursor
    arcpy.CreateRoutes_lr("tempProfielen", "profielnummer", "profielen","TWO_FIELDS", "van", "tot", "UPPER_LEFT", "1", "0", "IGNORE", "INDEX")




def bepaal_kruinvlak_toetsniveau(trajectlijn,rasterWaterstaatswerk,toetsniveau,profielen):
    # maak buffer van traject om raster te knippen
    arcpy.Buffer_analysis(trajectlijn, "tempBufferTrajectlijn", "10 Meters", "FULL", "ROUND", "NONE", "", "PLANAR")

    # knip buffer uit totaalraster
    arcpy.Clip_management(rasterWaterstaatswerk,"", "tempRaster", "tempBufferTrajectlijn", "-3,402823e+038", "ClippingGeometry", "MAINTAIN_EXTENT")
    

    # raster calculator, selecteer deel op en boven toetsniveau
    raster = arcpy.Raster("tempRaster")
    outraster = raster >= toetsniveau
    outraster.save("tempRasterCalc")

    # arcpy.gp.FocalStatistics_sa("tempRasterCalc", "tempRasterCalcFocal", "Rectangle 3 3 CELL", "MEAN", "DATA")

    # raster vertalen naar polygon en alleen deel boven toetsniveau overhouden (gridcode = 1)
    arcpy.RasterToPolygon_conversion("tempRasterCalc", "tempRasterPoly", "SIMPLIFY", "Value")
    arcpy.Select_analysis("tempRasterPoly", "temp_opBovenTn", "gridcode = 1")


    # knip profielen op vlak "opBovenTn"
    arcpy.Intersect_analysis([profielen,"temp_opBovenTn"], "tempSplitKruin", "ALL", "", "POINT")
    arcpy.SplitLineAtPoint_management(profielen, "tempSplitKruin", "splitTempProfielen", "1 Meters")
    arcpy.MakeFeatureLayer_management("splitTempProfielen", "tempProfiellayer") 

    arcpy.SelectLayerByLocation_management("tempProfiellayer", "WITHIN", "temp_opBovenTn", "", "NEW_SELECTION", "NOT_INVERT")
    arcpy.CopyFeatures_management("tempProfiellayer", "profielDelenOpBovenTn")

    # samenvoegen delen die 0,5 m van elkaar afliggen
    sr = arcpy.SpatialReference(28992)
    arcpy.CreateFeatureclass_management(workspace, "kruindelenTraject", "POLYLINE",spatial_reference= sr)
    arcpy.AddField_management("kruindelenTraject","profielnummer","DOUBLE", 2, field_is_nullable="NULLABLE")
    kruindelenCursor = arcpy.da.InsertCursor("kruindelenTraject", ["profielnummer","SHAPE@"])


    kruinCursor = arcpy.da.UpdateCursor("profielDelenOpBovenTn",["profielnummer","SHAPE@"],sql_clause=(None, 'ORDER BY profielnummer ASC'))
    
    for profielnummer, group in groupby(kruinCursor, lambda x: x[0]):

        kruinDelenGroep = []
        for kRow in group:
            kruinDelenGroep.append(kRow[1])
        
        # samenvoegen
        arcpy.Merge_management(kruinDelenGroep,"kruinGroep")

        # near tabel maken
        arcpy.Near_analysis("kruinGroep", "kruinGroep", "", "NO_LOCATION", "NO_ANGLE", "PLANAR")

        # nears met < 0,5 m verwijderen
     

        profielCursorKruin = arcpy.da.UpdateCursor("kruinGroep",["NEAR_DIST","SHAPE@LENGTH"])

        for pRow in profielCursorKruin:
            if (pRow[0] > afstandKruinSegment) and (pRow[1] < minKruinBreedte):
                profielCursorKruin.deleteRow()
            else:
                pass

        del profielCursorKruin

        # indien twee of meer delen aanwezig zijn die wel lang genoeg zijn maar te ver uit elkaar liggen: langste overhouden
        
        try:
            minLengte = round(min([z[0] for z in arcpy.da.SearchCursor ("kruinGroep", ["SHAPE@LENGTH"])]),2)
            maxLengte = round(max([z[0] for z in arcpy.da.SearchCursor ("kruinGroep", ["SHAPE@LENGTH"])]),2)

            profielCursorKruin = arcpy.da.UpdateCursor("kruinGroep",["NEAR_DIST","SHAPE@LENGTH"])

            for pRow in profielCursorKruin:
                if (pRow[0] > afstandKruinSegment) and (round(pRow[1],2) == maxLengte):
                    pass
                if (pRow[0] > afstandKruinSegment) and (round(pRow[1],2) < maxLengte):
                    profielCursorKruin.deleteRow()

            del profielCursorKruin
        
        except ValueError:
            pass


        
        
        # punten van lijnen maken
        arcpy.FeatureVerticesToPoints_management("kruinGroep", "kruinGroepPunten", "BOTH_ENDS")
        arcpy.AddField_management("kruinGroepPunten", "profielnummer", "DOUBLE", 2, field_is_nullable="NULLABLE")
        tempCursor = arcpy.da.UpdateCursor("kruinGroepPunten","profielnummer")
        for tRow in tempCursor:
            tRow[0] = profielnummer
            tempCursor.updateRow(tRow)

        del tempCursor
        # eindpunten overhouden door afstandberekening
        arcpy.LocateFeaturesAlongRoutes_lr("kruinGroepPunten", profielen, "profielnummer", "0,1 Meters", "kruinTable", "RID POINT MEAS", "FIRST", "DISTANCE", "ZERO", "FIELDS", "M_DIRECTON")
        arcpy.JoinField_management("kruinGroepPunten","OBJECTID","kruinTable","OBJECTID","MEAS")


        try:
            minMeas = round(min([z[0] for z in arcpy.da.SearchCursor ("kruinGroepPunten", ["MEAS"])]),2)
            maxMeas = round(max([z[0] for z in arcpy.da.SearchCursor ("kruinGroepPunten", ["MEAS"])]),2)

            eindMeas = [minMeas,maxMeas]

            tempCursor = arcpy.da.UpdateCursor("kruinGroepPunten",["profielnummer","MEAS"])
            for tRow in tempCursor:
                if round(tRow[1],2) in eindMeas:
                    pass
                else:
                    tempCursor.deleteRow()

            del tempCursor

            # lijn maken van afstandpunten
            arcpy.PointsToLine_management("kruinGroepPunten", "kruinGroepLijn", "", "", "NO_CLOSE")

            # lijn toevoegen aan kruindelen met insertcursor
            kruinDeel = [z[0] for z in arcpy.da.SearchCursor ("kruinGroepLijn", ["SHAPE@"])][0]


            kruindelenCursor.insertRow([profielnummer,kruinDeel])
            print profielnummer 

        except ValueError:
            pass














with arcpy.da.SearchCursor(trajectenHDSR,['SHAPE@',code_hdsr,toetsniveaus]) as cursor:
    for row in cursor:
        
        # lokale variabelen per dijktraject
        code = code_hdsr
        toetsniveau = float(row[2])
        id = row[1]
        
        profielen = "profielen"
        trajectlijn = "tempTrajectlijn"

        # selecteer betreffend traject en kopieer naar tijdelijke laag
        where = '"' + code_hdsr + '" = ' + "'" + str(id) + "'"
        arcpy.Select_analysis(trajectenHDSR, trajectlijn, where)


        # stap 1: profielen op juiste maat maken
        maak_profielen(trajectlijn=trajectlijn,code=code,toetsniveau=toetsniveau,profielen=profielen,bgt_waterdeel_boezem=waterlopenBGTBoezem)



        # stap 2: bepaal gedeelte dat op-boven toetsniveau ligt
        bepaal_kruinvlak_toetsniveau(trajectlijn=trajectlijn,rasterWaterstaatswerk=rasterWaterstaatswerk,toetsniveau=toetsniveau,profielen=profielen)

