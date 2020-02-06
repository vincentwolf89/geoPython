import arcpy
from basisfuncties import*

arcpy.env.workspace = r'D:\Projecten\WSRL\safe_temp.gdb'
arcpy.env.overwriteOutput = True

trajecten = r'D:\Projecten\WSRL\safe_basis.gdb\priovakken_test'


code_wsrl = "prio_nummer"

buffer_afstand = 50
buffer_afstand_panden = 500
buffer_afstand_panden_bit = 20
buffer_afstand_go = 100

dpiplaag = r'D:\Projecten\WSRL\safe_basis.gdb\dpip_bit'
zettinglaag = r'D:\Projecten\WSRL\safe_basis.gdb\zetting_buk'
kabels_leidingen = r'D:\Projecten\WSRL\safe_basis.gdb\kabels_leidingen_safe'
panden = r'D:\Projecten\WSRL\safe_basis.gdb\panden_bag'
dijkzone = r'D:\Projecten\WSRL\safe_basis.gdb\bit_but_zone'
binnenteenlijn = r'D:\Projecten\WSRL\safe_basis.gdb\binnenteenlijn_safe'
extra_go = r'D:\Projecten\WSRL\safe_basis.gdb\go_oktober_2019'
versterkingen = r'D:\Projecten\WSRL\safe_basis.gdb\versterkingen_safe'
resultaten = r'D:\Projecten\WSRL\safe_basis.gdb\resultaten_vvk'



profiel_interval = 25
stapgrootte_punten = 1
profiel_lengte_land = 200
profiel_lengte_rivier = 100 # 10 default


excelmap = 'D:/Projecten/WSRL/safe/uitvoer_priovakken/' # gewenste map voor .xlsx-uitvoer
raster = r'C:\Users\Vincent\Desktop\ahn3clip_safe' # hoogtegrid
toetspeil = 999 # naam van kolom met toetspeil/toetshoogte, 999 voor uitvoer zonder toetspeil
min_plot = -50
max_plot = 100
profielen_mg = 'profielen_mg'
naam_totaalprofielen = 'prioprofielen_safe_jan2020'
totaal_profielen =[]




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
    # print gem_dpip, var_dpip
    del cursor
    # koppel gem_dpip en var_dpip aan deeltraject
    arcpy.AddField_management(trajectlijn, "gem_dpip", "DOUBLE", 2, field_is_nullable="NULLABLE")
    arcpy.AddField_management(trajectlijn, "var_dpip", "DOUBLE", 2, field_is_nullable="NULLABLE")

    try:
        gem_dpip
        with arcpy.da.UpdateCursor(trajectlijn, ['gem_dpip','var_dpip']) as cursor:
            for row in cursor:
                row[0] = gem_dpip
                row[1] = var_dpip
                cursor.updateRow(row)
        del cursor
    except NameError:
        pass

    # schoonmaken
    arcpy.DeleteFeatures_management(buffer)
    arcpy.DeleteFeatures_management("bufferzone")
    arcpy.Delete_management("temp_stat")

    print "Dikte deklaag gekoppeld"

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
    # print gem_zet, var_zet
    del cursor
    # koppel gem_zet en var_zet aan deeltraject
    arcpy.AddField_management(trajectlijn, "gem_zet", "DOUBLE", 2, field_is_nullable="NULLABLE")
    arcpy.AddField_management(trajectlijn, "var_zet", "DOUBLE", 2, field_is_nullable="NULLABLE")

    try:
        gem_zet
        with arcpy.da.UpdateCursor(trajectlijn, ['gem_zet','var_zet']) as cursor:
            for row in cursor:
                row[0] = gem_zet
                row[1] = var_zet
                cursor.updateRow(row)
        del cursor
    except NameError:
        pass


    # schoonmaken
    arcpy.DeleteFeatures_management(buffer)
    arcpy.DeleteFeatures_management("bufferzone")
    arcpy.Delete_management("temp_stat")

    print "Zetting gekoppeld"

