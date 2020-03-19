import arcpy

arcpy.env.workspace = r'D:\GoogleDrive\WSRL\test_vergridden.gdb'
arcpy.env.overwriteOutput = True
code_waterloop = "id_string"
talud = (1.0/4.0)
delta_w = 0.8
buffer_max = 0.7
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



def vergridden_waterloop(waterloop,waterloop_lijn,waterloop_lijn_totaal,waterloop_3d_lijn, waterloop_3d_poly,tin,raster_waterloop):
    # lijn van omtrek waterloop
    arcpy.FeatureToLine_management(waterloop, waterloop_lijn)

    # merge waterlooplijn met bufferlijn
    arcpy.Merge_management([waterloop_lijn,buffer_lijn],waterloop_lijn_totaal)

    # feature to 3d
    arcpy.FeatureTo3DByAttribute_3d(waterloop_lijn_totaal, waterloop_3d_lijn, "z_nap")
    arcpy.FeatureToPolygon_management(waterloop_3d_lijn, waterloop_3d_poly)

    # tin
    arcpy.CreateTin_3d(tin, "", "{} z_nap Hard_Line <None>".format(waterloop_3d_lijn), "DELAUNAY")
    # tin to raster
    arcpy.TinRaster_3d(tin, raster_waterloop, "FLOAT", "LINEAR", "CELLSIZE 0,1", "1")

    # clip raster met waterloop poly en verwijder oude raster


with arcpy.da.SearchCursor(waterlopen,['SHAPE@',code_waterloop]) as cursor:
    for row in cursor:
        id = row[1]

        waterloop = 'waterloop_' + str(row[1])
        waterloop_lijn = 'waterloop_lijn_' + str(row[1])
        waterloop_lijn_totaal = 'tt_waterloop_lijn_' + str(row[1])
        waterloop_3d_lijn = 'waterloop_3d_lijn' + str(row[1])
        waterloop_3d_poly = 'waterloop_3d_poly' + str(row[1])


        tin = "D:/GoogleDrive/WSRL/tin/waterloop"+str(row[1])
        raster_waterloop = 'waterloop_raster_' + str(row[1])
        buffer = 'buffer_waterloop_'+str(row[1])
        buffer_lijn = 'buffer_waterloop_lijn_'+str(row[1])


        where = '"' + code_waterloop + '" = ' + "'" + str(id) + "'"

        arcpy.Select_analysis(waterlopen, waterloop, where)

        # functies runnen
        buffer_waterloop(waterloop, talud, buffer,buffer_lijn,insteek_waterloop)
        vergridden_waterloop(waterloop, waterloop_lijn, waterloop_lijn_totaal, waterloop_3d_lijn, waterloop_3d_poly, tin, raster_waterloop)








# buitencontour waterloop --> BGT omtrek
#
# buffer stapjes
# arcpy.Buffer_analysis()
