import arcpy
from basisfuncties import average
from basisfuncties import generate_profiles

arcpy.env.workspace = r'D:\GoogleDrive\WSRL\test_waterlopen.gdb'
arcpy.env.overwriteOutput = True
code_waterloop = "string_id"
raster_safe = r'C:\Users\Vincent\Desktop\ahn3clip_safe'
min_lengte_segment = 15 #?
defaultbreedte = 5 #?

# variabelen nodig voor goede run:
standaardTalud = 0.25
bodemDiepte = 1
smooth = "10 Meters"
tolerance = 0.3
dist_mini_buffer = -0.2




buffer_buitenkant = 3 # buffer voor focalraster
# insteek_waterloop = -1

waterlopen = "demoset_1"
inmetingenWaterlopen = "profielpunten_waterlopen_safe_1000m"

rasterlijst = []


def bepaal_maxbufferdist(waterloop_lijn_simp,waterloop, defaultbreedte):
    # remove sideparts
    lengtes_segmenten = []
    with arcpy.da.SearchCursor(waterloop_lijn_simp,['SHAPE@LENGTH']) as cursor:
        for row in cursor:
            lengtes_segmenten.append(row[0])

    del cursor
    gem_lengte = average(lengtes_segmenten)


    arcpy.CopyFeatures_management(waterloop_lijn_simp, 'templijn')
    with arcpy.da.UpdateCursor('templijn',['SHAPE@LENGTH']) as cursor:
        for row in cursor:
            if row[0] < gem_lengte:
                cursor.deleteRow()
    del cursor
    generate_profiles(5,20,20,'templijn',code_waterloop,0,"temp_profielen")

    # intersect punt uitvoer
    arcpy.Intersect_analysis(['temp_profielen','templijn'], "temp_isect", "ALL", "", "POINT")
    # remove punten with join count <2
    with arcpy.da.UpdateCursor('temp_isect', ['Join_Count']) as cursor:
        for row in cursor:
            if row[0] < 2:
                cursor.deleteRow()
    del cursor
    # multipoint to point
    arcpy.FeatureToPoint_management("temp_isect", "temp_isect_point")
    # point to line
    arcpy.PointsToLine_management("temp_isect_point", "temp_breedtes", "profielnummer", "", "NO_CLOSE")
    # average line length
    lijst_gemiddelde_breedte = []
    with arcpy.da.UpdateCursor("temp_breedtes", ['SHAPE@LENGTH']) as cursor:
        for row in cursor:
            if row[0] > 0:
                lijst_gemiddelde_breedte.append(row[0])
            else:
                cursor.deleteRow()
    del cursor
    global gemiddelde_breedte
    #### REMOVE 0 lengtes uit temp breedtes!!!

    if lijst_gemiddelde_breedte:
        gemiddelde_breedte = average(lijst_gemiddelde_breedte)
    else:
        gemiddelde_breedte = defaultbreedte
        print "Defaultbreedte gebruikt bij {}".format(waterloop)

    print "Gemiddelde breedte waterloop is {}".format(gemiddelde_breedte)





def buffer_waterloop(waterloop,talud, buffer, buffer_lijn, waterloop_lijn_simp):


    try:
        talud
        talud = talud
        print "talud gebruiken waterloop"
    except NameError:
        talud = standaardTalud
        print "standaard talud gebruiken"


    # buffer_max = gemiddelde_breedte/2
    buffer_max = 1
    print buffer_max, "max_bufferafstand"
    buffer_afstand_talud = abs(bodemDiepte/talud) # buffer afstand volgens talud, tot bodemdiepte


    if abs(buffer_afstand_talud) <= abs(buffer_max):
        arcpy.Buffer_analysis(waterloop_lijn_simp, buffer, buffer_afstand_talud, "RIGHT", "FLAT", "NONE", "", "PLANAR")
        gebruikte_buffer = buffer_afstand_talud
    else:
        arcpy.Buffer_analysis(waterloop_lijn_simp, buffer, buffer_max, "RIGHT", "FLAT", "NONE", "", "PLANAR")
        gebruikte_buffer = buffer_max

    # feature to line
    arcpy.FeatureToLine_management(buffer,buffer_lijn)

    # split line at vertices
    arcpy.SplitLine_management(buffer_lijn, "bufferlijn")

    # isect met simplijn
    arcpy.MakeFeatureLayer_management("bufferlijn", "temp_bufferlijn")
    arcpy.SelectLayerByLocation_management("temp_bufferlijn", 'intersect', waterloop_lijn_simp,selection_type="NEW_SELECTION",invert_spatial_relationship="INVERT")
    arcpy.CopyFeatures_management("temp_bufferlijn",buffer_lijn)

    # # remove biggest objectid
    # id_list = []
    # with arcpy.da.SearchCursor(buffer_lijn, ['OBJECTID']) as cursor:
    #     for row in cursor:
    #         id_list.append(row[0])
    # max_id = max(id_list)
    #
    # del cursor
    # with arcpy.da.UpdateCursor(buffer_lijn, ['OBJECTID']) as cursor:
    #     for row in cursor:
    #         if row[0] == max_id:
    #             cursor.deleteRow()
    #         else:
    #             pass
    # del cursor

    # bereken hoogte bufferlijn met insteek
    with arcpy.da.SearchCursor(waterloop_lijn_simp, ['z_nap']) as cursor:
        for row in cursor:
            insteek_waterloop = row[0]
            break

    if gebruikte_buffer == buffer_afstand_talud:
        # print (buffer_afstand_talud*talud), "buffer onbegrensd", waterloop_lijn_simp
        z_nap = insteek_waterloop- (buffer_afstand_talud*talud)

    elif gebruikte_buffer == buffer_max:
        # print (buffer_max * talud), "buffer begrensd", waterloop_lijn_simp
        global zBodem
        zBodem = insteek_waterloop- (buffer_max*talud)

    else:
        print "Er is een probleem bij {} !".format(waterloop_lijn_simp)


    with arcpy.da.UpdateCursor(buffer_lijn, ['z_nap']) as cursor:
        for row in cursor:
            row[0] = zBodem
            cursor.updateRow(row)
    del cursor

    # maak veld aan voor onderdeel-waterloop
    arcpy.AddField_management(buffer_lijn, 'onderdeel', "TEXT", field_length=50)
    arcpy.CalculateField_management(buffer_lijn, "onderdeel", "\"onderkant_talud\"", "PYTHON")

    print "Binnen-buffer gemaakt voor {}".format(waterloop)


