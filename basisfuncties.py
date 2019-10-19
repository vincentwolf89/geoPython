import arcpy
import math
from arcpy.sa import *

arcpy.env.overwriteOutput = True


arcpy.env.workspace = r'C:\Users\vince\Desktop\GIS\test.gdb'

profielen = 'test_profielen'
stapgrootte_punten = 2
raster = r'C:\Users\vince\Desktop\GIS\losse rasters\ahn3clip\ahn3clip_2m'
trajectlijn = 'test_trajectlijn'

def distance_points(profielen):

    # clean feature
    existing_fields = arcpy.ListFields(profielen)
    needed_fields = ['OBJECTID','SHAPE','SHAPE_Length']
    for field in existing_fields:
        if field.name not in needed_fields:
            arcpy.DeleteField_management(profielen, field.name)


    # add needed fields
    arcpy.AddField_management(profielen, "profielnummer", "DOUBLE", 2, field_is_nullable="NULLABLE")
    arcpy.AddField_management(profielen, "van", "DOUBLE", 2, field_is_nullable="NULLABLE")
    arcpy.AddField_management(profielen, "tot", "DOUBLE", 2, field_is_nullable="NULLABLE")

    # set values of new fields
    arcpy.CalculateField_management(profielen, "profielnummer", '!OBJECTID!', "PYTHON")
    arcpy.CalculateField_management(profielen, "van", 0, "PYTHON")
    arcpy.CalculateField_management(profielen, "tot", '!SHAPE_Length!', "PYTHON")

    # create routes
    arcpy.CreateRoutes_lr(profielen, "profielnummer", "routes_profielen", "TWO_FIELDS", "van", "tot", "", "1", "0", "IGNORE", "INDEX")
    arcpy.GeneratePointsAlongLines_management('routes_profielen', 'punten_route', 'DISTANCE', Distance= stapgrootte_punten, Include_End_Points='END_POINTS')

    # extra field for joining
    arcpy.AddField_management('punten_route', 'punt_id', "DOUBLE", field_precision=2, field_is_nullable="NULLABLE")
    arcpy.CalculateField_management("punten_route", "punt_id", '!OBJECTID!', "PYTHON")


    # lokaliseren van de punten op de gemaakte routes
    Output_Event_Table_Properties = "RID POINT MEAS"
    arcpy.LocateFeaturesAlongRoutes_lr('punten_route', 'routes_profielen', "profielnummer", "1 Meters",
                                       'uitvoer_tabel', Output_Event_Table_Properties, "FIRST", "DISTANCE", "ZERO",
                                       "FIELDS", "M_DIRECTON")


    # Koppelen van tabel met locaties met de punten, hier is het punt_id veld weer nodig
    arcpy.JoinField_management('punten_route', 'punt_id', 'uitvoer_tabel', 'punt_id', 'MEAS')
    arcpy.AlterField_management('punten_route', 'MEAS', 'afstand')
    arcpy.CalculateField_management("punten_route", "afstand", 'round(!afstand!, 2)', "PYTHON")
    # print 'MEAS toegevoegd aan puntenlaag vanuit tabel en veldnaam aangepast naar afstand'





def extract_z_arcpy(invoerpunten, uitvoerpunten, raster): #

    # Test de ArcGIS Spatial Analyst extension license
    arcpy.CheckOutExtension("Spatial")

    # Koppel z-waardes
    ExtractValuesToPoints(invoerpunten, raster, uitvoerpunten,
                          "INTERPOLATE", "VALUE_ONLY")

    # Pas het veld 'RASTERVALU' aan naar 'z_ahn'
    arcpy.AlterField_management(uitvoerpunten, 'RASTERVALU', 'z_ahn')
    print "Hoogte-waarde aan punten gekoppeld en veld aangepast naar z_ahn"





def copy_trajectory_lr():
    arcpy.AddField_management(trajectlijn, "Width", "DOUBLE", 2, field_is_nullable="NULLABLE")
    arcpy.CalculateField_management(trajectlijn, "Width", 5, "PYTHON")

    arcpy.CopyFeatures_management(trajectlijn, "river")
    arcpy.CopyFeatures_management(trajectlijn, "land")
    land = "land"
    river = "river"


    with arcpy.da.UpdateCursor(land, ("Shape@", "Width")) as cursor:
        for shp, w in cursor:
            LeftLine = CopyParallelL(shp, w)
            cursor.updateRow((LeftLine, w))

    with arcpy.da.UpdateCursor(river, ("Shape@", "Width")) as cursor:
        for shp, w in cursor:
            RightLine = CopyParallelR(shp, w)
            cursor.updateRow((RightLine, w))


def CopyParallelL(plyP,sLength):
    part=plyP.getPart(0)
    lArray=arcpy.Array()
    for ptX in part:
        dL=plyP.measureOnLine(ptX)
        ptX0=plyP.positionAlongLine (dL-0.01).firstPoint
        ptX1=plyP.positionAlongLine (dL+0.01).firstPoint
        dX=float(ptX1.X)-float(ptX0.X)
        dY=float(ptX1.Y)-float(ptX0.Y)
        lenV=math.hypot(dX,dY)
        sX=-dY*sLength/lenV;sY=dX*sLength/lenV
        leftP=arcpy.Point(ptX.X+sX,ptX.Y+sY)
        lArray.add(leftP)
    array = arcpy.Array([lArray])
    section=arcpy.Polyline(array)
    return section

def CopyParallelR(plyP,sLength):
    part=plyP.getPart(0)
    rArray=arcpy.Array()
    for ptX in part:
        dL=plyP.measureOnLine(ptX)
        ptX0=plyP.positionAlongLine (dL-0.01).firstPoint
        ptX1=plyP.positionAlongLine (dL+0.01).firstPoint
        dX=float(ptX1.X)-float(ptX0.X)
        dY=float(ptX1.Y)-float(ptX0.Y)
        lenV=math.hypot(dX,dY)
        sX=-dY*sLength/lenV;sY=dX*sLength/lenV
        rightP=arcpy.Point(ptX.X-sX, ptX.Y-sY)
        rArray.add(rightP)
    array = arcpy.Array([rArray])
    section=arcpy.Polyline(array)
    return section

copy_trajectory_lr()