import arcpy
from basisfuncties import average
from basisfuncties import generate_profiles

arcpy.env.workspace = r'D:\GoogleDrive\WSRL\test_waterlopen.gdb'
arcpy.env.overwriteOutput = True
code_waterloop = "id_string"
raster_ahn = r'D:\Projecten\WSRL\grote_data\ahn3SProk.gdb\ahn3ClipSprok'

# variabelen nodig voor goede run:
min_lengte_segment = 15 # segementlengte voor bepaling insteekhoogte
standaardTalud = 0.5 # standaardtalud als talud niet berekend kan worden vanuit nabijgelegen waterloop
bodemDiepte = 1 # standaardbodemdiepte als bodemdiepte niet berekend kan worden vanuit nabijgelegen waterloop
bodemDiepteSmal = 0.5
smooth = "10 Meters" # smooth voor euclidean
tolerance = 0.3 # tolerantie voor selecteren bodemdeel
dist_mini_buffer = -0.2 # minibuffer bij selecteren bodemdeel
buffer_buitenkant = 3 # buffer voor focalraster
maxBreedteSmal = 2

# invoervariabelen
waterlopen_invoer = "waterlopen_samples2"
waterlopen = "waterlopen_"
# inmetingenWaterlopen =

rasterlijst = []




def buffer_waterloop(waterloop, buffer, buffer_lijn, bodemDiepte):

    arcpy.SmoothPolygon_cartography(waterloop, "poly_smooth", "PAEK", smooth, "FIXED_ENDPOINT", "NO_CHECK")

    # set talud to standard
    talud = standaardTalud

    # bepaal bodemdDiepte
    with arcpy.da.SearchCursor(waterloop, ['soortWaterloop']) as cursor:
        for row in cursor:
            soortWaterloop = row[0]
            break

    del cursor
    print soortWaterloop


    if soortWaterloop == "smal":
        bodemDiepte = bodemDiepteSmal
    else:
        pass

    print "Er wordt voor {} een bodemdiepte van {}m gebruikt".format(waterloop, bodemDiepte)


    # bepaal bufferafstand talud
    buffer_afstand_talud = abs(bodemDiepte/talud) # buffer afstand volgens talud, tot bodemdiepte
    arcpy.Buffer_analysis("poly_smooth", buffer, -buffer_afstand_talud, "OUTSIDE_ONLY", "ROUND", "NONE", "", "PLANAR")

    arcpy.FeatureToLine_management(buffer,"temp_bufferlijn")

    # with arcpy.da.UpdateCursor("temp_bufferlijn", ['z_nap']) as cursor:
    #     for row in cursor:
    #         bodemHoogte = insteekHoogte-bodemDiepte
    #         row[0] = bodemHoogte
    #         cursor.updateRow(row)
    # del cursor

    print "Buffer gemaakt met afstand van {}m en bodemdiepte {}m".format(buffer_afstand_talud,bodemDiepte)


    # maak veld aan voor onderdeel-waterloop
    arcpy.AddField_management("temp_bufferlijn", 'onderdeel', "TEXT", field_length=50)
    arcpy.CalculateField_management("temp_bufferlijn", "onderdeel", "\"onderkant_talud\"", "PYTHON")

    #### verwijder bufferlijn die matcht met waterlooplijn!! ####
    arcpy.MakeFeatureLayer_management("temp_bufferlijn", 'templaag_bufferlijn')
    arcpy.SelectLayerByLocation_management("templaag_bufferlijn", "INTERSECT", "line_smooth", 0.1,
                                           "NEW_SELECTION", "INVERT")


    arcpy.CopyFeatures_management("templaag_bufferlijn", buffer_lijn)

    # update features
    with arcpy.da.SearchCursor(waterloop, ['bodemHoogte']) as cursor:
        for row in cursor:
            bodemHoogte = row[0]
            break
    del cursor

    with arcpy.da.UpdateCursor(buffer_lijn, ['z_nap']) as cursor:
        for row in cursor:
            row[0] = bodemHoogte
            cursor.updateRow(row)

    del cursor
    print "Binnen-buffer gemaakt voor {}".format(waterloop)


