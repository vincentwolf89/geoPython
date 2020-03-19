import arcpy
from basisfuncties import average

arcpy.env.workspace = r'D:\GoogleDrive\WSRL\test_vergridden.gdb'
arcpy.env.overwriteOutput = True
code_waterloop = "id_string"
raster_safe = r'C:\Users\Vincent\Desktop\ahn3clip_safe'
talud = (1.0/4.0)
delta_w = 0.8
buffer_max = 0.7

buffer_buitenkant = 3 # buffer voor focalraster
insteek_waterloop = -1

waterlopen = "waterlopen_samples"

def buffer_waterloop(waterloop,talud, buffer, buffer_lijn, insteek_waterloop):

    buffer_afstand_talud = abs(delta_w/talud) # buffer afstand volgens talud, tot bodemdiepte


    if abs(buffer_afstand_talud) <= abs(buffer_max):
        arcpy.Buffer_analysis(waterloop, buffer, -buffer_afstand_talud, "OUTSIDE_ONLY", "FLAT", "NONE", "", "PLANAR")
        gebruikte_buffer = buffer_afstand_talud
    else:
        arcpy.Buffer_analysis(waterloop, buffer, -buffer_max, "OUTSIDE_ONLY", "FLAT", "NONE", "", "PLANAR")
        gebruikte_buffer = buffer_max

    # feature to line
    arcpy.FeatureToLine_management(buffer,buffer_lijn)

    # remove biggest objectid
    id_list = []
    with arcpy.da.SearchCursor(buffer_lijn, ['OBJECTID']) as cursor:
        for row in cursor:
            id_list.append(row[0])
    max_id = max(id_list)

    del cursor
    with arcpy.da.UpdateCursor(buffer_lijn, ['OBJECTID']) as cursor:
        for row in cursor:
            if row[0] == max_id:
                cursor.deleteRow()
            else:
                pass
    del cursor

    # bereken hoogte bufferlijn

    if gebruikte_buffer == buffer_afstand_talud:
        print (buffer_afstand_talud*talud), "buffer onbegrensd", waterloop
        z_nap = insteek_waterloop- (buffer_afstand_talud*talud)

    elif gebruikte_buffer == buffer_max:
        print (buffer_max * talud), "buffer begrensd", waterloop
        z_nap = insteek_waterloop- (buffer_max*talud)

    else:
        print "Er is een probleem bij {} !".format(waterloop)


    with arcpy.da.UpdateCursor(buffer_lijn, ['z_nap']) as cursor:
        for row in cursor:
            row[0] = z_nap
            cursor.updateRow(row)
    del cursor


## hier wordt een breder raster gemaakt aan de buitenkant voor zoveel mogelijk geldende z-waardes
def raster_buitenkant(waterloop, buffer_buitenkant, buitenraster, raster_safe):
    # buffer waterloop
    arcpy.Buffer_analysis(waterloop, "temp_buffer_wl", buffer_buitenkant, "OUTSIDE_ONLY", "FLAT", "NONE", "", "PLANAR")
    # raster clippen met bufferzone
    arcpy.Clip_management(raster_safe, "",
                          "temp_raster_buitenkant", "temp_buffer_wl", "-3,402823e+038", "ClippingGeometry", "MAINTAIN_EXTENT")
    # focal stats op bufferclip
    arcpy.gp.FocalStatistics_sa("temp_raster_buitenkant", buitenraster, "Rectangle 4 4 CELL", "MEAN", "DATA")





def vergridden_waterloop(waterloop,waterloop_lijn,waterloop_lijn_totaal,waterloop_3d_lijn,tin,raster_waterloop,raster_waterloop_clip, waterloop_lijn_simp, punten_insteek):

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

    with arcpy.da.UpdateCursor(waterloop_lijn_simp, ['SHAPE@', 'z_nap']) as cursor:

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

                if aantal_nan/aantal_z > 0.25:
                    print "Aansluiting eruitgehaald"
                    cursor.deleteRow()


    # koppel gemiddelde hoogte van 10 laagste punten aan lijnstukken als z-waarde






    # # merge waterlooplijn met bufferlijn
    # arcpy.Merge_management([waterloop_lijn,buffer_lijn],waterloop_lijn_totaal)
    #
    # # feature to 3d
    # arcpy.FeatureTo3DByAttribute_3d(waterloop_lijn_totaal, waterloop_3d_lijn, "z_nap")
    #
    # # tin
    # arcpy.CreateTin_3d(tin, "", "{} z_nap Hard_Line <None>".format(waterloop_3d_lijn), "DELAUNAY")
    # # tin to raster
    # arcpy.TinRaster_3d(tin, raster_waterloop, "FLOAT", "LINEAR", "CELLSIZE 0,1", "1")
    #
    # # clip raster met waterloop poly en verwijder oude raster
    # arcpy.Clip_management(raster_waterloop, "",
    #                       raster_waterloop_clip, waterloop, "-3,402823e+038", "ClippingGeometry", "MAINTAIN_EXTENT")
    #
    # arcpy.Delete_management(raster_waterloop)

with arcpy.da.SearchCursor(waterlopen,['SHAPE@',code_waterloop]) as cursor:
    for row in cursor:
        id = row[1]

        waterloop = 'waterloop_' + str(row[1])
        waterloop_lijn = 'waterloop_lijn_' + str(row[1])
        waterloop_lijn_simp = 'waterloop_lijn_simp_' + str(row[1])
        punten_insteek = 'waterloop_punten_insteek_' + str(row[1])
        waterloop_lijn_totaal = 'tt_waterloop_lijn_' + str(row[1])
        waterloop_3d_lijn = 'waterloop_3d_lijn' + str(row[1])
        waterloop_3d_poly = 'waterloop_3d_poly' + str(row[1])


        tin = "D:/GoogleDrive/WSRL/tin/waterloop"+str(row[1])
        raster_waterloop = 'waterloop_raster_' + str(row[1])
        raster_waterloop_clip = 'waterloop_raster_clip_' + str(row[1])
        buitenraster = 'waterloop_buitenraster_' + str(row[1])
        buffer = 'buffer_waterloop_'+str(row[1])
        buffer_lijn = 'buffer_waterloop_lijn_'+str(row[1])


        where = '"' + code_waterloop + '" = ' + "'" + str(id) + "'"

        arcpy.Select_analysis(waterlopen, waterloop, where)

        # functies runnen
        buffer_waterloop(waterloop, talud, buffer,buffer_lijn,insteek_waterloop)
        raster_buitenkant(waterloop, buffer_buitenkant, buitenraster, raster_safe)
        vergridden_waterloop(waterloop,waterloop_lijn,waterloop_lijn_totaal,waterloop_3d_lijn,tin,raster_waterloop,raster_waterloop_clip, waterloop_lijn_simp, punten_insteek)








# buitencontour waterloop --> BGT omtrek
#
# buffer stapjes
# arcpy.Buffer_analysis()
