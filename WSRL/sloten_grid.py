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
contour_ahn = 'smooth_contour_2m'
profiel_interval = 10
profiel_lengte_land = 10
profiel_lengte_rivier = 10
min_breedte = 0.6
raster = 'ahn3clip_test'
df_breedtes = pd.DataFrame(columns=['sloot_id', 'gem_breedte'])
factor_lengte = 0.5

def knip_sloten(profielen,slootlijn,code):
    # mini-profielen voor nan-check
    generate_profiles(profiel_interval,2,2,slootlijn,code,'mini_profielen')
    arcpy.FeatureVerticesToPoints_management("mini_profielen",
                                             "mini_profielen_punten",
                                             "ALL")

    print 'mini_profielen gemaakt'






    # verwijder profiel indien middelpunt op niet-nan data ligt
    existing_fields = arcpy.ListFields(profielen)
    needed_fields = ['RASTERVALU']
    for field in existing_fields:
        if field.name in needed_fields:
            arcpy.DeleteField_management(profielen, field.name)
    arcpy.Intersect_analysis([profielen, slootlijn], 'middelpunten_profielen', "", 0.5, "point")

    arcpy.FeatureToPoint_management('middelpunten_profielen', 'middelpunten_profielen_', "CENTROID")
    ExtractValuesToPoints('middelpunten_profielen_', raster, 'middelpunten_profielen_z', "INTERPOLATE", "VALUE_ONLY")
    arcpy.JoinField_management(profielen, "profielnummer", "middelpunten_profielen_z", "profielnummer", ["RASTERVALU"])

    with arcpy.da.UpdateCursor(profielen, ['RASTERVALU']) as cursor:
        for row in cursor:
            if row[0] is not None:
                cursor.deleteRow()
            else:
                continue


    # intersect op snijpunten met gridlijnen
    intersects = [profielen,contour_ahn]
    arcpy.Intersect_analysis(intersects, 'knip_sloten_punt', "", 0, "point")
    # knip profiellijnen met intersects

    searchRadius = "0.2 Meters"
    arcpy.SplitLineAtPoint_management(profielen, 'knip_sloten_punt', 'knip_profielen', searchRadius)



    # selecteer lijndeel dat intersect met sloten
    arcpy.MakeFeatureLayer_management('knip_profielen', 'knip_profielen_temp')
    arcpy.SelectLayerByLocation_management('knip_profielen_temp', 'intersect', slootlijn)
    arcpy.CopyFeatures_management('knip_profielen_temp', 'slootbreedtes')

    # bereken gemiddelde breedte
    gem_breedte_list = []
    with arcpy.da.SearchCursor('slootbreedtes', ['sloot_id','Shape_Length']) as cursor:
        for row in cursor:
            if row[1] is not None:
                gem_breedte_list.append(row[1])
            else:
                pass

    gem_breedte = average(gem_breedte_list)
    slootnaam = id
    dct_sloot[id] = gem_breedte



    # koppel gemiddelde breedte aan sloot
    # smooth contourlines?