def raster_buitenkant(waterloop, buffer_buitenkant, buitenraster, raster_ahn):
    # buffer waterloop
    arcpy.Buffer_analysis(waterloop, "temp_buffer_wl", buffer_buitenkant, "OUTSIDE_ONLY", "FLAT", "NONE", "", "PLANAR")
    # raster clippen met bufferzone
    arcpy.Clip_management(raster_ahn, "",
                          "temp_raster_buitenkant", "temp_buffer_wl", "-3,402823e+038", "ClippingGeometry", "MAINTAIN_EXTENT")
    # focal stats op bufferclip
    arcpy.gp.FocalStatistics_sa("temp_raster_buitenkant", buitenraster, "Rectangle 4 4 CELL", "MEAN", "DATA")

    print "Focal buffer gemaakt voor {}".format(waterloop)


def bepaal_insteek_waterloop(waterloop,waterloop_lijn,waterloop_lijn_simp, punten_insteek, min_lengte_segment,code_waterloop):

    # lijn van omtrek waterloop
    arcpy.FeatureToLine_management(waterloop, waterloop_lijn)
    ## lijn splitsen en hoogte koppelen van oever:
    # lijn simplifyen
    arcpy.SimplifyLine_cartography(waterloop_lijn, "templijn_waterloop", "POINT_REMOVE", "0.6 Meters",
                                   "FLAG_ERRORS", "KEEP_COLLAPSED_POINTS", "CHECK")

    # lijn splitten op vertices
    arcpy.SplitLine_management("templijn_waterloop",waterloop_lijn_simp)
    # punten over lijn om de ? 0.5m?
    arcpy.GeneratePointsAlongLines_management(waterloop_lijn_simp, "templaag_punten", "DISTANCE",
                                              "0,5 Meters", "", "")

    # punten extracten uit focal stats...
    arcpy.gp.ExtractValuesToPoints_sa("templaag_punten", buitenraster, punten_insteek, "NONE",
                                      "VALUE_ONLY")

    # verwijder lijnen die in waterloop liggen (aansluitingen)
    # selecteer punten op lijnstuk, als meer dan 3/4 van de punten geen z-waarde heeft, lijnstuk deleten
    arcpy.MakeFeatureLayer_management(punten_insteek, 'templaag_insteekpunten')

    with arcpy.da.UpdateCursor(waterloop_lijn_simp, ['SHAPE@', 'z_nap', 'SHAPE@LENGTH']) as cursor:

            for row in cursor:

                arcpy.SelectLayerByLocation_management('templaag_insteekpunten', 'intersect', row[0])
                arcpy.CopyFeatures_management('templaag_insteekpunten', 'selectie_punten_temp')

                # verwijder aansluitstukken
                aantal_z = 0.1 #
                aantal_nan = 0.1
                lijst_z = []
                with arcpy.da.SearchCursor('selectie_punten_temp', ['RASTERVALU','z_nap','OBJECTID']) as cursor_waterloop:
                    for row_waterloop in cursor_waterloop:
                        if row_waterloop[0] is None:
                            aantal_nan += 1
                        else:
                            aantal_z += 1
                            lijst_z.append(row_waterloop[0])


                del cursor_waterloop


                if aantal_nan/aantal_z > 0.25 and row[2] < min_lengte_segment:
                    # print "Aansluiting eruitgehaald"
                    cursor.deleteRow()


    ## koppel gemiddelde hoogte van 10 laagste punten aan lijnstukken als z-waarde

    # zoek laagste 15 waardes per waterloop
    with arcpy.da.UpdateCursor(punten_insteek, ['RASTERVALU','z_nap','OBJECTID'],sql_clause = (None,"ORDER BY RASTERVALU ASC")) as cursor:
        aantal_punten = 0
        lijst_punten = []


        for row in cursor:
            if row[0] is None:
                cursor.deleteRow()
            else:
                if aantal_punten < 15:
                    lijst_punten.append(row[0])
                    aantal_punten += 1

                elif aantal_punten == 15:
                    z_nap_og = average(lijst_punten)
                    # print z_nap_og, waterloop
                    break




    # koppel gemiddelde laaste waarde terug aan hele waterloop
    with arcpy.da.UpdateCursor(waterloop_lijn_simp, ['z_nap']) as cursor:
        for row in cursor:
            global insteekHoogte
            insteekHoogte = round(z_nap_og,2)
            row[0] = insteekHoogte
            cursor.updateRow(row)

    # # voeg losse lijndelen weer samen
    arcpy.Dissolve_management(waterloop_lijn_simp, "templijn", [code_waterloop,"z_nap"], "", "MULTI_PART",
                              "DISSOLVE_LINES")


    arcpy.Copy_management("templijn",waterloop_lijn_simp)

    # maak veld aan voor onderdeel-waterloop
    arcpy.AddField_management(waterloop_lijn_simp, 'onderdeel', "TEXT", field_length=50)
    arcpy.CalculateField_management(waterloop_lijn_simp, "onderdeel", "\"insteek\"", "PYTHON")

    # smooth waterloop lijn
    arcpy.SmoothLine_cartography(waterloop_lijn, "line_smooth", "PAEK", smooth, "FIXED_CLOSED_ENDPOINT", "NO_CHECK")
    with arcpy.da.UpdateCursor("line_smooth", ['z_nap']) as cursor:
        for row in cursor:
            row[0] = insteekHoogte
            cursor.updateRow(row)
    del cursor

    arcpy.AddField_management(waterloop, "insteekHoogte", "DOUBLE", 2, field_is_nullable="NULLABLE")
    with arcpy.da.UpdateCursor(waterloop, ['insteekHoogte']) as cursor:
        for row in cursor:
            row[0] = insteekHoogte
            cursor.updateRow(row)
    del cursor
    print "Gemiddelde insteekhoogte van {}m bepaald voor {}".format(insteekHoogte,waterloop)