def koppel_panden_dijk(trajectlijn, dijkzone, panden, buffer_afstand_panden, panden_dijkzone):
    # select panden features in dijkvlak, totaal
    arcpy.MakeFeatureLayer_management(panden, 'templaag_panden')
    arcpy.SelectLayerByLocation_management('templaag_panden', "INTERSECT", dijkzone, "0 Meters", "NEW_SELECTION", "NOT_INVERT")
    arcpy.CopyFeatures_management('templaag_panden', 'panden_dijkzone')

    # bufferzone trajectlijn voor panden
    arcpy.Buffer_analysis(trajectlijn, 'bufferzone', buffer_afstand_panden, "FULL", "FLAT", "NONE", "", "PLANAR")

    # select panden features from panden dijkzone in bufferzone
    arcpy.MakeFeatureLayer_management("panden_dijkzone", 'templaag_panden_dijkzone')
    arcpy.SelectLayerByLocation_management('templaag_panden_dijkzone', "INTERSECT", "bufferzone", "0 Meters", "NEW_SELECTION","NOT_INVERT")
    arcpy.CopyFeatures_management('templaag_panden_dijkzone', panden_dijkzone)

    # koppel aantal panden in dijkzone aan traject
    aantal_panden_ = arcpy.GetCount_management(panden_dijkzone)
    aantal_panden = aantal_panden_[0]
    arcpy.AddField_management(trajectlijn, "panden_dijkzone", "DOUBLE", 2, field_is_nullable="NULLABLE")

    with arcpy.da.UpdateCursor(trajectlijn, 'panden_dijkzone') as cursor:
        for row in cursor:
            row[0] = aantal_panden
            cursor.updateRow(row)
    del cursor

    arcpy.DeleteFeatures_management(panden_dijkzone)

    print "Panden dijkzone gekoppeld"

def koppel_panden_bitplus_20(trajectlijn, dijkzone, panden, buffer_afstand_panden_bit, panden_dijkzone_bit,binnenteenlijn, binnenteen_traject,code_wsrl,id):

    ## knip deel binnenteenlijn
    # buffer
    arcpy.Buffer_analysis(trajectlijn, 'bufferzone', buffer_afstand_panden, "FULL", "FLAT", "NONE", "", "PLANAR")
    # isect bit
    arcpy.MakeFeatureLayer_management(binnenteenlijn, 'templaag_binnenteen')
    arcpy.Intersect_analysis(["templaag_binnenteen","bufferzone"], "binnenteen_traject_temp", "ALL", "", "LINE")

    # afvangen loze lijnsecties
    arcpy.FeatureVerticesToPoints_management("binnenteen_traject_temp", "punten_temp", "BOTH_ENDS")
    arcpy.SplitLineAtPoint_management("binnenteen_traject_temp", "punten_temp", binnenteen_traject,"1 Meters")
    arcpy.Near_analysis(trajectlijn, binnenteen_traject, "", "NO_LOCATION", "NO_ANGLE", "PLANAR")
    # zoek near fid
    with arcpy.da.SearchCursor(trajectlijn, 'NEAR_FID') as cursor:
        for row in cursor:
            near_fid = int(row[0])

    # verwijder niet-near-fid
    with arcpy.da.UpdateCursor(binnenteen_traject, "OBJECTID") as cursor:
        for row in cursor:
            if int(row[0]) == near_fid:
                pass
            else:
                cursor.deleteRow()



    # buffer bit 20m
    arcpy.Buffer_analysis(binnenteen_traject, 'bufferzone', buffer_afstand_panden_bit, "LEFT", "FLAT", "NONE", "", "PLANAR")

    # select panden features from panden dijkzone in bufferzone
    arcpy.MakeFeatureLayer_management(panden, 'templaag_panden')
    arcpy.SelectLayerByLocation_management('templaag_panden', "INTERSECT", "bufferzone", "0 Meters", "NEW_SELECTION","NOT_INVERT")
    arcpy.CopyFeatures_management('templaag_panden', panden_dijkzone_bit)

    # koppel aantal panden in dijkzone aan traject
    aantal_panden_ = arcpy.GetCount_management(panden_dijkzone_bit)
    aantal_panden = aantal_panden_[0]
    arcpy.AddField_management(trajectlijn, "panden_dijkzone_bit", "DOUBLE", 2, field_is_nullable="NULLABLE")

    with arcpy.da.UpdateCursor(trajectlijn, 'panden_dijkzone_bit') as cursor:
        for row in cursor:
            row[0] = aantal_panden
            cursor.updateRow(row)

    del cursor

    arcpy.DeleteField_management(trajectlijn, ['NEAR_FID','NEAR_DIST'])

    # sommeren?

    # arcpy.DeleteFeatures_management(panden_dijkzone_bit)
    # arcpy.DeleteFeatures_management(binnenteen_traject)

    print "Panden bitzone gekoppeld"