def knip_sloten_test(profielen,slootlijn,code):




    # verwijder profiel indien middelpunt op niet-nan data ligt
    existing_fields = arcpy.ListFields(profielen)
    needed_fields = ['RASTERVALU']
    for field in existing_fields:
        if field.name in needed_fields:
            arcpy.DeleteField_management(profielen, field.name)
    arcpy.Intersect_analysis([profielen, slootlijn], 'middelpunten_profielen', "", 0.5, "point")

    arcpy.FeatureToPoint_management('middelpunten_profielen', 'middelpunten_profielen_', "CENTROID")
    ExtractValuesToPoints('middelpunten_profielen_', raster, 'middelpunten_profielen_z', "INTERPOLATE", "VALUE_ONLY")
    arcpy.JoinField_management(profielen, "profielnummer", "middelpunten_profielen_z", "profielnummer", ["RASTERVALU"])

    with arcpy.da.UpdateCursor(profielen, ['RASTERVALU']) as cursor:
        for row in cursor:
            if row[0] is not None:
                cursor.deleteRow()
            else:
                continue




    # intersect op snijpunten met gridlijnen
    intersects = [profielen,contour_ahn]
    arcpy.Intersect_analysis(intersects, 'knip_sloten_punt', "", 0, "point")
    # knip profiellijnen met intersects

    searchRadius = "0.2 Meters"
    arcpy.SplitLineAtPoint_management(profielen, 'knip_sloten_punt', 'knip_profielen', searchRadius)



    # midpoints op splits
    arcpy.FeatureVerticesToPoints_management("knip_profielen",
                                             "knip_profielen_punten",
                                             "MID")
    # ahn values midpoints
    existing_fields = arcpy.ListFields('knip_profielen_punten')
    needed_fields = ['RASTERVALU']
    for field in existing_fields:
        if field.name in needed_fields:
            arcpy.DeleteField_management('knip_profielen_punten', field.name)


    ExtractValuesToPoints('knip_profielen_punten', raster, 'knip_profielen_punten_z', "INTERPOLATE", "VALUE_ONLY")


    # koppel non-nan aan splitlines
    existing_fields = arcpy.ListFields('knip_profielen')
    needed_fields = ['RASTERVALU']
    for field in existing_fields:
        if field.name in needed_fields:
            arcpy.DeleteField_management('knip_profielen', field.name)

    arcpy.JoinField_management('knip_profielen', "OBJECTID", "knip_profielen_punten_z", "ORIG_FID", ["RASTERVALU"])

    with arcpy.da.UpdateCursor('knip_profielen', ['RASTERVALU','Shape_Length']) as cursor:
        for row in cursor:
            if row[0] is not None or row[1] < min_breedte:
                cursor.deleteRow()
            else:
                continue

    # selecteer delen die in de buurt liggen van slootlijn
    arcpy.MakeFeatureLayer_management('knip_profielen', 'knip_profielen_temp')
    arcpy.SelectLayerByLocation_management('knip_profielen_temp', 'intersect', slootlijn,"0,5 Meters", "NEW_SELECTION", "NOT_INVERT")
    arcpy.CopyFeatures_management('knip_profielen_temp', 'slootbreedtes')

    # verwijder profielen delen die in de lengte van een sloot liggen
    arcpy.MakeFeatureLayer_management('slootbreedtes', 'slootbreedtes_temp')
    arcpy.SelectLayerByLocation_management('slootbreedtes_temp', 'intersect', 'knip_sloten_punt', "0,2 Meters", "NEW_SELECTION",
                                           "NOT_INVERT")
    arcpy.CopyFeatures_management('slootbreedtes_temp', 'slootbreedtes_aangepast')

    gemiddelde_slootlengte = []
    with arcpy.da.SearchCursor('slootbreedtes_aangepast', ['sloot_id','Shape_Length']) as cursor:
        for row in cursor:
            if row[1] is not None:
                gemiddelde_slootlengte.append(row[1])
            else:
                pass
    try:
        gemiddelde_slootlengte
        gemiddelde = average(gemiddelde_slootlengte)
        bovengrens = (gemiddelde+factor_lengte*gemiddelde)
        with arcpy.da.UpdateCursor('slootbreedtes_aangepast', ['sloot_id','Shape_Length']) as cursor:
            for row in cursor:
                if row[1] is None or row[1] > bovengrens:
                    cursor.deleteRow()
                else:
                    df_breedtes.loc[row[0]] = row[0], gemiddelde
                    continue
    except NameError:
        pass


def koppel_gem_lengtes():
    existing_fields = arcpy.ListFields('waterlopen_test')
    needed_fields = ['gem_breedte']
    for field in existing_fields:
        if field.name in needed_fields:
            arcpy.DeleteField_management('waterlopen_test', field.name)

    arcpy.AddField_management('waterlopen_test', "gem_breedte", "DOUBLE", 2, field_is_nullable="NULLABLE")

    with arcpy.da.UpdateCursor('waterlopen_test', ['sloot_id', 'gem_breedte']) as cursor:
        for row in cursor:
            slootnummer = row[0]
            for i, row in df_breedtes.iterrows():
                if row['sloot_id'] == slootnummer:
                    row[1] = round(row['gem_breedte'], 2)
                    cursor.updateRow(row)









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



            knip_sloten_test(profielen,slootlijn,code)


# profielen = 'profielen_sloot_52'
# slootlijn = 'sloot_52'
# code = 'sloot_id'
# knip_sloten_test(profielen,slootlijn,code)

iterate_sloten()
koppel_gem_lengtes()
# print df_breedtes