def create_raster(waterloop,waterloop_lijn_simp, buffer_lijn, waterloop_lijn_totaal, waterloop_3d_lijn,tin, raster_waterloop,raster_waterloop_clip, bodemlijn):

    # # merge waterlooplijn met bufferlijn
    arcpy.Merge_management(["line_smooth",buffer_lijn,bodemlijn],waterloop_lijn_totaal)



    # feature to 3d
    arcpy.FeatureTo3DByAttribute_3d(waterloop_lijn_totaal, waterloop_3d_lijn, "z_nap")

    # tin
    arcpy.CreateTin_3d(tin, "", "{} z_nap Hard_Line <None>".format(waterloop_3d_lijn), "DELAUNAY")
    # tin to raster
    arcpy.TinRaster_3d(tin, raster_waterloop, "FLOAT", "LINEAR", "CELLSIZE 0,1", "1")

    # clip raster met waterloop poly en verwijder oude raster
    arcpy.Clip_management(raster_waterloop, "",
                      raster_waterloop_clip, "poly_smooth", "-3,402823e+038", "ClippingGeometry", "MAINTAIN_EXTENT")

    arcpy.Delete_management(raster_waterloop)

    rasterlijst.append(raster_waterloop_clip)

    print "Raster gemaakt voor {}".format(waterloop)

def insert_into_ahn(waterlopen, raster_ahn,rasterlijst):
    # clip totaalgebied uit ahn
    arcpy.Clip_management(raster_ahn, "", "clip_waterlopen", waterlopen, "-3,402823e+038", "NONE","MAINTAIN_EXTENT")
    rasterlijst.append("clip_waterlopen")

    # voeg lagen toe van losse waterlopen
    rasters = arcpy.ListRasters()
    for raster in rasters:
        if raster.startswith("waterloop_raster_clip"):
            rasterlijst.append(raster)
    # merge rasterlijst
    arcpy.MosaicToNewRaster_management(rasterlijst, arcpy.env.workspace, "raster_totaal",
                                       "", "32_BIT_FLOAT", "0,5", "1", "LAST", "FIRST")


