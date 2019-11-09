import arcpy
import gc
gc.collect()
from basisfuncties import *

# rastercalculator remove nan
# contour lines 0.5 m
# profielen



arcpy.env.overwriteOutput = True


arcpy.env.workspace = r'D:\Projecten\WSRL\werk.gdb'

sloten = 'waterlopen_test'
contour_ahn = 'contour_test'
profiel_interval = 10
profiel_lengte_land = 10
profiel_lengte_rivier = 10
raster = 'ahn3clip_test'


def knip_sloten(profielen,slootlijn):
    # intersect op snijpunten met gridlijnen
    intersects = [profielen,contour_ahn]
    arcpy.Intersect_analysis(intersects, 'knip_sloten_punt', "", 0, "point")
    # knip profiellijnen met intersects

    searchRadius = "0.2 Meters"
    arcpy.SplitLineAtPoint_management(profielen, 'knip_sloten_punt', 'knip_profielen', searchRadius)

    # verwijder profiel indien middelpunt op niet-nan data ligt
    arcpy.Intersect_analysis([profielen,slootlijn], 'middelpunten_profielen', "", 0.5, "point")

    arcpy.FeatureToPoint_management('middelpunten_profielen', 'middelpunten_profielen_', "CENTROID")
    ExtractValuesToPoints('middelpunten_profielen_', raster, 'middelpunten_profielen_z', "INTERPOLATE", "VALUE_ONLY")
    arcpy.JoinField_management(profielen, "profielnummer", "middelpunten_profielen_z", "profielnummer",["RASTERVALU"])

    with arcpy.da.UpdateCursor(profielen, ['RASTERVALU']) as cursor:
        for row in cursor:
            if row[0] is not None:
                cursor.deleteRow()
            else:
                continue

    # selecteer lijndeel dat intersect met sloten
    arcpy.MakeFeatureLayer_management('knip_profielen', 'knip_profielen_temp')
    arcpy.SelectLayerByLocation_management('knip_profielen_temp', 'intersect', slootlijn)
    arcpy.CopyFeatures_management('knip_profielen_temp', 'slootbreedtes')



profielen = 'profielen_sloot_16'
slootlijn = 'sloot_16'
knip_sloten(profielen,slootlijn)


def iterate_sloten():
    with arcpy.da.SearchCursor(sloten,['SHAPE@','sloot_id']) as cursor:
        for row in cursor:
            # lokale variabelen per dijktraject
            code = 'sloot_id'
            id = row[1]
            slootlijn = 'sloot_'+str(row[1])
            profielen = 'profielen_sloot_'+str(row[1])
            where = '"' + code + '" = ' + "'" + str(id) + "'"

            # selecteer betreffend traject
            arcpy.Select_analysis(sloten, slootlijn, where)

            # genereer profielen haaks op sloten
            generate_profiles(profiel_interval, profiel_lengte_land, profiel_lengte_rivier, slootlijn, code, profielen)



            knip_sloten(profielen)