def raster_buitenkant(waterloop, buffer_buitenkant, buitenraster, raster_safe):
    # buffer waterloop
    arcpy.Buffer_analysis(waterloop, "temp_buffer_wl", buffer_buitenkant, "OUTSIDE_ONLY", "FLAT", "NONE", "", "PLANAR")
    # raster clippen met bufferzone
    arcpy.Clip_management(raster_safe, "",
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



                # if lijst_z:
                #     row[1] = average(lijst_z)
                #     cursor.updateRow(row)

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


    print "Gemiddelde insteekhoogte bepaald voor {}".format(waterloop)


def create_raster(waterloop,waterloop_lijn_simp, buffer_lijn, waterloop_lijn_totaal, waterloop_3d_lijn,tin, raster_waterloop,raster_waterloop_clip, bodemlijn):

    # # merge waterlooplijn met bufferlijn
    arcpy.Merge_management([waterloop_lijn_simp,buffer_lijn,bodemlijn],waterloop_lijn_totaal)



    # feature to 3d
    arcpy.FeatureTo3DByAttribute_3d(waterloop_lijn_totaal, waterloop_3d_lijn, "z_nap")

    # tin
    arcpy.CreateTin_3d(tin, "", "{} z_nap Hard_Line <None>".format(waterloop_3d_lijn), "DELAUNAY")
    # tin to raster
    arcpy.TinRaster_3d(tin, raster_waterloop, "FLOAT", "LINEAR", "CELLSIZE 0,1", "1")

    # clip raster met waterloop poly en verwijder oude raster
    arcpy.Clip_management(raster_waterloop, "",
                      raster_waterloop_clip, waterloop, "-3,402823e+038", "ClippingGeometry", "MAINTAIN_EXTENT")

    arcpy.Delete_management(raster_waterloop)

    rasterlijst.append(raster_waterloop_clip)

    print "Raster gemaakt voor {}".format(waterloop)

def insert_into_ahn(waterlopen, raster_safe,rasterlijst):
    # clip totaalgebied uit ahn
    arcpy.Clip_management(raster_safe, "", "clip_waterlopen", waterlopen, "-3,402823e+038", "NONE","MAINTAIN_EXTENT")
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

    #vlak naar lijn vertalen
    # arcpy.FeatureToLine_management(waterloop, waterloop_lijn)
    # waterloop buffer afronden (lijn en polygoon)
    arcpy.SmoothLine_cartography(waterloop_lijn, "line_smooth", "PAEK", smooth, "FIXED_CLOSED_ENDPOINT", "NO_CHECK")
    arcpy.SmoothPolygon_cartography(waterloop, "poly_smooth", "PAEK", smooth, "FIXED_ENDPOINT", "NO_CHECK")
    # euclidean raster
    arcpy.gp.EucDistance_sa("line_smooth", "temp_euclidean", "", "0,01","")
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
    arcpy.SelectLayerByLocation_management("temp_poly_lijn_split_feat", "INTERSECT", waterloop_lijn, tolerance, "NEW_SELECTION", "INVERT")
    arcpy.CopyFeatures_management("temp_poly_lijn_split_feat", bodemlijn)

    # maak veld aan voor onderdeel-waterloop
    arcpy.AddField_management(bodemlijn, 'onderdeel', "TEXT", field_length=50)
    arcpy.CalculateField_management(bodemlijn, "onderdeel", "\"bodem\"", "PYTHON")

    # calculate z value ## temp
    # print zBodem
    arcpy.AddField_management(bodemlijn, "z_nap", "DOUBLE", 2, field_is_nullable="NULLABLE")
    with arcpy.da.UpdateCursor(bodemlijn, ["z_nap"]) as cursor:
        for row in cursor:
            row[0] = zBodem
            cursor.updateRow(row)

    # arcpy.CalculateField_management(bodemlijn, "z_nap", "\"{}\"".format(temp_bodemhoogte), "PYTHON")
    # # arcpy.CalculateField_management(bodemlijn, "z_nap", temp_bodemhoogte, "PYTHON")

def parameters_talud(inmetingenWaterlopen,waterloop):

    # select nearest waterloop
    # near
    arcpy.Near_analysis(waterloop, inmetingenWaterlopen, "", "NO_LOCATION", "NO_ANGLE", "PLANAR")

    # select meetpunten met near-fid
    arcpy.SpatialJoin_analysis(waterloop, inmetingenWaterlopen, "temp_nearest", "JOIN_ONE_TO_ONE", "KEEP_ALL", "",
                               match_option="CLOSEST")


    # get profielnummer
    with arcpy.da.SearchCursor("temp_nearest", ["PROFIELNR"]) as cursor:
        for row in cursor:
            profielNummer = row[0]

    # select waterloop
    arcpy.MakeFeatureLayer_management(inmetingenWaterlopen, "temp_inmetingen")
    arcpy.SelectLayerByAttribute_management("temp_inmetingen", 'NEW_SELECTION',
                                            "PROFIELNR = '{}'".format(profielNummer))
    arcpy.CopyFeatures_management("temp_inmetingen", 'waterloop_near')
    profiel = "waterloop_near"

    # bereken bodemhoogte
    with arcpy.da.SearchCursor(profiel, ["PROFIELNR","MEETPUNT","HOOGTE","AFSTAND"]) as cursor:
        for row in cursor:
            if row[1] == "Laagste punt":
                bodemHoogte = row[2]
                break
    try:
        bodemHoogte
        print bodemHoogte
        # bereken gemiddelde bodembreedte
        lijstBodembreedtes = []
        with arcpy.da.SearchCursor(profiel, ["PROFIELNR", "MEETPUNT", "HOOGTE", "AFSTAND"]) as cursor:
            for row in cursor:
                if row[2] <= bodemHoogte + 0.2:
                    lijstBodembreedtes.append(row[3])

        if lijstBodembreedtes:
            minimum = min(lijstBodembreedtes)
            maximum = max(lijstBodembreedtes)
            bodemBreedte = abs(minimum - maximum)
            print bodemBreedte

        # bereken breedte op waterloop
        counter = 0
        lijstWaterspiegelBreedtes = []
        with arcpy.da.SearchCursor(profiel, ["PROFIELNR", "MEETPUNT", "HOOGTE", "AFSTAND"]) as cursor:
            for row in cursor:
                if row[1] == "Waterspiegel" and counter < 2:
                    lijstWaterspiegelBreedtes.append(row[3])
                    counter += 1
        print lijstWaterspiegelBreedtes
        if lijstWaterspiegelBreedtes:
            if len(lijstWaterspiegelBreedtes) == 2:
                waterspiegelBreedte = average(lijstWaterspiegelBreedtes)
            else:
                print "Waterspiegel is niet berekend, andere waarde nodig"

        # bereken talud
        try:
            bodemHoogte, bodemBreedte, waterspiegelBreedte
            horizontaal = abs(bodemBreedte - waterspiegelBreedte) / 2

            # set global
            global talud
            talud = bodemDiepte / horizontaal  # waarde aanpassen
            print talud

        except NameError:
            print "Waardes ontbreken voor taludberekening"

    except NameError:
        print "Geen bodemhoogte gevonden"





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

        raster_buitenkant(waterloop, buffer_buitenkant, buitenraster, raster_safe)
        bepaal_insteek_waterloop(waterloop, waterloop_lijn, waterloop_lijn_simp, punten_insteek, min_lengte_segment,code_waterloop)
        # bepaal_maxbufferdist(waterloop_lijn_simp,waterloop,defaultbreedte)
        parameters_talud(inmetingenWaterlopen,waterloop)
        buffer_waterloop(waterloop, talud, buffer, buffer_lijn, waterloop_lijn_simp)

        bodemlijn_bepalen(waterloop_lijn,waterloop,tolerance,dist_mini_buffer,bodemlijn)
        create_raster(waterloop, waterloop_lijn_simp, buffer_lijn, waterloop_lijn_totaal, waterloop_3d_lijn, tin,
                      raster_waterloop, raster_waterloop_clip, bodemlijn)


        # delete globals
        del talud, zBodem

# insert_into_ahn(waterlopen,raster_safe,rasterlijst)