def koppel_kl(trajectlijn, kabels_leidingen, buffer_afstand, buffer):
    # aantal meter kl in buffer traject
    arcpy.Buffer_analysis(trajectlijn, 'bufferzone', buffer_afstand, "FULL", "ROUND", "NONE", "", "PLANAR")
    # select kabels en leidingen features in buffer
    arcpy.MakeFeatureLayer_management(kabels_leidingen, 'templaag_kl')
    arcpy.SelectLayerByLocation_management('templaag_kl', "INTERSECT", 'bufferzone', "0 Meters", "NEW_SELECTION", "NOT_INVERT")
    arcpy.CopyFeatures_management('templaag_kl', buffer)


    # bereken totaal aantal kl in buffer
    arcpy.Statistics_analysis(buffer, "temp_stat", "Shape_Length SUM", "")
    with arcpy.da.SearchCursor("temp_stat", 'SUM_Shape_Length') as cursor:
        for row in cursor:
            tot_kl = row[0]
            print tot_kl


    arcpy.AddField_management(trajectlijn, "lengte_kl", "DOUBLE", 2, field_is_nullable="NULLABLE")


    try:
        tot_kl
        with arcpy.da.UpdateCursor(trajectlijn, 'lengte_kl') as cursor:
            for row in cursor:
                row[0] = tot_kl
                cursor.updateRow(row)
        del cursor
    except NameError:
        pass


    # schoonmaken
    arcpy.DeleteFeatures_management(buffer)

    print "Kabels en leidingen gekoppeld"

def koppel_go(trajectlijn, extra_go, buffer_afstand_go, buffer):
    # buffer priovak
    arcpy.Buffer_analysis(trajectlijn, 'bufferzone', buffer_afstand_go, "FULL", "FLAT", "NONE", "", "PLANAR")

    # select zetting features in buffer
    arcpy.MakeFeatureLayer_management(extra_go, 'templaag_go')
    arcpy.SelectLayerByLocation_management('templaag_go', "INTERSECT", 'bufferzone', "0 Meters", "NEW_SELECTION", "NOT_INVERT")
    arcpy.CopyFeatures_management('templaag_go', buffer)


    # koppel aantal panden in dijkzone aan traject
    aantal_go_ = arcpy.GetCount_management(buffer)
    aantal_go = aantal_go_[0]
    arcpy.AddField_management(trajectlijn, "extra_go", "DOUBLE", 2, field_is_nullable="NULLABLE")

    try:
        aantal_go
        with arcpy.da.UpdateCursor(trajectlijn, 'extra_go') as cursor:
            for row in cursor:
                row[0] = aantal_go
                cursor.updateRow(row)
        del cursor
    except NameError:
        pass


    # schoonmaken
    arcpy.DeleteFeatures_management(buffer)
    arcpy.DeleteFeatures_management("bufferzone")
    arcpy.Delete_management("temp_stat")

    print "Grondonderzoek gekoppeld"

