import arcpy

arcpy.env.workspace = r'D:\Projecten\WSRL\safe_temp.gdb'
arcpy.env.overwriteOutput = True

trajecten = r'D:\Projecten\WSRL\safe_basis.gdb\priovakken_test'
code_wsrl = "prio_nummer"

buffer_afstand = 50
buffer_afstand_panden = 500
dpiplaag = r'D:\Projecten\WSRL\safe_basis.gdb\dpip_bit'
zettinglaag = r'D:\Projecten\WSRL\safe_basis.gdb\zetting_buk'
panden = r'D:\Projecten\WSRL\safe_basis.gdb\panden_bag'
dijkzone = r'D:\Projecten\WSRL\safe_basis.gdb\bit_but_zone'

def koppel_dpip(trajectlijn, dpiplaag, buffer_afstand, buffer):
    # buffer priovak
    arcpy.Buffer_analysis(trajectlijn, 'bufferzone', buffer_afstand, "FULL", "ROUND", "NONE", "", "PLANAR")

    # select dpip features in buffer
    arcpy.MakeFeatureLayer_management(dpiplaag, 'templaag_dpip')
    arcpy.SelectLayerByLocation_management('templaag_dpip', "INTERSECT", 'bufferzone', "0 Meters", "NEW_SELECTION", "NOT_INVERT")
    arcpy.CopyFeatures_management('templaag_dpip', buffer)

    # bereken gemiddelde dikte dpip en variantie
    arcpy.Statistics_analysis(buffer, "temp_stat", "dikte_deklaag MEAN;dikte_deklaag RANGE", "")
    with arcpy.da.SearchCursor("temp_stat", ['MEAN_dikte_deklaag','RANGE_dikte_deklaag']) as cursor:
        for row in cursor:
            gem_dpip, var_dpip = round(row[0],2),round(row[1],2)
    print gem_dpip, var_dpip
    del cursor
    # koppel gem_dpip en var_dpip aan deeltraject
    arcpy.AddField_management(trajectlijn, "gem_dpip", "DOUBLE", 2, field_is_nullable="NULLABLE")
    arcpy.AddField_management(trajectlijn, "var_dpip", "DOUBLE", 2, field_is_nullable="NULLABLE")

    with arcpy.da.UpdateCursor(trajectlijn, ['gem_dpip','var_dpip']) as cursor:
        for row in cursor:
            row[0] = gem_dpip
            row[1] = var_dpip
            cursor.updateRow(row)
    del cursor

    # schoonmaken
    arcpy.DeleteFeatures_management(buffer)
    arcpy.DeleteFeatures_management("bufferzone")
    arcpy.Delete_management("temp_stat")

def koppel_zetting(trajectlijn, zettinglaag, buffer_afstand, buffer):
    # buffer priovak
    arcpy.Buffer_analysis(trajectlijn, 'bufferzone', buffer_afstand, "FULL", "ROUND", "NONE", "", "PLANAR")

    # select zetting features in buffer
    arcpy.MakeFeatureLayer_management(zettinglaag, 'templaag_zetting')
    arcpy.SelectLayerByLocation_management('templaag_zetting', "INTERSECT", 'bufferzone', "0 Meters", "NEW_SELECTION", "NOT_INVERT")
    arcpy.CopyFeatures_management('templaag_zetting', buffer)

    # bereken gemiddelde zetting en variantie
    arcpy.Statistics_analysis(buffer, "temp_stat", "velocity MEAN;velocity RANGE", "")
    with arcpy.da.SearchCursor("temp_stat", ['MEAN_velocity','RANGE_velocity']) as cursor:
        for row in cursor:
            gem_zet, var_zet = round(row[0],2),round(row[1],2)
    print gem_zet, var_zet
    del cursor
    # koppel gem_zet en var_zet aan deeltraject
    arcpy.AddField_management(trajectlijn, "gem_zet", "DOUBLE", 2, field_is_nullable="NULLABLE")
    arcpy.AddField_management(trajectlijn, "var_zet", "DOUBLE", 2, field_is_nullable="NULLABLE")

    with arcpy.da.UpdateCursor(trajectlijn, ['gem_zet','var_zet']) as cursor:
        for row in cursor:
            row[0] = gem_zet
            row[1] = var_zet
            cursor.updateRow(row)
    del cursor

    # schoonmaken
    arcpy.DeleteFeatures_management(buffer)
    arcpy.DeleteFeatures_management("bufferzone")
    arcpy.Delete_management("temp_stat")

def koppel_panden_dijk(trajectlijn, dijkzone, panden, buffer_afstand_panden, panden_dijkzone):
    # select panden features in dijkvlak, totaal
    arcpy.MakeFeatureLayer_management(panden, 'templaag_panden')
    arcpy.SelectLayerByLocation_management('templaag_panden', "INTERSECT", dijkzone, "0 Meters", "NEW_SELECTION", "NOT_INVERT")
    arcpy.CopyFeatures_management('templaag_panden', 'panden_dijkzone')

    # bufferzone trajectlijn voor panden
    arcpy.Buffer_analysis(trajectlijn, 'bufferzone', buffer_afstand_panden, "FULL", "FLAT", "NONE", "", "PLANAR")

    # select panden features from panden dijkzone in bufferzone
    arcpy.MakeFeatureLayer_management("panden_dijkzone", 'templaag_panden_dijkzone')
    arcpy.SelectLayerByLocation_management('templaag_panden_dijkzone', "INTERSECT", "bufferzone" "0 Meters", "NEW_SELECTION",
                                           "NOT_INVERT")
    arcpy.CopyFeatures_management('templaag_panden', panden_dijkzone)



with arcpy.da.SearchCursor(trajecten,['SHAPE@',code_wsrl]) as cursor:
    for row in cursor:
        code = code_wsrl
        id = row[1]
        trajectlijn = 'deeltraject_' + str(row[1])
        buffer_dpip = 'buffer_dpip' + str(row[1])
        buffer_zet = 'buffer_zet' + str(row[1])
        panden_dijkzone = 'panden_dijkzone_' + str(row[1])
        where = '"' + code_wsrl + '" = ' + "'" + str(id) + "'"


        # selecteer betreffend traject
        arcpy.Select_analysis(trajecten, trajectlijn, where)

        # doorlopen scripts
        print trajectlijn
        # koppel_dpip(trajectlijn,dpiplaag,buffer_afstand,buffer_dpip)
        # koppel_zetting(trajectlijn, zettinglaag, buffer_afstand, buffer_zet)
        koppel_panden_dijk(trajectlijn, dijkzone, panden, buffer_afstand_panden, panden_dijkzone)


