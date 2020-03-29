import arcpy
from basisfuncties import *
from arcpy.sa import *

arcpy.CheckOutExtension("Spatial")

arcpy.env.workspace = r'D:\GoogleDrive\WSRL\test_vergridden.gdb'
arcpy.env.overwriteOutput = True

waterlopen = "waterlopen_samples"


tolerance = 0.3
dist_mini_buffer = -0.2
code_waterloop = "id_string"



lijn = "waterloop_lijn_21"
vlak = "waterloop_21"
## raster maken voor middenlijn ##

def bodemlijn_bepalen(lijn,vlak,tolerance,dist_mini_buffer, bodemlijn):

    #vlak naar lijn vertalen
    arcpy.FeatureToLine_management(vlak, lijn)
    # waterloop buffer afronden (lijn en polygoon)
    arcpy.SmoothLine_cartography(lijn, "line_smooth", "PAEK", "10 Meters", "FIXED_CLOSED_ENDPOINT", "NO_CHECK")
    arcpy.SmoothPolygon_cartography(vlak, "poly_smooth", "PAEK", "10 Meters", "FIXED_ENDPOINT", "NO_CHECK")
    # euclidean raster
    arcpy.gp.EucDistance_sa("line_smooth", "temp_euclidean", "", "0,1","")
    # slope euclidean raster
    arcpy.gp.Slope_sa("temp_euclidean", "temp_slope", "DEGREE", "1")
    # rastercalc
    raster = arcpy.Raster("temp_slope")
    outraster = raster <= 42
    outraster.save("temp_rastercalc")
    # clip raster with polygon
    # eerst minibuffer op polygoon
    arcpy.Buffer_analysis("poly_smooth", "temp_buffer_smnooth", dist_mini_buffer, "OUTSIDE_ONLY", "FLAT", "NONE", "", "PLANAR")
    # minibuffer binnekant bewaren
    list_oid = []
    arcpy.FeatureToLine_management("temp_buffer_smnooth", "temp_buffer_smnooth_lijn")
    with arcpy.da.SearchCursor("temp_buffer_smnooth_lijn", "OID@") as cursor:
        for row in cursor:
            list_oid.append(row[0])
    del cursor
    oid = list_oid[-2]
    with arcpy.da.UpdateCursor("temp_buffer_smnooth_lijn", "OID@") as cursor:
        for row in cursor:
            if row[0] == oid:
                pass
            else:
                cursor.deleteRow()
    # terugvertaling buffer naar binnenvlak
    arcpy.FeatureToPolygon_management("temp_buffer_smnooth_lijn", "temp_buffer_smnooth_poly")

    # clip raster met minibuffer
    arcpy.Clip_management("temp_rastercalc", "", "temp_clip", "temp_buffer_smnooth_poly", "127", "ClippingGeometry", "MAINTAIN_EXTENT")
    # clip to polygon
    arcpy.RasterToPolygon_conversion("temp_clip", "temp_poly", "SIMPLIFY", "Value")
    # remove items with gridcode 0
    with arcpy.da.UpdateCursor("temp_poly", ["gridcode","SHAPE@AREA"]) as cursor:
        for row in cursor:
            if row[0] is 0 or row[1] < 0.1:
                cursor.deleteRow()
            else:
                pass


    ## middenlijn maken vanuit raster ##
    # poly to line
    arcpy.FeatureToLine_management("temp_poly", "temp_poly_lijn")
    # split line at vertices
    arcpy.SplitLine_management("temp_poly_lijn", "temp_poly_lijn_split")

    # select only bodempart
    arcpy.MakeFeatureLayer_management("temp_poly_lijn_split", "temp_poly_lijn_split_feat")
    arcpy.SelectLayerByLocation_management("temp_poly_lijn_split_feat", "INTERSECT", lijn, tolerance, "NEW_SELECTION", "INVERT")
    arcpy.CopyFeatures_management("temp_poly_lijn_split_feat", bodemlijn)



with arcpy.da.SearchCursor(waterlopen,['SHAPE@',code_waterloop]) as cursor:
    for row in cursor:
        id = row[1]

        lijn = "waterloop_lijn_" + str(row[1])
        vlak = "waterloop_vlak_" + str(row[1])
        bodemlijn = "bodemlijn_waterloop_" + str(row[1])
        # tin = "D:/GoogleDrive/WSRL/tin/waterloop"+str(row[1])

        where = '"' + code_waterloop + '" = ' + "'" + str(id) + "'"

        arcpy.Select_analysis(waterlopen, vlak, where)

        bodemlijn_bepalen(lijn, vlak, tolerance, dist_mini_buffer, bodemlijn)