def bodemlijn_bepalen(waterloop_lijn,waterloop,tolerance,dist_mini_buffer, bodemlijn):

    # waterloop buffer afronden (lijn en polygoon)
    arcpy.SmoothPolygon_cartography(waterloop, "poly_smooth", "PAEK", smooth, "FIXED_ENDPOINT", "NO_CHECK")
    # euclidean raster
    arcpy.gp.EucDistance_sa("line_smooth", "temp_euclidean", "", "0,05","")
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
    arcpy.FeatureToPolygon_management("temp_buffer_smnooth_lijn", "temp_buffer_smooth_poly")

    # clip raster met minibuffer
    # if arcpy.Exists("temp_clip"):
    #     #     arcpy.Delete_management("temp_clip")
    arcpy.Clip_management("temp_rastercalc", "", "temp_clipper", "temp_buffer_smooth_poly", "127", "ClippingGeometry", "MAINTAIN_EXTENT")
    # clip to polygon
    arcpy.RasterToPolygon_conversion("temp_clipper", "temp_poly", "SIMPLIFY", "Value")
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
    arcpy.SelectLayerByLocation_management("temp_poly_lijn_split_feat", "INTERSECT", waterloop_lijn, tolerance, "NEW_SELECTION", "INVERT")
    arcpy.CopyFeatures_management("temp_poly_lijn_split_feat", bodemlijn)

    # maak veld aan voor onderdeel-waterloop
    arcpy.AddField_management(bodemlijn, 'onderdeel', "TEXT", field_length=50)
    arcpy.CalculateField_management(bodemlijn, "onderdeel", "\"bodem\"", "PYTHON")

    # calculate z value ## temp


    # update features
    bodemHoogte = insteekHoogte-bodemDiepte
    print bodemHoogte
    arcpy.AddField_management(bodemlijn, "z_nap", "DOUBLE", 2, field_is_nullable="NULLABLE")
    with arcpy.da.UpdateCursor(bodemlijn, ["z_nap"]) as cursor:
        for row in cursor:
            row[0] = bodemHoogte
            cursor.updateRow(row)
    del cursor


    # delete features
    arcpy.Delete_management("temp_euclidean")
    arcpy.Delete_management("temp_clipper")
    arcpy.Delete_management("temp_rastercalc")

def minimale_breedte(bodemlijn):
    ## profiles along line ##
    # dissolve bodemlijn
    arcpy.Dissolve_management(bodemlijn, "tempDissolveBodemlijn", "onderdeel", "", "MULTI_PART",
                              "DISSOLVE_LINES")
    generate_profiles(5,50,50,"tempDissolveBodemlijn","onderdeel",0,"tempProfielenBodem")

    # isect profiles met line_smooth
    arcpy.Intersect_analysis(["tempProfielenBodem", "line_smooth"], "tempIsect", "ALL", "", "POINT")
    # split profiles
    arcpy.SplitLineAtPoint_management("tempProfielenBodem", "tempIsect", 'splitProfielen', 0.2)
    # select only water part
    arcpy.MakeFeatureLayer_management('splitProfielen', 'temp_splitProfielen')
    arcpy.SelectLayerByLocation_management('temp_splitProfielen', "INTERSECT", "tempDissolveBodemlijn", 0.1,
                                           "NEW_SELECTION", "")


    arcpy.CopyFeatures_management('temp_splitProfielen', 'tempWaterProfielen')

    lijstBreedtes = []
    with arcpy.da.SearchCursor("tempWaterProfielen", ["SHAPE@LENGTH"]) as cursor:
        for row in cursor:
            if row[0] > 0 and row[0] is not None:
                lijstBreedtes.append(row[0])
            else:
                pass


    gemiddeldeBreedte = round(average(lijstBreedtes),2)
    print "Gemiddelde breedte voor {} is {}m".format(waterloop,gemiddeldeBreedte)

    arcpy.AddField_management(waterloop, 'soortWaterloop', "TEXT", field_length=50)
    if gemiddeldeBreedte <= maxBreedteSmal:
        # bodemhoogte bodemlijn aanpassen
        with arcpy.da.UpdateCursor(bodemlijn, ['z_nap']) as cursor:
            for row in cursor:
                bodemHoogte = insteekHoogte-bodemDiepteSmal
                row[0] = bodemHoogte
                cursor.updateRow(row)
        del cursor
        arcpy.CalculateField_management(waterloop, "soortWaterloop", "\"smal\"", "PYTHON")
        arcpy.AddField_management(waterloop, "bodemHoogte", "DOUBLE", 2, field_is_nullable="NULLABLE")
        with arcpy.da.UpdateCursor(waterloop, ["bodemHoogte"]) as cursor:
            for row in cursor:
                row[0] = bodemHoogte
                cursor.updateRow(row)
        del cursor

    if gemiddeldeBreedte > maxBreedteSmal:
        # bodemhoogte bodemlijn aanpassen
        with arcpy.da.UpdateCursor(bodemlijn, ['z_nap']) as cursor:
            for row in cursor:
                bodemHoogte = insteekHoogte-bodemDiepte
                row[0] = bodemHoogte
                cursor.updateRow(row)
        del cursor
        arcpy.CalculateField_management(waterloop, "soortWaterloop", "\"breed\"", "PYTHON")

        arcpy.AddField_management(waterloop, "bodemHoogte", "DOUBLE", 2, field_is_nullable="NULLABLE")
        with arcpy.da.UpdateCursor(waterloop, ["bodemHoogte"]) as cursor:
            for row in cursor:
                row[0] = bodemHoogte
                cursor.updateRow(row)
        del cursor






