import arcpy
from basisfuncties import average
arcpy.env.workspace = r'D:\GoogleDrive\WSRL\test_waterlopen.gdb'
arcpy.env.overwriteOutput = True

inmetingenWaterlopen = "profielpunten_sample"
bodemDiepte = 1
waterloop = "waterloop_1"

# per waterloop
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






parameters_talud(inmetingenWaterlopen,waterloop)