def koppel_versterkingen(trajectlijn, versterkingen):
    arcpy.Near_analysis(trajectlijn, versterkingen, "5 Meters", "NO_LOCATION", "NO_ANGLE", "PLANAR")

    # zoek near fid
    with arcpy.da.SearchCursor(trajectlijn, 'NEAR_FID') as cursor:
        for row in cursor:
            near_fid = int(row[0])



    # test of near aanwezig is
    if near_fid > -1:

        # maak templaag voor veiliger werken
        arcpy.MakeFeatureLayer_management(versterkingen, 'templaag_versterkingen')

        # join field based on near fid - OID
        arcpy.JoinField_management(trajectlijn, 'NEAR_FID', 'templaag_versterkingen', 'OBJECTID_1', ['TRAJECT','OPLEVERING'])
        arcpy.AlterField_management(trajectlijn, 'TRAJECT', 'traject')
        arcpy.AlterField_management(trajectlijn, 'OPLEVERING', 'oplevering')


        arcpy.DeleteField_management(trajectlijn, ['NEAR_FID', 'NEAR_DIST'])
    else:
        pass


    print "Versterkingen gekoppeld"
def koppel_resultaten(trajectlijn,resultaten):

    arcpy.JoinField_management(trajectlijn, code_wsrl, resultaten, 'dijkvak', ['gekb_2023','stph_2023','stbi_2023'])

    print "Resultaten gekoppeld"


with arcpy.da.SearchCursor(trajecten,['SHAPE@',code_wsrl]) as cursor:
    for row in cursor:
        code = code_wsrl
        id = row[1]

        profielen = 'profielen_' + str(row[1])
        profielen_plus = 'profielen_plus' + str(row[1])
        uitvoerpunten = 'punten_profielen_z_' + str(row[1])
        excel = excelmap + 'priovak_' + str(row[1]) + '.xlsx'


        trajectlijn = 'deeltraject_' + str(row[1])
        buffer_dpip = 'buffer_dpip_' + str(row[1])
        buffer_zet = 'buffer_zet_' + str(row[1])
        buffer_kl = 'buffer_kl_' + str(row[1])
        buffer_go = 'buffer_go_' + str(row[1])
        panden_dijkzone = 'panden_dijkzone_' + str(row[1])
        panden_dijkzone_bit = 'panden_dijkzone_bit_' + str(row[1])
        binnenteen_traject = 'binnenteen_' + str(row[1])
        where = '"' + code_wsrl + '" = ' + "'" + str(id) + "'"


        # selecteer betreffend traject
        arcpy.Select_analysis(trajecten, trajectlijn, where)

        # doorlopen scripts
        print trajectlijn
        koppel_dpip(trajectlijn,dpiplaag,buffer_afstand,buffer_dpip)
        koppel_zetting(trajectlijn, zettinglaag, buffer_afstand, buffer_zet)
        koppel_panden_dijk(trajectlijn, dijkzone, panden, buffer_afstand_panden, panden_dijkzone)
        koppel_panden_bitplus_20(trajectlijn, dijkzone, panden, buffer_afstand_panden_bit, panden_dijkzone_bit,
                                 binnenteenlijn, binnenteen_traject, code_wsrl, id)
        koppel_kl(trajectlijn, kabels_leidingen, buffer_afstand, buffer_kl)
        koppel_go(trajectlijn, extra_go, buffer_afstand_go, buffer_go)
        koppel_versterkingen(trajectlijn,versterkingen)
        koppel_resultaten(trajectlijn,resultaten)


        # generate_profiles(profiel_interval, profiel_lengte_land, profiel_lengte_rivier, trajectlijn, code_wsrl,toetspeil, profielen)
        # join_mg_profiles(trajectlijn,profielen,profielen_mg,profielen_plus)
        # copy_trajectory_lr(trajectlijn, code_wsrl)
        # set_measurements_trajectory(profielen_plus, trajectlijn, code_wsrl, stapgrootte_punten,toetspeil)
        # extract_z_arcpy(invoerpunten, uitvoerpunten, raster)
        # add_xy(uitvoerpunten, code_wsrl)
        # excel_writer_factsheets(uitvoerpunten, code, excel, id,trajecten,toetspeil,min_plot,max_plot,trajectlijn)