def aggregate_input(waterlopen_invoer):
    arcpy.AggregatePolygons_cartography(waterlopen_invoer, "waterlopen_", "0,01 Meters",
                                        "0 SquareMeters", "0 SquareMeters", "NON_ORTHOGONAL", "",
                                        "temptabel")

    arcpy.AddField_management("waterlopen_", 'id_string', "TEXT", field_length=50)
    arcpy.CalculateField_management("waterlopen_", "id_string", '!OBJECTID!', "PYTHON")


    print "Aanliggende polygonen gemerged"


aggregate_input(waterlopen_invoer)
with arcpy.da.SearchCursor(waterlopen,['SHAPE@',code_waterloop]) as cursor:
    for row in cursor:
        id = row[1]

        waterloop = 'waterloop_' + str(row[1])
        waterloop_lijn = 'waterloop_lijn_' + str(row[1])
        waterloop_lijn_simp = 'waterloop_lijn_simp_' + str(row[1])
        punten_insteek = 'waterloop_punten_insteek_' + str(row[1])
        waterloop_lijn_totaal = 'tt_waterloop_lijn_' + str(row[1])
        waterloop_3d_lijn = 'waterloop_3d_lijn' + str(row[1])
        bodemlijn = "bodemlijn_waterloop_" + str(row[1])


        tin = "D:/GoogleDrive/WSRL/tin/waterloop"+str(row[1])
        raster_waterloop = 'waterloop_raster_' + str(row[1])
        raster_waterloop_clip = 'waterloop_raster_clip_' + str(row[1])
        buitenraster = 'waterloop_buitenraster_' + str(row[1])
        buffer = 'buffer_waterloop_'+str(row[1])
        buffer_lijn = 'buffer_waterloop_lijn_'+str(row[1])



        where = '"' + code_waterloop + '" = ' + "'" + str(id) + "'"

        arcpy.Select_analysis(waterlopen, waterloop, where)

        # voeg veld toe voor z_nap
        arcpy.AddField_management(waterloop,"z_nap","DOUBLE", 2, field_is_nullable="NULLABLE")


        # algemene functies runnen

        raster_buitenkant(waterloop, buffer_buitenkant, buitenraster, raster_ahn)
        bepaal_insteek_waterloop(waterloop, waterloop_lijn, waterloop_lijn_simp, punten_insteek, min_lengte_segment,code_waterloop)


        bodemlijn_bepalen(waterloop_lijn, waterloop, tolerance, dist_mini_buffer, bodemlijn)
        minimale_breedte(bodemlijn)

        buffer_waterloop(waterloop, buffer, buffer_lijn, bodemDiepte)



        create_raster(waterloop, waterloop_lijn_simp, buffer_lijn, waterloop_lijn_totaal, waterloop_3d_lijn, tin,
                      raster_waterloop, raster_waterloop_clip, bodemlijn)


        # delete globals
        try:
            talud
            del talud
        except NameError:
            pass

        try:
            bodemHoogte
            del bodemHoogte
        except NameError:
            pass

        try:
            insteekHoogte
            del insteekHoogte
        except NameError:
            pass



# insert_into_ahn(waterlopen,raster_ahn,rasterlijst)




