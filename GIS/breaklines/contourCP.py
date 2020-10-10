import arcpy
import matplotlib.pyplot as plt 
import pandas as pd
import numpy as np
from itertools import groupby
sys.path.append('.')
from basisfuncties import average, splitByAttributes
from arcpy.sa import *


arcpy.env.overwriteOutput = True


taludValue = 0.06
taludDistance = "1 Meters"
taludDistance2 = "1,5 Meters"
pointDistance = 0.5




inritDistance = 3 #meter
pandDistance = 2 #meter 

diepteSmal = 0.5
diepteBreed = 1 
standaardTalud = 0.5 #1/2
breedteSmal = 3

# minLengteTalud = 1.5 #meter wordt niet meer gebruikt! 





# invoer hdsr
workspaceProfielen = r"D:\Projecten\HDSR\2020\gisData\testbatchGrechtkade.gdb"
arcpy.env.workspace = r"D:\Projecten\HDSR\2020\gisData\testbatchGrechtkade.gdb"



minLengteTaludBasis = 1 # meter

hoogtedata = r"D:\Projecten\HDSR\2020\gisData\basisData.gdb\BAG2mPlusWaterlopenAHN3"
trajectLijn = r"D:\Projecten\HDSR\2020\gisData\basisData.gdb\RWK_areaal_2024"

bgtPanden = r"D:\Projecten\HDSR\2020\gisData\basisData.gdb\bgt_pand"
bgtWaterdelen = r"D:\Projecten\HDSR\2020\gisData\basisData.gdb\bgt_waterdeel"
bgtWaterdelenOndersteunend = r"D:\Projecten\HDSR\2020\gisData\basisData.gdb\bgt_ondersteunendWaterdeel"
bgtWaterdelenTotaal = r"D:\Projecten\HDSR\2020\gisData\basisData.gdb\bgt_waterdeel_totaal"
bgtWegdelen = r"D:\Projecten\HDSR\2020\gisData\basisData.gdb\bgt_wegdeel"
bgtWegdelenInritten = r"D:\Projecten\HDSR\2020\gisData\basisData.gdb\bgt_wegdeel_inritten"

profielen = 'profiel49'
outputFigures = r"C:\Users\Vincent\Desktop\cPointsFiguresGrechtkade"


# # invoer safe
# workspaceProfielen = r"D:\Projecten\HDSR\2020\gisData\testbatchSafe.gdb"
# arcpy.env.workspace = r"D:\Projecten\HDSR\2020\gisData\testbatchSafe.gdb"

# minLengteTaludBasis = 3 # meter

# hoogtedata = r"D:\Projecten\WSRL\safe\waterlopenSafe300m.gdb\waterlopen300mTotaalFocal3m"
# trajectLijn = r"D:\GoogleDrive\WSRL\safe_basis.gdb\buitenkruinlijn_safe_wsrl"

# bgtPanden = r"D:\GoogleDrive\WSRL\safe_basis.gdb\panden_bag"
# bgtWaterdelen = r"D:\GoogleDrive\WSRL\safe_basis.gdb\bgt_waterdeel_500m"
# bgtWaterdelenOndersteunend = r"D:\GoogleDrive\WSRL\safe_basis.gdb\bgt_ondersteunend_waterdeel_500m"
# bgtWaterdelenTotaal = r"D:\GoogleDrive\WSRL\safe_basis.gdb\bgt_waterdelen_safe_totaal"
# bgtWegdelen = r"D:\GoogleDrive\WSRL\safe_basis.gdb\bgt_wegdelen_500m"
# bgtWegdelenInritten = r"D:\GoogleDrive\WSRL\safe_basis.gdb\bgt_wegdelen_inritten_500m"

# profielen = 'profielenSafeTest2'
# outputFigures = r"C:\Users\Vincent\Desktop\cPointsFiguresSafe"








profielVelden = ['SHAPE@','profielnummer']
spatialRef = arcpy.Describe(profielen).spatialReference



   




def profielControle(profiel):
    # check op huizen in profiel

    arcpy.MakeFeatureLayer_management(bgtPanden, 'tempPanden') 
    arcpy.SelectLayerByLocation_management('tempPanden', "INTERSECT", profiel, pandDistance, "NEW_SELECTION", "NOT_INVERT")
    pandIsects = int(arcpy.GetCount_management("tempPanden").getOutput(0))



    if pandIsects > 0:
        print ("Profiel snijdt met geregistreerd(e) pand(en), berekening voor profiel .. afbreken")
        return ("STOP")
        
    else:
        #check op inrit

        arcpy.MakeFeatureLayer_management(bgtWegdelenInritten, 'tempInritten') 
        arcpy.SelectLayerByLocation_management('tempInritten', "INTERSECT", profiel, inritDistance, "NEW_SELECTION", "NOT_INVERT")
        inritIsects = int(arcpy.GetCount_management("tempInritten").getOutput(0))


        if inritIsects > 0:
            print ("Profiel snijdt met geregistreerde inrit(ten), berekening voor profiel .. afbreken")
            return ("STOP")

        else:
            
            # check op wegdeel aan landzijde profiel 
            arcpy.FeatureVerticesToPoints_management(profiel, "startPointLand", "START")
            arcpy.MakeFeatureLayer_management(bgtWegdelen, 'tempWegdelen') 
            arcpy.SelectLayerByLocation_management('tempWegdelen', "INTERSECT", "startPointLand", "", "NEW_SELECTION", "NOT_INVERT")
            wegdeelIsects = int(arcpy.GetCount_management("tempWegdelen").getOutput(0))

            if wegdeelIsects > 0:
                print ("Profiel snijdt met geregistreerd(e) wegdeel/wegdelen, berekening voor profiel .. afbreken")
                return ("STOP")
            
            else:
                print ("Geen belemmeringen gevonden voor verdere berekeningen")
                return ("DOORGAAN")





def taludDelen(profiel):
    taludLijnLijst = []
    taludPuntLijst = []
    

    # raster clippen op profiel
    arcpy.Buffer_analysis(profiel, "bufferProfiel", "15 Meters", "FULL", "FLAT", "NONE", "", "PLANAR")
    arcpy.Clip_management(hoogtedata,"", "testClip", "bufferProfiel", "-3,402823e+038", "ClippingGeometry", "MAINTAIN_EXTENT")

    # focal op clip
    arcpy.gp.FocalStatistics_sa("testClip", "testClipFocal", "Rectangle 3 3 CELL", "MEAN", "DATA")

    # contour op focal
    arcpy.Contour_3d("testClipFocal", "testClipFocalContour", "0,01", "0", "1")

    # intersect op profiel en focal
    arcpy.Intersect_analysis([profiel,"testClipFocalContour"], "testIsectFocal", "ALL", "", "POINT")
    arcpy.MultipartToSinglepart_management("testIsectFocal","testIsectFocalPoint")


    # maak route van profiel
    veldenProfiel = [f.name for f in arcpy.ListFields(profiel)]
    veldenRoute = ["van","tot"]
    for veld in veldenRoute:
        if veld in veldenProfiel:
            pass
        else: 
            arcpy.AddField_management(profiel,veld,"DOUBLE", 2, field_is_nullable="NULLABLE")

    profielCursor = arcpy.da.UpdateCursor(profiel, ["van","tot","SHAPE@LENGTH"])
    for row in profielCursor:
        lengte = row[2]
        row[0] = 0
        row[1] = lengte
        profielCursor.updateRow(row)

    
    
    arcpy.CreateRoutes_lr(profiel, "RID", 'testRoute',"TWO_FIELDS", "van", "tot", "UPPER_LEFT", "1", "0", "IGNORE", "INDEX")

    # localiseer isect over route
    arcpy.LocateFeaturesAlongRoutes_lr("testIsectFocalPoint", "testRoute", "rid", "0,1 Meters", "testOutTable", "RID POINT MEAS", "FIRST", "DISTANCE", "ZERO", "FIELDS", "M_DIRECTON")

    arcpy.JoinField_management("testIsectFocalPoint","OBJECTID","testOutTable","OBJECTID","MEAS")


    # zoek over intersect naar punten op afstand van .. m 

        


    fc = "testIsectFocalPoint"
    fields = ['OID@',"MEAS","vorigeWaarde","verschilWaarde","groupNr"]

    arcpy.Sort_management(fc, "testIsectFocalPoint_", "MEAS")



    fc = "testIsectFocalPoint_"

    arcpy.AddField_management(fc,"vorigeWaarde","DOUBLE", 2, field_is_nullable="NULLABLE")
    arcpy.AddField_management(fc,"verschilWaarde","DOUBLE", 2, field_is_nullable="NULLABLE")
    arcpy.AddField_management(fc,"groupNr","DOUBLE", 2, field_is_nullable="NULLABLE")



                
    with arcpy.da.UpdateCursor(fc, fields) as cursor:

                
        p = cursor.next()[1] # eerste waarde

        value = 1

        for row in cursor:
            c = row[1] # volgende waarde
            if abs(c-p) <= taludValue:
                row[4] = value
                cursor.updateRow(row)
            else:
                value+=1
                # print "Nieuwe volumegroep gemaakt op profiel, g"
                # pass

            p = row[1]

            row[4] = value
            cursor.updateRow(row)

    del cursor



    # maak losse delen van groepen met meer dan x leden 

    volgordeTalud = 1


    with arcpy.da.UpdateCursor(fc, fields) as cursor:
                for k, g in groupby(cursor, lambda x: x[4]):
                    
                    items = []
                    measList = []

                    for row in g:
                        items.append(row[0])
                    
                    if len(items) > 5:
                        
                        taludDeel = "taludDeel_{}".format(volgordeTalud)
                        arcpy.CopyFeatures_management(fc, taludDeel)
                        taludCursor = arcpy.da.UpdateCursor(taludDeel,fields)

                        for row in taludCursor:
                            if row[0] in items:
                                measList.append(row[1])
                            else:
                                taludCursor.deleteRow()




                        

                        # maak taludlijn
                        arcpy.PointsToLine_management(taludDeel, taludDeel+"_lijn", "groupNr", "MEAS", "NO_CLOSE")
                        taludLijnLijst.append(taludDeel+"_lijn")

                        # bereken gemiddelde MEAS voor localisatie taludeel
                        arcpy.AddField_management(taludDeel+"_lijn","avMEAS","DOUBLE", 2, field_is_nullable="NULLABLE")
                        averageMEAS = average(measList)
                        taludDeelCursor = arcpy.da.UpdateCursor(taludDeel+"_lijn",["avMEAS"])
                        for row in taludDeelCursor:
                            row[0] = averageMEAS
                            taludDeelCursor.updateRow(row)
                        # print ("gemiddelde MEAS is {}".format(averageMEAS))
                        


                        # maak uiteindes talud (knikpunten)
                        arcpy.FeatureVerticesToPoints_management(taludDeel+"_lijn", taludDeel+"_eindpunten", "BOTH_ENDS")
                        taludPuntLijst.append(taludDeel+"_eindpunten")

                        volgordeTalud +=1
                        
                        print taludDeel
    if taludLijnLijst:
        arcpy.Merge_management(taludLijnLijst,"taludLijnenTotaal")
        arcpy.Merge_management(taludPuntLijst,"taludPuntenTotaal")
        
    else:
        return ("STOP")
                   


    del taludLijnLijst
    del taludPuntLijst








def getKruin(profiel): 
    ## aanpassing kruinbepalen:
    # intersect trajectlijn met profiel
    arcpy.Intersect_analysis([profiel,trajectLijn], "kruinPunt", "ALL", "", "POINT")

    
    #split profiel met bestaande knikpunten
    arcpy.SplitLineAtPoint_management(profiel, "taludPuntenTotaal", "splitProfielDelen", 1)

    # selecteer niet hellende delen van profiel
    arcpy.MakeFeatureLayer_management("splitProfielDelen", "temp_splitProfielDelen") 
   
    arcpy.SelectLayerByLocation_management("temp_splitProfielDelen", "WITHIN", "taludLijnenTotaal", "", "NEW_SELECTION", "INVERT")
    arcpy.CopyFeatures_management("temp_splitProfielDelen", "profielDelenVlak")

    # selecteer niet hellende deel dat dichtste bij isectpunt ligt (near)
    arcpy.Near_analysis("kruinPunt", "profielDelenVlak", "", "NO_LOCATION", "NO_ANGLE", "PLANAR")

    # gebruik NEAR_FID 
    tempNEARList = [z[0] for z in arcpy.da.SearchCursor ("kruinPunt", ["NEAR_FID"])]
    for item in tempNEARList:
        nearFID = int(item)

    arcpy.CopyFeatures_management("profielDelenVlak", "kruinLijn")
    # select OBJECTID met NEAR_FID waarde uit profielDelenVlak
    kruinCursor = arcpy.da.UpdateCursor("kruinLijn",["OBJECTID"])
    for row in kruinCursor:
        if int(row[0]) == nearFID:
            pass
        else:
            kruinCursor.deleteRow()

    
    # where = '"' + "OBJECTID" + '" = ' + "'" + str(nearFID) + "'"
    # arcpy.Select_analysis("profielDelenVlak", "kruinLijn", where)


    # binnen- en buitenkruin bepalen (profielen liggen van binnen naar buiten)
    arcpy.FeatureVerticesToPoints_management("kruinLijn", "binnenkruin", "START")
    arcpy.FeatureVerticesToPoints_management("kruinLijn", "buitenkruin", "END")

    # lokaliseer binnenkruin
    arcpy.LocateFeaturesAlongRoutes_lr("binnenkruin", "testRoute", "rid", "0,1 Meters", "bitTable", "RID POINT MEAS", "FIRST", "DISTANCE", "ZERO", "FIELDS", "M_DIRECTON")
    arcpy.JoinField_management("binnenkruin","OBJECTID","bitTable","OBJECTID","MEAS")

    # lokaliseer buitenkruin
    arcpy.LocateFeaturesAlongRoutes_lr("buitenkruin", "testRoute", "rid", "0,1 Meters", "butTable", "RID POINT MEAS", "FIRST", "DISTANCE", "ZERO", "FIELDS", "M_DIRECTON")
    arcpy.JoinField_management("buitenkruin","OBJECTID","butTable","OBJECTID","MEAS")


    
    # voeg bikPunten toe aan profiel
    bikCursor = arcpy.da.InsertCursor(outPath, ['cPoint','SHAPE@XY'])
    xyBikList = [z[0] for z in arcpy.da.SearchCursor ("binnenkruin", ["SHAPE@XY"])]
    for bikPunt in xyBikList:
        iRow = ['binnenkruin', bikPunt]
        print iRow, bikPunt
        bikCursor.insertRow(iRow)

    del bikCursor
    # voeg bukPunten toe aan profiel
    bukCursor = arcpy.da.InsertCursor(outPath, ['cPoint','SHAPE@XY'])
    xyBukList = [z[0] for z in arcpy.da.SearchCursor ("buitenkruin", ["SHAPE@XY"])]
    for bukPunt in xyBukList:
        iRow = ['buitenkruin', bukPunt]
        print iRow, bukPunt
        bukCursor.insertRow(iRow)

    del bukCursor


def voorbewerkingTest(profiel):

    # lokaliseer profieldelen op binnenkant-buitenkant
    bitCursor = arcpy.da.SearchCursor("binnenkruin","MEAS")
    for row in bitCursor:
        bikMEAS = row[0]
    del bitCursor
    butCursor = arcpy.da.SearchCursor("buitenkruin","MEAS")
    for row in butCursor:
        bukMEAS = row[0]
    del butCursor


    arcpy.AddField_management("taludLijnenTotaal", "locatie", "TEXT", field_length=200)
    taludLijstCursor = arcpy.da.UpdateCursor("taludLijnenTotaal",["avMEAS","locatie"])
    for row in taludLijstCursor:
        if row[0] < bikMEAS:
            row[1] = "binnenzijde"
        if row[0] > bukMEAS:
            row[1] = "buitenzijde"

        taludLijstCursor.updateRow(row)

    del taludLijstCursor  


    ## voorbewerking taluddelen############


    # knip slootdelen af
    # knip profiel op waterlopen, alleen deel overhouden dat tussen waterlopen in ligt en dus snijdt met trajectlijn
    arcpy.Intersect_analysis([profiel,bgtWaterdelenTotaal], "isectWaterlopen", "ALL", "", "POINT")
    arcpy.SplitLineAtPoint_management(profiel, "isectWaterlopen", "splitProfielWaterloop", 1)


    arcpy.MakeFeatureLayer_management("splitProfielWaterloop", "temp_splitProfielWaterloop") 
    arcpy.SelectLayerByLocation_management("temp_splitProfielWaterloop", "INTERSECT", trajectLijn, "", "NEW_SELECTION", "NOT_INVERT")
    arcpy.CopyFeatures_management("temp_splitProfielWaterloop", "profielDeelBasis")

    # knip taluddelen af die niet in profielDeelBasis liggen
    
    arcpy.SplitLineAtPoint_management("taludLijnenTotaal", "isectWaterlopen", "splitTaludLijnenTotaal", 1)
    arcpy.MakeFeatureLayer_management("splitTaludLijnenTotaal", "temp_splitTaludLijnenTotaal")


    arcpy.SelectLayerByLocation_management("temp_splitTaludLijnenTotaal", "WITHIN", "profielDeelBasis", "", "NEW_SELECTION", "NOT_INVERT")
    arcpy.CopyFeatures_management("temp_splitTaludLijnenTotaal", "taludLijnenProfielBasis")

    # controle op helling taluddelen
    taludDelenLos = splitByAttributes("taludLijnenProfielBasis","groupNr")


    
    print len(taludDelenLos), taludDelenLos

    # controle taluds
    if taludDelenLos:
        allTaludPoints = []
        binnenTaludLijnen = []
        buitenTaludLijnen = []

        for item in taludDelenLos:
            allTaludPoints.append(item+"Point")

        for item in taludDelenLos:
            # lijndeel naar punten
            tempTalud = item+"Point"
            
            arcpy.FeatureVerticesToPoints_management(item, tempTalud, "BOTH_ENDS")
            # punten lokaliseren op route
            arcpy.LocateFeaturesAlongRoutes_lr(tempTalud, "testRoute", "rid", "0,1 Meters", "tempTaludTable", "RID POINT MEAS", "FIRST", "DISTANCE", "ZERO", "FIELDS", "M_DIRECTON")
            arcpy.JoinField_management(tempTalud,"OBJECTID","tempTaludTable","OBJECTID","MEAS")

            # hoogtewaarde aan punten koppelen
            tempTaludZ = item+"PointZ"
            arcpy.CheckOutExtension("Spatial")
            ExtractValuesToPoints(tempTalud, hoogtedata, tempTaludZ,"INTERPOLATE", "VALUE_ONLY")
            arcpy.AlterField_management(tempTaludZ, 'RASTERVALU', 'z_ahn')

            # koppel aan contourwaardes en geef z-waarde contour-waarde indien niet aanwezig (raster nodata)
            arcpy.SpatialJoin_analysis(tempTaludZ, "testIsectFocalPoint_", tempTalud, "JOIN_ONE_TO_ONE", "KEEP_ALL","","CLOSEST", "", "")
            taludCursor = arcpy.da.UpdateCursor(tempTalud,["z_ahn","Contour"])
            for row in taludCursor:
                if row[0] == None:
                    row[0] = row[1]
                    taludCursor.updateRow(row)
            del taludCursor
        
        
        
        ## controle op verloop toepassen
        buitenTaluds = []
        binnenTaluds = []
        for item in allTaludPoints:
            itemCursor = arcpy.da.SearchCursor(item,"locatie")
            for row in itemCursor:
                if row[0] == "buitenzijde":
                    buitenTaluds.append(item)
                    break
                if row[0]=="binnenzijde":
                    binnenTaluds.append(item)
                    break

  
        # controle verloop 
        if binnenTaluds:
            for talud in binnenTaluds:

                zList = [z[0] for z in arcpy.da.SearchCursor (talud, ["z_ahn"])] 
                measList = [z[0] for z in arcpy.da.SearchCursor (talud, ["MEAS"])] 
                maxZ = round(max(zList),2)
                minZ = round(min(zList),2)
                maxMeas = round(max(measList),2)
                minMeas = round(min(measList),2)

                
                taludCursor = arcpy.da.SearchCursor(talud,["MEAS","z_ahn"])
                taludCheck = False
                for row in taludCursor:
                    if (round(row[0],2) == minMeas) and (round(row[1],2) == minZ):
                        taludCheck = True
                    if (round(row[0],2) == maxMeas) and (round(row[1],2) == maxZ):
                        taludCheck = True

                
                if taludCheck is True:
                    pass
                else:
                    arcpy.Delete_management(talud)
                    binnenTaluds.remove(talud)
                    print talud, " is verwijderd vanwege foutief verloop"

            # vul schone lijst met lijnen zodat near kan worden toegepast
            # binnenTaludLijnen = []
            for talud in binnenTaluds:
                taludLijn = talud.strip("Point")
                binnenTaludLijnen.append(taludLijn)
            
            for item in binnenTaludLijnen:
                arcpy.Near_analysis(item, binnenTaludLijnen, taludDistance, "NO_LOCATION", "NO_ANGLE", "PLANAR")

                itemCursor = arcpy.da.SearchCursor(item,["NEAR_FID"])
                for row in itemCursor:
                    nearFID = row[0]

                del itemCursor

                if nearFID is not -1:
                    itemCursor = arcpy.da.SearchCursor(item,["NEAR_FC"])
                    for row in itemCursor:
                        nearFC = row[0]
                    
                    del itemCursor

                    nearFC = nearFC.split("\\")[-1]
                    arcpy.Merge_management([item,nearFC],"tempMerge")
                    arcpy.FeatureVerticesToPoints_management("tempMerge", "tempTaludPoints", "BOTH_ENDS")


                    # endpoints
                    
                    arcpy.LocateFeaturesAlongRoutes_lr("tempTaludPoints", "testRoute", "rid", "0,1 Meters", "tempTaludPointsTable", "RID POINT MEAS", "FIRST", "DISTANCE", "ZERO", "FIELDS", "M_DIRECTON")
                    arcpy.JoinField_management("tempTaludPoints","OBJECTID","tempTaludPointsTable","OBJECTID","MEAS")
                    minMeas = min([z[0] for z in arcpy.da.SearchCursor ("tempTaludPoints", ["MEAS"])])
                    minMeas = round(minMeas,2) 
                    maxMeas = max([z[0] for z in arcpy.da.SearchCursor ("tempTaludPoints", ["MEAS"])]) 
                    maxMeas = round(maxMeas,2)

                    endPoints = [minMeas,maxMeas]

                    tempCursor = arcpy.da.UpdateCursor("tempTaludPoints","MEAS")
                    for tempRow in tempCursor:
                        print round(tempRow[0],2)
                        if round(tempRow[0],2) in endPoints:
                            pass
                        else:
                            tempCursor.deleteRow()
                    
                    del tempCursor
                    arcpy.PointsToLine_management("tempTaludPoints", item, "locatie", "", "NO_CLOSE")

                    # bereken gemiddelde MEAS voor nieuwe deel
                    arcpy.AddField_management(item,"avMEAS","DOUBLE", 2, field_is_nullable="NULLABLE")
                    averageMEAS = average(endPoints)
                    taludDeelCursor = arcpy.da.UpdateCursor(item,["avMEAS"])
                    for avRow in taludDeelCursor:
                        avRow[0] = averageMEAS
                        taludDeelCursor.updateRow(avRow)

                    del taludDeelCursor
                    
                


            



                    arcpy.Delete_management(nearFC)
                    binnenTaludLijnen.remove(nearFC)






            # schoonmaken en samenvoegen binnentaludlijnen
            if binnenTaludLijnen:
                for item in binnenTaludLijnen:
                    fields = [f.name for f in arcpy.ListFields(item)]
                    delFields = ["groupNr","NEAR_FC","NEAR_FID","NEAR_DIST","splitID"]
                    
                    for field in fields:
                        if field in delFields:
                            arcpy.DeleteField_management(item,field)
                        else:
                            pass
                
                arcpy.Merge_management(binnenTaludLijnen, "binnenTaludLijnen")

        if buitenTaluds:
            for talud in buitenTaluds:

                zList = [z[0] for z in arcpy.da.SearchCursor (talud, ["z_ahn"])] 
                measList = [z[0] for z in arcpy.da.SearchCursor (talud, ["MEAS"])] 
                maxZ = round(max(zList),2)
                minZ = round(min(zList),2)
                maxMeas = round(max(measList),2)
                minMeas = round(min(measList),2)

                
                taludCursor = arcpy.da.SearchCursor(talud,["MEAS","z_ahn"])
                taludCheck = False
                for row in taludCursor:
                    if (round(row[0],2) == minMeas) and (round(row[1],2) == maxZ):
                        taludCheck = True
                    if (round(row[0],2) == maxMeas) and (round(row[1],2) == minZ):
                        taludCheck = True

                
                if taludCheck is True:
                    pass
                else:
                    arcpy.Delete_management(talud)
                    buitenTaluds.remove(talud)
                    print talud, " is verwijderd vanwege foutief verloop"

            # vul schone lijst met lijnen zodat near kan worden toegepast
            # buitenTaludLijnen = []
            for talud in buitenTaluds:
                taludLijn = talud.strip("Point")
                buitenTaludLijnen.append(taludLijn)
            
            for item in buitenTaludLijnen:
                print item, "buitentalud"
                arcpy.Near_analysis(item, buitenTaludLijnen, taludDistance, "NO_LOCATION", "NO_ANGLE", "PLANAR")

                itemCursor = arcpy.da.SearchCursor(item,["NEAR_FID"])
                for row in itemCursor:
                    nearFID = row[0]

                del itemCursor

                if nearFID is not -1:
                    itemCursor = arcpy.da.SearchCursor(item,["NEAR_FC"])
                    for row in itemCursor:
                        nearFC = row[0]
                    
                    del itemCursor
                    nearFC = nearFC.split("\\")[-1]
                    arcpy.Merge_management([item,nearFC],"tempMerge")
                    arcpy.FeatureVerticesToPoints_management("tempMerge", "tempTaludPoints", "BOTH_ENDS")


                    # endpoints
                    
                    arcpy.LocateFeaturesAlongRoutes_lr("tempTaludPoints", "testRoute", "rid", "0,1 Meters", "tempTaludPointsTable", "RID POINT MEAS", "FIRST", "DISTANCE", "ZERO", "FIELDS", "M_DIRECTON")
                    arcpy.JoinField_management("tempTaludPoints","OBJECTID","tempTaludPointsTable","OBJECTID","MEAS")
                    minMeas = min([z[0] for z in arcpy.da.SearchCursor ("tempTaludPoints", ["MEAS"])])
                    minMeas = round(minMeas,2) 
                    maxMeas = max([z[0] for z in arcpy.da.SearchCursor ("tempTaludPoints", ["MEAS"])]) 
                    maxMeas = round(maxMeas,2)

                    endPoints = [minMeas,maxMeas]

                    tempCursor = arcpy.da.UpdateCursor("tempTaludPoints","MEAS")
                    for tempRow in tempCursor:
                        print round(tempRow[0],2)
                        if round(tempRow[0],2) in endPoints:
                            pass
                        else:
                            tempCursor.deleteRow()
                    
                    del tempCursor
                    arcpy.PointsToLine_management("tempTaludPoints", item, "locatie", "", "NO_CLOSE")

                    # bereken gemiddelde MEAS voor nieuwe deel
                    arcpy.AddField_management(item,"avMEAS","DOUBLE", 2, field_is_nullable="NULLABLE")
                    averageMEAS = average(endPoints)
                    taludDeelCursor = arcpy.da.UpdateCursor(item,["avMEAS"])
                    for avRow in taludDeelCursor:
                        avRow[0] = averageMEAS
                        taludDeelCursor.updateRow(avRow)

                    del taludDeelCursor
                    
                


            



                    arcpy.Delete_management(nearFC)
                    buitenTaludLijnen.remove(nearFC)






            # schoonmaken en samenvoegen binnentaludlijnen
            if buitenTaludLijnen:
                for item in buitenTaludLijnen:
                    fields = [f.name for f in arcpy.ListFields(item)]
                    delFields = ["groupNr","NEAR_FC","NEAR_FID","NEAR_DIST","splitID"]
                    
                    for field in fields:
                        if field in delFields:
                            arcpy.DeleteField_management(item,field)
                        else:
                            pass
                
                arcpy.Merge_management(buitenTaludLijnen, "buitenTaludLijnen")
                


    # indien meer dan 2 taluddelen, voeg twee dichtstbijzijnde delen samen o.b.v. taludDistance2
    if binnenTaludLijnen:
        if len(binnenTaludLijnen) > 2: 
            print "Tweede samenvoeging uitvoeren binnekant met {} meter".format(taludDistance2)
            for item in binnenTaludLijnen:
                arcpy.Near_analysis(item, binnenTaludLijnen, taludDistance2, "NO_LOCATION", "NO_ANGLE", "PLANAR")

                itemCursor = arcpy.da.SearchCursor(item,["NEAR_FID"])
                for row in itemCursor:
                    nearFID = row[0]

                del itemCursor

                if nearFID is not -1:
    
                    itemCursor = arcpy.da.SearchCursor(item,["NEAR_FC"])
                    for row in itemCursor:
                        nearFC = row[0]
                    
                    del itemCursor

                    nearFC = nearFC.split("\\")[-1]
                    arcpy.Merge_management([item,nearFC],"tempMerge")
                    arcpy.FeatureVerticesToPoints_management("tempMerge", "tempTaludPoints", "BOTH_ENDS")


                    arcpy.LocateFeaturesAlongRoutes_lr("tempTaludPoints", "testRoute", "rid", "0,1 Meters", "tempTaludPointsTable", "RID POINT MEAS", "FIRST", "DISTANCE", "ZERO", "FIELDS", "M_DIRECTON")
                    arcpy.JoinField_management("tempTaludPoints","OBJECTID","tempTaludPointsTable","OBJECTID","MEAS")
                    minMeas = min([z[0] for z in arcpy.da.SearchCursor ("tempTaludPoints", ["MEAS"])])
                    minMeas = round(minMeas,2) 
                    maxMeas = max([z[0] for z in arcpy.da.SearchCursor ("tempTaludPoints", ["MEAS"])]) 
                    maxMeas = round(maxMeas,2)

                    endPoints = [minMeas,maxMeas]

                    tempCursor = arcpy.da.UpdateCursor("tempTaludPoints","MEAS")
                    for tempRow in tempCursor:
                        print round(tempRow[0],2)
                        if round(tempRow[0],2) in endPoints:
                            pass
                        else:
                            tempCursor.deleteRow()
                    
                    del tempCursor
                    arcpy.PointsToLine_management("tempTaludPoints", item, "locatie", "", "NO_CLOSE")

                    # bereken gemiddelde MEAS voor nieuwe deel
                    arcpy.AddField_management(item,"avMEAS","DOUBLE", 2, field_is_nullable="NULLABLE")
                    averageMEAS = average(endPoints)
                    taludDeelCursor = arcpy.da.UpdateCursor(item,["avMEAS"])
                    for avRow in taludDeelCursor:
                        avRow[0] = averageMEAS
                        taludDeelCursor.updateRow(avRow)

                    del taludDeelCursor
                    

                    arcpy.Delete_management(nearFC)
                    binnenTaludLijnen.remove(nearFC)

                    # stoppen met samenvoegen als twee delen over zijn 
                    if len(binnenTaludLijnen) == 2:
                        # test voor samenvallen met waterloopIsect
                        break
    
    if buitenTaludLijnen:                
        if len(buitenTaludLijnen) > 2: 
            print "Tweede samenvoeging uitvoeren buitenkant met {} meter".format(taludDistance2)
            print buitenTaludLijnen, "buitentaludlijnenlijst"
            for item in buitenTaludLijnen:

                

                arcpy.Near_analysis(item, buitenTaludLijnen, taludDistance2, "NO_LOCATION", "NO_ANGLE", "PLANAR")

                itemCursor = arcpy.da.SearchCursor(item,["NEAR_FID"])
                for row in itemCursor:
                    nearFID = row[0]

                del itemCursor

                if nearFID is not -1:
            
                    itemCursor = arcpy.da.SearchCursor(item,["NEAR_FC"])
                    for row in itemCursor:
                        nearFC = row[0]
                    
                    del itemCursor

                    nearFC = nearFC.split("\\")[-1]
                    arcpy.Merge_management([item,nearFC],"tempMerge")
                    arcpy.FeatureVerticesToPoints_management("tempMerge", "tempTaludPoints", "BOTH_ENDS")


                    arcpy.LocateFeaturesAlongRoutes_lr("tempTaludPoints", "testRoute", "rid", "0,1 Meters", "tempTaludPointsTable", "RID POINT MEAS", "FIRST", "DISTANCE", "ZERO", "FIELDS", "M_DIRECTON")
                    arcpy.JoinField_management("tempTaludPoints","OBJECTID","tempTaludPointsTable","OBJECTID","MEAS")
                    minMeas = min([z[0] for z in arcpy.da.SearchCursor ("tempTaludPoints", ["MEAS"])])
                    minMeas = round(minMeas,2) 
                    maxMeas = max([z[0] for z in arcpy.da.SearchCursor ("tempTaludPoints", ["MEAS"])]) 
                    maxMeas = round(maxMeas,2)

                    endPoints = [minMeas,maxMeas]

                    tempCursor = arcpy.da.UpdateCursor("tempTaludPoints","MEAS")
                    for tempRow in tempCursor:
                        print round(tempRow[0],2)
                        if round(tempRow[0],2) in endPoints:
                            pass
                        else:
                            tempCursor.deleteRow()
                    
                    del tempCursor
                    arcpy.PointsToLine_management("tempTaludPoints", item, "locatie", "", "NO_CLOSE")

                    # bereken gemiddelde MEAS voor nieuwe deel
                    arcpy.AddField_management(item,"avMEAS","DOUBLE", 2, field_is_nullable="NULLABLE")
                    averageMEAS = average(endPoints)
                    taludDeelCursor = arcpy.da.UpdateCursor(item,["avMEAS"])
                    for avRow in taludDeelCursor:
                        avRow[0] = averageMEAS
                        taludDeelCursor.updateRow(avRow)

                    del taludDeelCursor
                    

                    arcpy.Delete_management(nearFC)
                    buitenTaludLijnen.remove(nearFC)

                    # stoppen met samenvoegen als twee delen over zijn 
                    if len(buitenTaludLijnen) == 2:
                        # test voor samenvallen met waterloopIsect
                        break

    
    if binnenTaludLijnen and buitenTaludLijnen:
        taludLijnen = binnenTaludLijnen+buitenTaludLijnen
        arcpy.Merge_management(taludLijnen,"taludLijnenTotaal")
        print "Taludlijnen aan beide kanten gevonden"
        return "DOORGAAN"

    if buitenTaludLijnen and not binnenTaludLijnen:
    
        taludLijnen = buitenTaludLijnen
        arcpy.Merge_management(taludLijnen,"taludLijnenTotaal")
        print "Alleen buitentaluds gevonden"
        return "DOORGAAN"

    if binnenTaludLijnen and not buitenTaludLijnen:
        taludLijnen = binnenTaludLijnen
        arcpy.Merge_management(taludLijnen,"taludLijnenTotaal")
        print "Alleen binnentaluds gevonden"
        return "DOORGAAN"
    
    if not binnenTaludLijnen and not buitenTaludLijnen:
        print "Geen taludlijnen gevonden"
        return "STOP"

    

   


        
def getBitBut(profiel):

    # lokaliseer profieldelen op binnenkant-buitenkant
    bitCursor = arcpy.da.SearchCursor("binnenkruin","MEAS")
    for row in bitCursor:
        bikMEAS = row[0]
    del bitCursor
    butCursor = arcpy.da.SearchCursor("buitenkruin","MEAS")
    for row in butCursor:
        bukMEAS = row[0]
    del butCursor



    # knip profiel op waterlopen, alleen deel overhouden dat tussen waterlopen in ligt en dus snijdt met trajectlijn
    arcpy.Intersect_analysis([profiel,bgtWaterdelenTotaal], "isectWaterlopen", "ALL", "", "POINT")
    arcpy.SplitLineAtPoint_management(profiel, "isectWaterlopen", "splitProfielWaterloop", 1)


    arcpy.MakeFeatureLayer_management("splitProfielWaterloop", "temp_splitProfielWaterloop") 
    arcpy.SelectLayerByLocation_management("temp_splitProfielWaterloop", "INTERSECT", trajectLijn, "", "NEW_SELECTION", "NOT_INVERT")
    arcpy.CopyFeatures_management("temp_splitProfielWaterloop", "profielDeelBasis")

    # knip taluddelen af die niet in profielDeelBasis liggen
    arcpy.MakeFeatureLayer_management("taludLijnenTotaal", "temp_taludLijnenTotaal")
    arcpy.SelectLayerByLocation_management("temp_taludLijnenTotaal", "INTERSECT", "profielDeelBasis", "", "NEW_SELECTION", "NOT_INVERT")
    arcpy.CopyFeatures_management("temp_taludLijnenTotaal", "taludLijnenProfielBasis")


    # afsnijden eventueel waterdeel
    arcpy.Intersect_analysis(["taludLijnenTotaal",bgtWaterdelenTotaal], "isectTaluddelen", "ALL", "", "POINT")
    waterKruising = int(arcpy.GetCount_management("isectTaluddelen").getOutput(0))
    if waterKruising > 0:
        arcpy.SplitLineAtPoint_management("taludLijnenTotaal", "isectTaluddelen", "taludLijnenSplit", 1)
        arcpy.MakeFeatureLayer_management("taludLijnenSplit", "temp_taludLijnenSplit") 
        arcpy.SelectLayerByLocation_management("temp_taludLijnenSplit", "WITHIN", bgtWaterdelenTotaal, "", "NEW_SELECTION", "INVERT")
        arcpy.CopyFeatures_management("temp_taludLijnenSplit", "taludLijnenTotaal_")

        # select alleen waar profieldeelbasis 
        arcpy.MakeFeatureLayer_management("taludLijnenTotaal_", "temp_taludLijnenTotaal_")
        arcpy.SelectLayerByLocation_management("temp_taludLijnenTotaal_", "WITHIN", "profielDeelBasis", "", "NEW_SELECTION", "NOT_INVERT")
        arcpy.CopyFeatures_management("temp_taludLijnenTotaal_", "taludLijnenTotaal")

    else:
        pass



    # verwijder kleine segmenten
    minCursor = arcpy.da.UpdateCursor("taludLijnenTotaal","SHAPE@LENGTH")
    for minRow in minCursor:
        if round(minRow[0],2) < minLengteTaludBasis:
            print "Klein talud verwijderen van {} m ".format(round(minRow[0],2))
            minCursor.deleteRow()
        else:
            pass
    del minCursor
    

    ## binnenzijde en buitenzijde loskoppelen
    whereBinnen = '"' + "locatie" + '" = ' + "'" + "binnenzijde" + "'"
    arcpy.Select_analysis("taludLijnenTotaal", "taludLijnenBinnenkant", whereBinnen)
    taludDelenBinnenkant = int(arcpy.GetCount_management("taludLijnenBinnenkant").getOutput(0))
    print "Aantal taluddelen binnenkant: {}".format(taludDelenBinnenkant)

    whereBuiten = '"' + "locatie" + '" = ' + "'" + "buitenzijde" + "'"
    arcpy.Select_analysis("taludLijnenTotaal", "taludLijnenBuitenkant", whereBuiten)
    taludDelenBuitenkant = int(arcpy.GetCount_management("taludLijnenBuitenkant").getOutput(0))
    print "Aantal taluddelen buitenkant: {}".format(taludDelenBuitenkant)

    ## check voor snijpunten op insteek, bij twee of meer delen: verwijder onderste deel
    # binnenkant
    binnenkantCursor = arcpy.da.SearchCursor("taludLijnenBinnenkant",["SHAPE@","OID@"])
    taludDelenBinnenkantLijst = []
    for row in binnenkantCursor:
        oid = int(row[1])
        name = "binnenTalud_{}".format(oid)
        arcpy.CopyFeatures_management(row[0], name)
        taludDelenBinnenkantLijst.append(name)

    binnenkantCheck = False
    if taludDelenBinnenkant > 1 and binnenkantCheck is False:
        print "Check op waterloop intersectie binnenkant"

        
        # isect
        for item in taludDelenBinnenkantLijst:
            arcpy.Intersect_analysis([item,bgtWaterdelenTotaal], "isectTaluddeel", "ALL", "", "POINT")
            waterKruisingTD = int(arcpy.GetCount_management("isectTaluddeel").getOutput(0))


            if waterKruisingTD > 0: 
                taludDelenBinnenkantLijst.remove(item)
                taludDelenBinnenkant -= 1
                binnenkantCheck = True
            else:
                pass
    

    if taludDelenBinnenkant > 1 and binnenkantCheck is True:
        pass
    
    if taludDelenBinnenkantLijst:
        arcpy.Merge_management(taludDelenBinnenkantLijst,"taludLijnenBinnenkant")

    # buitenkant
    buitenkantCursor = arcpy.da.SearchCursor("taludLijnenBuitenkant",["SHAPE@","OID@"])
    taludDelenBuitenkantLijst = []
    for row in buitenkantCursor:
        oid = int(row[1])
        name = "buitenTalud_{}".format(oid)
        arcpy.CopyFeatures_management(row[0], name)
        taludDelenBuitenkantLijst.append(name)

    buitenkantCheck = False
    if taludDelenBuitenkant > 1 and buitenkantCheck is False:
        print "Check op waterloop intersectie buitenkant"

        
        # isect
        for item in taludDelenBuitenkantLijst:
            arcpy.Intersect_analysis([item,bgtWaterdelenTotaal], "isectTaluddeel", "ALL", "", "POINT")
            waterKruisingTD = int(arcpy.GetCount_management("isectTaluddeel").getOutput(0))


            if waterKruisingTD > 0: 
                taludDelenBuitenkantLijst.remove(item)
                taludDelenBuitenkant -= 1
                buitenkantCheck = True
            else:
                pass
    
    

    if taludDelenBuitenkant > 1 and buitenkantCheck is True:
        pass

    if taludDelenBuitenkantLijst:
        arcpy.Merge_management(taludDelenBuitenkantLijst,"taludLijnenBuitenkant")


    # bij een deel: hou deel --> bepalen insteek/bit/but!!! 





    ## binnenzijde 
    if taludDelenBinnenkant == 1:
        # binnenteen = laagste punt taluddeel

        # # afsnijden eventueel waterdeel
        # arcpy.Intersect_analysis(["taludLijnenBinnenkant",bgtWaterdelenTotaal], "isectTaludeelBinnen", "ALL", "", "POINT")
        # bitWaterKruising = int(arcpy.GetCount_management("taludLijnenBinnenkant").getOutput(0))
        # if bitWaterKruising > 0:
        #     arcpy.SplitLineAtPoint_management("taludLijnenBinnenkant", "isectTaludeelBinnen", "taludLijnenBinnenkantSplit", 1)
        #     arcpy.MakeFeatureLayer_management("taludLijnenBinnenkantSplit", "temp_taludLijnenBinnenkantSplit") 
        #     arcpy.SelectLayerByLocation_management("temp_taludLijnenBinnenkantSplit", "WITHIN", bgtWaterdelenTotaal, "", "NEW_SELECTION", "INVERT")
        #     arcpy.CopyFeatures_management("temp_taludLijnenBinnenkantSplit", "taludLijnenBinnenkant_")

        #     # select alleen waar profieldeelbasis 
        #     arcpy.MakeFeatureLayer_management("taludLijnenBinnenkant_", "temp_taludLijnenBinnenkant")
        #     arcpy.SelectLayerByLocation_management("temp_taludLijnenBinnenkant", "WITHIN", "profielDeelBasis", "", "NEW_SELECTION", "NOT_INVERT")
        #     arcpy.CopyFeatures_management("temp_taludLijnenBinnenkant", "taludLijnenBinnenkant")

        # else:
        #     pass


        arcpy.FeatureVerticesToPoints_management("taludLijnenBinnenkant", "binnenTaludPoints", "BOTH_ENDS")
        arcpy.LocateFeaturesAlongRoutes_lr("binnenTaludPoints", "testRoute", "rid", "0,1 Meters", "binnenTaludPointsTable", "RID POINT MEAS", "FIRST", "DISTANCE", "ZERO", "FIELDS", "M_DIRECTON")
        arcpy.JoinField_management("binnenTaludPoints","OBJECTID","binnenTaludPointsTable","OBJECTID","MEAS")
        
        # koppel z-waardes
        arcpy.CheckOutExtension("Spatial")
        ExtractValuesToPoints("binnenTaludPoints", hoogtedata, "binnenTaludPointsZ","INTERPOLATE", "VALUE_ONLY")
        arcpy.AlterField_management("binnenTaludPointsZ", 'RASTERVALU', 'z_ahn')

    

        # koppel aan contourwaardes en geef z-waarde contour-waarde indien niet aanwezig (raster nodata)
        arcpy.SpatialJoin_analysis("binnenTaludPointsZ", "testIsectFocalPoint_", "binnenTaludPointsZJoin", "JOIN_ONE_TO_ONE", "KEEP_ALL","","CLOSEST", "", "")
        taludCursor = arcpy.da.UpdateCursor("binnenTaludPointsZJoin",["z_ahn","Contour"])
        for row in taludCursor:
            if row[0] == None:
                row[0] = row[1]
                taludCursor.updateRow(row)

        zListBit = [z[0] for z in arcpy.da.SearchCursor ("binnenTaludPointsZ", ["z_ahn"])] 
        bitCursor = arcpy.da.UpdateCursor("binnenTaludPointsZ",["MEAS","z_ahn"])

        for row in bitCursor:
            if (round(row[0],2) == round(bikMEAS,2)):
                bitCursor.deleteRow()
            else:
                pass

        
        arcpy.CopyFeatures_management("binnenTaludPointsZ", "binnenteen")

        # voeg bitPunten toe aan profiel
        bitCursor = arcpy.da.InsertCursor(outPath, ['cPoint','SHAPE@XY'])
        xyBitList = [z[0] for z in arcpy.da.SearchCursor ("binnenteen", ["SHAPE@XY"])]
        for bitPunt in xyBitList:
            iRow = ['binnenteen', bitPunt]
            print iRow, bitPunt
            bitCursor.insertRow(iRow)

        del bitCursor


    if taludDelenBinnenkant > 1:
        print "binnenberm gevonden"
        # bepaal verloop taluddelen
        # # afsnijden eventueel waterdeel
        # arcpy.Intersect_analysis(["taludLijnenBinnenkant",bgtWaterdelenTotaal], "isectTaludeelBinnen", "ALL", "", "POINT")
        # bitWaterKruising = int(arcpy.GetCount_management("taludLijnenBinnenkant").getOutput(0))
        # if bitWaterKruising > 0:
        #     arcpy.SplitLineAtPoint_management("taludLijnenBinnenkant", "isectTaludeelBinnen", "taludLijnenBinnenkantSplit", 1)
        #     arcpy.MakeFeatureLayer_management("taludLijnenBinnenkantSplit", "temp_taludLijnenBinnenkantSplit") 
        #     arcpy.SelectLayerByLocation_management("temp_taludLijnenBinnenkantSplit", "WITHIN", bgtWaterdelenTotaal, "", "NEW_SELECTION", "INVERT")
        #     arcpy.CopyFeatures_management("temp_taludLijnenBinnenkantSplit", "taludLijnenBinnenkant_")

        #     # select alleen waar profieldeelbasis 
        #     arcpy.MakeFeatureLayer_management("taludLijnenBinnenkant_", "temp_taludLijnenBinnenkant")
        #     arcpy.SelectLayerByLocation_management("temp_taludLijnenBinnenkant", "WITHIN", "profielDeelBasis", "", "NEW_SELECTION", "NOT_INVERT")
        #     arcpy.CopyFeatures_management("temp_taludLijnenBinnenkant", "taludLijnenBinnenkant")



        # else:
        #     pass

        

        # voeg lengte toe om later te kunnen filteren
        arcpy.AddField_management("taludLijnenBinnenkant","lengteTalud","DOUBLE", 2, field_is_nullable="NULLABLE")
        taludCursor = arcpy.da.UpdateCursor("taludLijnenBinnenkant",["SHAPE@LENGTH","lengteTalud"])
        for row in taludCursor:
            row[1] = row[0]
            taludCursor.updateRow(row)

        del taludCursor

        # check of ieder taluddeel z-waardes heeft of begin en eindpunten
        arcpy.FeatureVerticesToPoints_management("taludLijnenBinnenkant", "binnenTaludPoints", "BOTH_ENDS")
        arcpy.LocateFeaturesAlongRoutes_lr("binnenTaludPoints", "testRoute", "rid", "0,1 Meters", "binnenTaludPointsTable", "RID POINT MEAS", "FIRST", "DISTANCE", "ZERO", "FIELDS", "M_DIRECTON")
        arcpy.JoinField_management("binnenTaludPoints","OBJECTID","binnenTaludPointsTable","OBJECTID","MEAS")

        # koppel z-waardes
        arcpy.CheckOutExtension("Spatial")
        ExtractValuesToPoints("binnenTaludPoints", hoogtedata, "binnenTaludPointsZ","INTERPOLATE", "VALUE_ONLY")
        arcpy.AlterField_management("binnenTaludPointsZ", 'RASTERVALU', 'z_ahn')

        # koppel aan contourwaardes en geef z-waarde contour-waarde indien niet aanwezig (raster nodata)
        arcpy.SpatialJoin_analysis("binnenTaludPointsZ", "testIsectFocalPoint_", "binnenTaludPointsZJoin", "JOIN_ONE_TO_ONE", "KEEP_ALL","","CLOSEST", "", "")
        taludCursor = arcpy.da.UpdateCursor("binnenTaludPointsZJoin",["z_ahn","Contour"])
        for row in taludCursor:
            if row[0] == None:
                row[0] = row[1]
                taludCursor.updateRow(row)
        

        
        # split in losse delen
        taludDelenB = splitByAttributes("binnenTaludPointsZJoin","ORIG_FID")
        removeList = []

        for taludDeel in taludDelenB:
            zList = [z[0] for z in arcpy.da.SearchCursor (taludDeel, ["z_ahn"])] 
            measList = [z[0] for z in arcpy.da.SearchCursor (taludDeel, ["MEAS"])] 


            maxZ = round(max(zList),2)
            minZ = round(min(zList),2)
            maxMeas = round(max(measList),2)
            minMeas = round(min(measList),2)

            # veld toevoegen voor gemiddelde hoogte taluddeel
            arcpy.AddField_management(taludDeel,"gemZ","DOUBLE", 2, field_is_nullable="NULLABLE")

            

            taludDeelCursor = arcpy.da.UpdateCursor(taludDeel,["MEAS","z_ahn","lengteTalud","gemZ"])
            for row in taludDeelCursor:
                meas = round(row[0],2)
                z_ahn = round(row[1],2)
                lengteTalud = round(row[2],2)
                row[3] = average([minZ,maxZ])

                taludDeelCursor.updateRow(row)

               
                        

        print taludDelenB
        taludDelenFinal = taludDelenB


        if len(taludDelenFinal) == 2:


            # ophalen gemiddelde hoogtes van taluddelen
            hoogtes = []
            for taludDeel in taludDelenFinal:
                arcpy.AddField_management(taludDeel,"taludDeel","TEXT", field_length=200)
                gemZ = [z[0] for z in arcpy.da.SearchCursor (taludDeel, ["gemZ"])] 
                for item in gemZ:
                    hoogtes.append(round(item,2))
                    break
            
            

            # onderverdeling in bovendeel-onderdeel
            for talud in taludDelenFinal:
                taludCursor = arcpy.da.UpdateCursor(talud,["taludDeel","gemZ"])
                for row in taludCursor:
                    if round(row[1],2) == max(hoogtes):
                        row[0] = "bovendeel"
                    else:
                        if round(row[1],2) == min(hoogtes):
                            row[0] = "benedendeel"

                    taludCursor.updateRow(row)

                del taludCursor
            # karakteristieke punten toekennen
            for talud in taludDelenFinal:

                

                zList = [z[0] for z in arcpy.da.SearchCursor (talud, ["z_ahn"])]
                maxZ = round(max(zList),2)
                minZ = round(min(zList),2)


                taludCursor = arcpy.da.UpdateCursor(talud,["z_ahn","taludDeel"])
                for row in taludCursor:
                    onderdeel = row[1]
                    if onderdeel == "benedendeel":
                        if round(row[0],2) == minZ:
                            arcpy.CopyFeatures_management(talud,"binnenteen")
                            bitCursor = arcpy.da.UpdateCursor("binnenteen",["z_ahn"])
                            for rij in bitCursor:
                                if round(rij[0],2) == minZ:
                                    pass
                                else:
                                    bitCursor.deleteRow()
                            row[1] = "onderzijde_"+onderdeel
                            taludCursor.updateRow(row)
                        
                        else:
                            arcpy.CopyFeatures_management(talud,"bovenkantOndertaludBinnen")
                            boCursor = arcpy.da.UpdateCursor("bovenkantOndertaludBinnen",["z_ahn"])
                            for rij in boCursor:
                                if round(rij[0],2) == maxZ:
                                    pass
                                else:
                                    boCursor.deleteRow()

                            row[1] = "onderzijde_"+onderdeel
                            taludCursor.updateRow(row)
                    
                    if onderdeel == "bovendeel":
                            if round(row[0],2) == minZ:
                                arcpy.CopyFeatures_management(talud,"onderkantBoventaludBinnen")
                                obCursor = arcpy.da.UpdateCursor("onderkantBoventaludBinnen",["z_ahn"])
                                for rij in obCursor:
                                    if round(rij[0],2) == minZ:
                                        pass
                                    else:
                                        obCursor.deleteRow()
                                row[1] = "onderzijde_"+onderdeel
                                taludCursor.updateRow(row)

                            else:
                                row[1] = "bovenzijde_"+onderdeel
                                taludCursor.updateRow(row)      

                del zList, maxZ, minZ, taludCursor

            # voeg bitPunten toe aan profiel
            bitCursor = arcpy.da.InsertCursor(outPath, ['cPoint','SHAPE@XY'])
            xyBitList = [z[0] for z in arcpy.da.SearchCursor ("binnenteen", ["SHAPE@XY"])]
            for bitPunt in xyBitList:
                iRow = ['binnenteen', bitPunt]
                print iRow, bitPunt
                bitCursor.insertRow(iRow)

            del bitCursor

            # voeg BinnentaludPunten toe aan profiel
            bermCursor = arcpy.da.InsertCursor(outPath, ['cPoint','SHAPE@XY'])
            xyBovenList = [z[0] for z in arcpy.da.SearchCursor ("onderkantBoventaludBinnen", ["SHAPE@XY"])]
            xyOnderList= [z[0] for z in arcpy.da.SearchCursor ("bovenkantOndertaludBinnen", ["SHAPE@XY"])]
            for bovenkantBerm in xyBovenList:
                iRow = ['bovenkantBermBinnen', bovenkantBerm]
                bermCursor.insertRow(iRow)

            for onderkantBerm in xyOnderList:
                iRow = ['onderkantBermBinnen', onderkantBerm]
                bermCursor.insertRow(iRow)
            
            del bermCursor


        else:
            print "probleem met aantal taluddelen binnenzijde"
            



            





    if taludDelenBinnenkant < 1:
        print "Geen taluddelen aan de binnenzijde"
        pass
        



    ## buitenzijde

    if taludDelenBuitenkant == 1:
        # buitenteen = laagste punt taluddeel

        # # afsnijden eventueel waterdeel
        # arcpy.Intersect_analysis(["taludLijnenBuitenkant",bgtWaterdelenTotaal], "isectTaludeelBuiten", "ALL", "", "POINT")
        # butWaterKruising = int(arcpy.GetCount_management("taludLijnenBuitenkant").getOutput(0))
        # if butWaterKruising > 0:
        #     arcpy.SplitLineAtPoint_management("taludLijnenBuitenkant", "isectTaludeelBuiten", "taludLijnenBuitenkantSplit", 1)
        #     arcpy.MakeFeatureLayer_management("taludLijnenBuitenkantSplit", "temp_taludLijnenBuitenkantSplit") 
        #     arcpy.SelectLayerByLocation_management("temp_taludLijnenBuitenkantSplit", "WITHIN", bgtWaterdelenTotaal, "", "NEW_SELECTION", "INVERT")
           

        #     arcpy.CopyFeatures_management("temp_taludLijnenBuitenkantSplit", "taludLijnenBuitenkant_")

        #     # select alleen waar profieldeelbasis 
        #     arcpy.MakeFeatureLayer_management("taludLijnenBuitenkant_", "temp_taludLijnenBuitenkant")
        #     arcpy.SelectLayerByLocation_management("temp_taludLijnenBuitenkant", "WITHIN", "profielDeelBasis", "", "NEW_SELECTION", "NOT_INVERT")
        #     arcpy.CopyFeatures_management("temp_taludLijnenBuitenkant", "taludLijnenBuitenkant")

        # else:
        #     pass


        arcpy.FeatureVerticesToPoints_management("taludLijnenBuitenkant", "buitenTaludPoints", "BOTH_ENDS")
        arcpy.LocateFeaturesAlongRoutes_lr("buitenTaludPoints", "testRoute", "rid", "0,1 Meters", "buitenTaludPointsTable", "RID POINT MEAS", "FIRST", "DISTANCE", "ZERO", "FIELDS", "M_DIRECTON")
        arcpy.JoinField_management("buitenTaludPoints","OBJECTID","buitenTaludPointsTable","OBJECTID","MEAS")
        
        # Koppel z-waardes
        arcpy.CheckOutExtension("Spatial")
        ExtractValuesToPoints("buitenTaludPoints", hoogtedata, "buitenTaludPointsZ","INTERPOLATE", "VALUE_ONLY")
        # Pas het veld 'RASTERVALU' aan naar 'z_ahn'
        arcpy.AlterField_management("buitenTaludPointsZ", 'RASTERVALU', 'z_ahn')

        
        
        # koppel aan contourwaardes en geef z-waarde contour-waarde indien niet aanwezig (raster nodata)
        arcpy.SpatialJoin_analysis("buitenTaludPointsZ", "testIsectFocalPoint_", "buitenTaludPointsZJoin", "JOIN_ONE_TO_ONE", "KEEP_ALL","","CLOSEST", "", "")
        taludCursor = arcpy.da.UpdateCursor("buitenTaludPointsZJoin",["z_ahn","Contour"])
        for row in taludCursor:
            if row[0] == None:
                row[0] = row[1]
                taludCursor.updateRow(row)

        zListBut = [z[0] for z in arcpy.da.SearchCursor ("buitenTaludPointsZ", ["z_ahn"])] 
        butCursor = arcpy.da.UpdateCursor("buitenTaludPointsZ",["MEAS","z_ahn"])

        for row in butCursor:
            if (round(row[0],2) == round(bukMEAS,2)):
                butCursor.deleteRow()
            else:
                pass
       
       
    	
        
        # if len(zListBut) ==2:
        #     print "Voldoende hoogtewaardes voor oordeel but met hoogtevergelijk"
        #     for row in butCursor:
        #         if (round(row[0],2) == round(bukMEAS,2)) and (round(max(zListBut),2)==round(row[1],2)):
        #             butCursor.deleteRow()
                    
        #         else:
        #             pass
        # else:
        #     print "Onvoldoende hoogtewaardes voor oordeel but met hoogtevergelijk" 
        #     for row in butCursor:
        #         if (round(row[0],2) == round(bukMEAS,2)):
        #             butCursor.deleteRow()
                    
        #         else:
        #             pass


        
        arcpy.CopyFeatures_management("buitenTaludPointsZ", "buitenteen")
        # voeg butPunten toe aan profiel
        butCursor = arcpy.da.InsertCursor(outPath, ['cPoint','SHAPE@XY'])
        xyButList = [z[0] for z in arcpy.da.SearchCursor ("buitenteen", ["SHAPE@XY"])]
        for butPunt in xyButList:
            iRow = ['buitenteen', butPunt]
            print iRow, butPunt
            butCursor.insertRow(iRow)

        del butCursor


    if taludDelenBuitenkant > 1:
        print "buitenberm gevonden"
        # bepaal verloop taluddelen
        # # afsnijden eventueel waterdeel
        # arcpy.Intersect_analysis(["taludLijnenBuitenkant",bgtWaterdelenTotaal], "isectTaludeelBuiten", "ALL", "", "POINT")
        # butWaterKruising = int(arcpy.GetCount_management("taludLijnenBuitenkant").getOutput(0))
        # if butWaterKruising > 0:
        #     arcpy.SplitLineAtPoint_management("taludLijnenBuitenkant", "isectTaludeelBuiten", "taludLijnenBuitenkantSplit", 1)
        #     arcpy.MakeFeatureLayer_management("taludLijnenBuitenkantSplit", "temp_taludLijnenBuitenkantSplit") 
        #     arcpy.SelectLayerByLocation_management("temp_taludLijnenBuitenkantSplit", "WITHIN", bgtWaterdelenTotaal, "", "NEW_SELECTION", "INVERT")
          

        #     arcpy.CopyFeatures_management("temp_taludLijnenBuitenkantSplit", "taludLijnenBuitenkant_")

        #     # select alleen waar profieldeelbasis 
        #     arcpy.MakeFeatureLayer_management("taludLijnenBuitenkant_", "temp_taludLijnenBuitenkant")
        #     arcpy.SelectLayerByLocation_management("temp_taludLijnenBuitenkant", "WITHIN", "profielDeelBasis", "", "NEW_SELECTION", "NOT_INVERT")
        #     arcpy.CopyFeatures_management("temp_taludLijnenBuitenkant", "taludLijnenBuitenkant")



        # else:
        #     pass

        

        # voeg lengte toe om later te kunnen filteren
        arcpy.AddField_management("taludLijnenBuitenkant","lengteTalud","DOUBLE", 2, field_is_nullable="NULLABLE")
        taludCursor = arcpy.da.UpdateCursor("taludLijnenBuitenkant",["SHAPE@LENGTH","lengteTalud"])
        for row in taludCursor:
            row[1] = row[0]
            taludCursor.updateRow(row)

        del taludCursor

        # check of ieder taluddeel z-waardes heeft of begin en eindpunten
        arcpy.FeatureVerticesToPoints_management("taludLijnenBuitenkant", "buitenTaludPoints", "BOTH_ENDS")
        arcpy.LocateFeaturesAlongRoutes_lr("buitenTaludPoints", "testRoute", "rid", "0,1 Meters", "buitenTaludPointsTable", "RID POINT MEAS", "FIRST", "DISTANCE", "ZERO", "FIELDS", "M_DIRECTON")
        arcpy.JoinField_management("buitenTaludPoints","OBJECTID","buitenTaludPointsTable","OBJECTID","MEAS")

        # koppel z-waardes
        arcpy.CheckOutExtension("Spatial")
        ExtractValuesToPoints("buitenTaludPoints", hoogtedata, "buitenTaludPointsZ","INTERPOLATE", "VALUE_ONLY")
        arcpy.AlterField_management("buitenTaludPointsZ", 'RASTERVALU', 'z_ahn')

        # koppel aan contourwaardes en geef z-waarde contour-waarde indien niet aanwezig (raster nodata)
        arcpy.SpatialJoin_analysis("buitenTaludPointsZ", "testIsectFocalPoint_", "buitenTaludPointsZJoin", "JOIN_ONE_TO_ONE", "KEEP_ALL","","CLOSEST", "", "")
        taludCursor = arcpy.da.UpdateCursor("buitenTaludPointsZJoin",["z_ahn","Contour"])
        for row in taludCursor:
            if row[0] == None:
                row[0] = row[1]
                taludCursor.updateRow(row)
        

        # indien het geval, controleer of talud afloopt en niet stijgt t.o.v. de kruin
        # split in losse delen
        taludDelenB = splitByAttributes("buitenTaludPointsZJoin","ORIG_FID")


        for taludDeel in taludDelenB:
            zList = [z[0] for z in arcpy.da.SearchCursor (taludDeel, ["z_ahn"])] 
            measList = [z[0] for z in arcpy.da.SearchCursor (taludDeel, ["MEAS"])]

            maxZ = round(max(zList),2)
            minZ = round(min(zList),2)
            maxMeas = round(max(measList),2)
            minMeas = round(min(measList),2)

            # veld toevoegen voor gemiddelde hoogte taluddeel
            arcpy.AddField_management(taludDeel,"gemZ","DOUBLE", 2, field_is_nullable="NULLABLE")

            


            taludDeelCursor = arcpy.da.UpdateCursor(taludDeel,["MEAS","z_ahn","lengteTalud","gemZ"])
            for row in taludDeelCursor:
                meas = round(row[0],2)
                z_ahn = round(row[1],2)
                lengteTalud = round(row[2],2)
                row[3] = average([minZ,maxZ])


                taludDeelCursor.updateRow(row)

               
                   
                  


        taludDelenFinal = taludDelenB
        # check of twee taluddelen over zijn, anders stoppen
        if len(taludDelenFinal) == 2:
            # ophalen gemiddelde hoogtes van taluddelen
            hoogtes = []
            for taludDeel in taludDelenFinal:
                arcpy.AddField_management(taludDeel,"taludDeel","TEXT", field_length=200)
                gemZ = [z[0] for z in arcpy.da.SearchCursor (taludDeel, ["gemZ"])] 
                for item in gemZ:
                    hoogtes.append(round(item,2))
                    break
            
            

            # onderverdeling in bovendeel-onderdeel
            for talud in taludDelenFinal:
                taludCursor = arcpy.da.UpdateCursor(talud,["taludDeel","gemZ"])
                for row in taludCursor:
                    if round(row[1],2) == max(hoogtes):
                        row[0] = "bovendeel"
                    else:
                        if round(row[1],2) == min(hoogtes):
                            row[0] = "benedendeel"

                    taludCursor.updateRow(row)

                del taludCursor
            # karakteristieke punten toekennen
            for talud in taludDelenFinal:

                

                zList = [z[0] for z in arcpy.da.SearchCursor (talud, ["z_ahn"])]
                maxZ = round(max(zList),2)
                minZ = round(min(zList),2)


                taludCursor = arcpy.da.UpdateCursor(talud,["z_ahn","taludDeel"])
                for row in taludCursor:
                    onderdeel = row[1]
                    if onderdeel == "benedendeel":
                        if round(row[0],2) == minZ:
                            arcpy.CopyFeatures_management(talud,"buitenteen")
                            bitCursor = arcpy.da.UpdateCursor("buitenteen",["z_ahn"])
                            for rij in bitCursor:
                                if round(rij[0],2) == minZ:
                                    pass
                                else:
                                    bitCursor.deleteRow()
                            row[1] = "onderzijde_"+onderdeel
                            taludCursor.updateRow(row)
                        
                        else:
                            arcpy.CopyFeatures_management(talud,"bovenkantOndertaludBuiten")
                            boCursor = arcpy.da.UpdateCursor("bovenkantOndertaludBuiten",["z_ahn"])
                            for rij in boCursor:
                                if round(rij[0],2) == maxZ:
                                    pass
                                else:
                                    boCursor.deleteRow()

                            row[1] = "onderzijde_"+onderdeel
                            taludCursor.updateRow(row)
                    
                    if onderdeel == "bovendeel":
                            if round(row[0],2) == minZ:
                                arcpy.CopyFeatures_management(talud,"onderkantBoventaludBuiten")
                                obCursor = arcpy.da.UpdateCursor("onderkantBoventaludBuiten",["z_ahn"])
                                for rij in obCursor:
                                    if round(rij[0],2) == minZ:
                                        pass
                                    else:
                                        obCursor.deleteRow()
                                row[1] = "onderzijde_"+onderdeel
                                taludCursor.updateRow(row)

                            else:
                                row[1] = "bovenzijde_"+onderdeel
                                taludCursor.updateRow(row)      

                del zList, maxZ, minZ, taludCursor
            
            # voeg bitPunten toe aan profiel
            butCursor = arcpy.da.InsertCursor(outPath, ['cPoint','SHAPE@XY'])
            xyButList = [z[0] for z in arcpy.da.SearchCursor ("buitenteen", ["SHAPE@XY"])]
            for butPunt in xyButList:
                iRow = ['buitenteen', butPunt]
                print iRow, butPunt
                butCursor.insertRow(iRow)

            del butCursor

            # voeg BinnentaludPunten toe aan profiel
            bermCursor = arcpy.da.InsertCursor(outPath, ['cPoint','SHAPE@XY'])
            xyBovenList = [z[0] for z in arcpy.da.SearchCursor ("onderkantBoventaludBuiten", ["SHAPE@XY"])]
            xyOnderList= [z[0] for z in arcpy.da.SearchCursor ("bovenkantOndertaludBuiten", ["SHAPE@XY"])]
            for bovenkantBerm in xyBovenList:
                iRow = ['bovenkantBermBuiten', bovenkantBerm]
                bermCursor.insertRow(iRow)

            for onderkantBerm in xyOnderList:
                iRow = ['onderkantBermBuiten', onderkantBerm]
                bermCursor.insertRow(iRow)
            
            del bermCursor


        else:
            print "probleem met aantal taluddelen buitenzijde"
     

        

    if taludDelenBuitenkant < 1:
        print "Geen taluddelen aan de buitenkant"
    

    # verwijder splitdata
    features = arcpy.ListFeatureClasses()
    for dataset in features:
        name = str(dataset)
        if name.startswith("split"):
            arcpy.Delete_management(dataset)


def getWaterPoints(profiel,output):

    # droge sloten en greppels worden (nog) niet meegenomen


    # bepaal binnenzijde en buitenzijde profieldeel
    arcpy.Merge_management(["binnenkruin","buitenkruin"],"kruinPunten")
    arcpy.SplitLineAtPoint_management(profiel, "kruinPunten", "profielSplitWater", 1)

    arcpy.MakeFeatureLayer_management("profielSplitWater", "temp_profielSplitWater") 
   
    arcpy.SelectLayerByLocation_management("temp_profielSplitWater", "WITHIN", "kruinLijn", "", "NEW_SELECTION", "INVERT")
    arcpy.CopyFeatures_management("temp_profielSplitWater", "profielSplitWaterZK")

    arcpy.MakeFeatureLayer_management("profielSplitWaterZK", "temp_profielSplitWaterZK") 
    arcpy.SelectLayerByLocation_management("temp_profielSplitWaterZK", "INTERSECT", "binnenkruin","", "NEW_SELECTION", "NOT_INVERT")
    arcpy.CopyFeatures_management("temp_profielSplitWaterZK", "profielBinnenzijde")

    arcpy.MakeFeatureLayer_management("profielSplitWaterZK", "temp_profielSplitWaterZK") 
    arcpy.SelectLayerByLocation_management("temp_profielSplitWaterZK", "INTERSECT", "buitenkruin","", "NEW_SELECTION", "NOT_INVERT")
    arcpy.CopyFeatures_management("temp_profielSplitWaterZK", "profielBuitenzijde")


    # check voor snijpunten met waterlopen
    arcpy.Intersect_analysis(["profielBuitenzijde",bgtWaterdelenTotaal], "isectWaterBuiten", "ALL", "", "POINT")
    snijpuntenWaterBuiten = int(arcpy.GetCount_management("isectWaterBuiten").getOutput(0))

    arcpy.Intersect_analysis(["profielBinnenzijde",bgtWaterdelenTotaal], "isectWaterBinnen", "ALL", "", "POINT")
    snijpuntenWaterBinnen= int(arcpy.GetCount_management("isectWaterBinnen").getOutput(0))



    if snijpuntenWaterBuiten > 0:
    
        arcpy.MultipartToSinglepart_management("isectWaterBuiten","isectWaterBuiten_")
        # waterpunten lokaliseren
        arcpy.LocateFeaturesAlongRoutes_lr("isectWaterBuiten_", "testRoute", "rid", "0,1 Meters", "waterBuitenRouteTable", "RID POINT MEAS", "FIRST", "DISTANCE", "ZERO", "FIELDS", "M_DIRECTON")
        arcpy.JoinField_management("isectWaterBuiten_","OBJECTID","waterBuitenRouteTable","OBJECTID","MEAS")
        arcpy.AlterField_management("isectWaterBuiten_", 'MEAS', 'afstand')

        # z-waarde aan waterpunten koppelen (indien aanwezig)
        arcpy.CheckOutExtension("Spatial")
        ExtractValuesToPoints("isectWaterBuiten_", hoogtedata, "isectWaterBuitenZ_","INTERPOLATE", "VALUE_ONLY")
        arcpy.AlterField_management("isectWaterBuitenZ_", 'RASTERVALU', 'z_ahn')
        

        # koppel aan contourwaardes en geef z-waarde contour-waarde indien niet aanwezig (raster nodata)
        arcpy.SpatialJoin_analysis("isectWaterBuitenZ_", "testIsectFocalPoint_", "isectWaterBuitenZ", "JOIN_ONE_TO_ONE", "KEEP_ALL","","CLOSEST", "", "")

        waterpuntCursor = arcpy.da.UpdateCursor("isectWaterBuitenZ",["z_ahn","Contour"])
        for wRow in waterpuntCursor:
            if wRow[0] == None:
                wRow[0] = wRow[1]
                waterpuntCursor.updateRow(wRow)
        del waterpuntCursor


        # schoonmaken 
        fields = [f.name for f in arcpy.ListFields("isectWaterBuitenZ")]
        keepFields = ["OBJECTID","Shape","afstand","z_ahn","BGTPlusType"]
        for field in fields:
            if field in keepFields:
                pass
            else:
                arcpy.DeleteField_management("isectWaterBuitenZ",field)

        arcpy.AddField_management("isectWaterBuitenZ","locatie","TEXT", field_length=200)

        # verwijder overlappende punten, selectie op hoogte en meas!


        # meas van waterlijnpunten:
        arcpy.CopyFeatures_management("isectWaterBuitenZ", "oeverpuntenBuiten_")
        waterpuntCursor = arcpy.da.UpdateCursor("oeverpuntenBuiten_",["z_ahn","afstand","BGTPlusType","locatie"])
        for wRow in waterpuntCursor:
            
            if "oever" in wRow[2]:
                pass
            else: 
                waterpuntCursor.deleteRow()
        del waterpuntCursor




        arcpy.CopyFeatures_management("isectWaterBuitenZ", "waterlijnpuntenBuiten")
        waterpuntCursor = arcpy.da.UpdateCursor("waterlijnpuntenBuiten",["z_ahn","afstand","BGTPlusType","locatie"])
        for wRow in waterpuntCursor:
            
            
            if "water" in wRow[2]:
                pass
            else: 
                waterpuntCursor.deleteRow()
            
            
        del waterpuntCursor
        



        # overlap verwijderen 
        arcpy.MakeFeatureLayer_management("oeverpuntenBuiten_", "temp_oeverpuntenBuiten") 
        arcpy.SelectLayerByLocation_management("temp_oeverpuntenBuiten", "INTERSECT", "waterlijnpuntenBuiten", "", "NEW_SELECTION", "INVERT")
        arcpy.CopyFeatures_management("temp_oeverpuntenBuiten","oeverpuntenBuiten")


        waterpuntCursor = arcpy.da.UpdateCursor("oeverpuntenBuiten",["z_ahn","afstand","BGTPlusType","locatie"])
        for wRow in waterpuntCursor:
            wRow[3] = "oever"
            waterpuntCursor.updateRow(wRow)

        del waterpuntCursor

        waterpuntCursor = arcpy.da.UpdateCursor("waterlijnpuntenBuiten",["z_ahn","afstand","BGTPlusType","locatie"])
        for wRow in waterpuntCursor:
            wRow[3] = "waterlijn"
            waterpuntCursor.updateRow(wRow)
        del waterpuntCursor

        # samenvoegen punten
        arcpy.Merge_management(["waterlijnpuntenBuiten","oeverpuntenBuiten"],"waterpuntenTotaalBuiten")



    
        # check voor max vier punten op profieldeel, meer kan/hoeft niet, sort op afstand ASC (binnen naar buiten)
        waterpuntCursor = arcpy.da.UpdateCursor("waterpuntenTotaalBuiten",["z_ahn","afstand","BGTPlusType","locatie"],sql_clause=(None, 'ORDER BY afstand ASC'))
        wPointsBuiten = 0

        for wRow in waterpuntCursor:
            wPointsBuiten += 1
            if wPointsBuiten <= 4:
                pass
            else:
                waterpuntCursor.deleteRow()

        del waterpuntCursor

        # check waterlijnpunten

        aantalPunten = int(arcpy.GetCount_management("waterpuntenTotaalBuiten")[0])
        # indien 2: twee soorten 
        if aantalPunten == 2:
            print "2 waterpunten gevonden buitenzijde, uitgaan van brede waterloop"

            soortlist= [z[0] for z in arcpy.da.SearchCursor ("waterpuntenTotaalBuiten", ["locatie","afstand"],sql_clause=(None, 'ORDER BY afstand ASC'))]

            soort1 = soortlist[0]
            soort2 = soortlist[1]

            if soort1 == "oever" and soort2 == "waterlijn":
                print "Volgorde klopt, bereken talud en punten"

                # bereken bodempunt
                # bereken talud
                hoogtelist= [z[0] for z in arcpy.da.SearchCursor ("waterpuntenTotaalBuiten", ["z_ahn","afstand"],sql_clause=(None, 'ORDER BY afstand ASC'))]
                afstandlist = [z[1] for z in arcpy.da.SearchCursor ("waterpuntenTotaalBuiten", ["z_ahn","afstand"],sql_clause=(None, 'ORDER BY afstand ASC'))]
                
                
                # oeverpunt
                hoogteOever = hoogtelist[0]
                afstandOever = afstandlist[0]
                
                #bodempunt
                offsetBodem = (diepteBreed/standaardTalud)
                hoogteBodem = (round(hoogtelist[1],2))-diepteBreed
                afstandBodem = afstandlist[1]+offsetBodem
                


                # tabel aanmaken voor localisatie
                arcpy.CreateTable_management(workspaceProfielen, "invoegtabel", "", "")
                arcpy.AddField_management("invoegtabel","locatie","TEXT", field_length=200)
                arcpy.AddField_management("invoegtabel","afstand","DOUBLE",field_is_nullable="NULLABLE")
                arcpy.AddField_management("invoegtabel","z_ahn","DOUBLE",field_is_nullable="NULLABLE")
                arcpy.AddField_management("invoegtabel","RID","DOUBLE", field_is_nullable="NULLABLE")

                tabelCursor = arcpy.da.InsertCursor("invoegtabel",["locatie","afstand","z_ahn","RID"])
                bodempunt = ("slootbodem_dijkzijde_buiten",afstandBodem,hoogteBodem,1)
                oeverpunt = ("insteek_sloot_dijkzijde_buiten",afstandOever,hoogteOever,1)
                tabelCursor.insertRow(bodempunt)
                tabelCursor.insertRow(oeverpunt)
                del tabelCursor



                # route event layer
                invoegtabelEvent = arcpy.MakeRouteEventLayer_lr("testRoute", "RID", "invoegtabel", "RID POINT afstand", "invoegtabel_event", "", "NO_ERROR_FIELD", "NO_ANGLE_FIELD", "NORMAL", "ANGLE", "LEFT", "POINT")

                # definitieve layer
                arcpy.CopyFeatures_management(invoegtabelEvent,"waterpunten_buiten_{}".format(output))
                
        


            else:
                print "Probleem in volgorde waterpunten, berekening overslaan"
                return "STOP"

            

        if aantalPunten == 3:
            print "3 waterpunten gevonden buitenzijde, controle waterloopbreedte op waterlijn"
            # check voor een oeverpunt en twee waterlijnpunten, eerste punt moet oever zijn!

            soortlist= [z[0] for z in arcpy.da.SearchCursor ("waterpuntenTotaalBuiten", ["locatie","z_ahn","afstand"],sql_clause=(None, 'ORDER BY afstand ASC'))]
            hoogtelist = [z[1] for z in arcpy.da.SearchCursor ("waterpuntenTotaalBuiten", ["locatie","z_ahn","afstand"],sql_clause=(None, 'ORDER BY afstand ASC'))]
            afstandlist = [z[2] for z in arcpy.da.SearchCursor ("waterpuntenTotaalBuiten", ["locatie","z_ahn","afstand"],sql_clause=(None, 'ORDER BY afstand ASC'))]

            soort1 = soortlist[0]
            soort2 = soortlist[1]
            soort3 = soortlist[2]

            print soort1, soort2, soort3
            if soort1 == "oever" and soort2 == "waterlijn" and soort3 == "waterlijn":

                # doorgaan
                # bereken breedte
                afstandWaterlijnDijk = hoogtelist[1]
                afstandWaterlijnBuiten = hoogtelist[2]
                breedteWaterloop = abs(afstandWaterlijnDijk-afstandWaterlijnBuiten)

                if breedteWaterloop <= breedteSmal:
                    diepte = diepteSmal
                else:
                    diepte = diepteBreed


                # oeverpunt
                hoogteOever = hoogtelist[0]
                afstandOever = afstandlist[0]
                
                
                offsetBodem = (diepte/standaardTalud)
                
                #bodempunt 1 dijkzijde
                hoogteBodem1 = (round(hoogtelist[1],2))-diepte
                afstandBodem1 = afstandlist[1]+offsetBodem

                # bodempunt 2 buitenzijde
                hoogteBodem2 = (round(hoogtelist[2],2))-diepte
                afstandBodem2 = afstandlist[2]-offsetBodem
                


                # tabel aanmaken voor localisatie
                arcpy.CreateTable_management(workspaceProfielen, "invoegtabel", "", "")
                arcpy.AddField_management("invoegtabel","locatie","TEXT", field_length=200)
                arcpy.AddField_management("invoegtabel","afstand","DOUBLE",field_is_nullable="NULLABLE")
                arcpy.AddField_management("invoegtabel","z_ahn","DOUBLE",field_is_nullable="NULLABLE")
                arcpy.AddField_management("invoegtabel","RID","DOUBLE", field_is_nullable="NULLABLE")

                tabelCursor = arcpy.da.InsertCursor("invoegtabel",["locatie","afstand","z_ahn","RID"])

                bodempunt1 = ("slootbodem_dijkzijde_buiten",afstandBodem1,hoogteBodem1,1)
                bodempunt2 = ("slootbodem_dijkzijde_buiten",afstandBodem2,hoogteBodem2,1)
                oeverpunt = ("insteek_sloot_dijkzijde_buiten",afstandOever,hoogteOever,1)

                tabelCursor.insertRow(bodempunt1)
                tabelCursor.insertRow(bodempunt2)
                tabelCursor.insertRow(oeverpunt)
                del tabelCursor



                # route event layer
                invoegtabelEvent = arcpy.MakeRouteEventLayer_lr("testRoute", "RID", "invoegtabel", "RID POINT afstand", "invoegtabel_event", "", "NO_ERROR_FIELD", "NO_ANGLE_FIELD", "NORMAL", "ANGLE", "LEFT", "POINT")

                # definitieve layer
                arcpy.CopyFeatures_management(invoegtabelEvent,"waterpunten_buiten_{}".format(output))
               
            
            
            else:
                print "Probleem in volgorde waterpunten, berekening overslaan"
                return "STOP"
                



        if aantalPunten == 4:
            print "4 waterpunten gevonden buitenzijde, controle waterloopbreedte op waterlijn"
            # check voor twee oeverpunten en twee waterlijnpunten
            soortlist= [z[0] for z in arcpy.da.SearchCursor ("waterpuntenTotaalBuiten", ["locatie","z_ahn","afstand"],sql_clause=(None, 'ORDER BY afstand ASC'))]
            hoogtelist = [z[1] for z in arcpy.da.SearchCursor ("waterpuntenTotaalBuiten", ["locatie","z_ahn","afstand"],sql_clause=(None, 'ORDER BY afstand ASC'))]
            afstandlist = [z[2] for z in arcpy.da.SearchCursor ("waterpuntenTotaalBuiten", ["locatie","z_ahn","afstand"],sql_clause=(None, 'ORDER BY afstand ASC'))]
            
            soort1 = soortlist[0]
            soort2 = soortlist[1]
            soort3 = soortlist[2]
            soort4 = soortlist[3]

            if soort1 == "oever" and soort2 =="waterlijn" and soort3 =="waterlijn" and soort4 =="oever":
                # doorgaan
                # bereken breedte
                afstandWaterlijnDijk = hoogtelist[1]
                afstandWaterlijnBuiten = hoogtelist[2]
                breedteWaterloop = abs(afstandWaterlijnDijk-afstandWaterlijnBuiten)

                if breedteWaterloop <= breedteSmal:
                    diepte = diepteSmal
                else:
                    diepte = diepteBreed


                # oeverpunt dijkzijde
                hoogteOever1 = hoogtelist[0]
                afstandOever1 = afstandlist[0]

                # oeverpunt buitenzijde
                hoogteOever2 = hoogtelist[3]
                afstandOever2 = afstandlist[3]
                
                
                offsetBodem = (diepte/standaardTalud)
                
                #bodempunt 1 dijkzijde
                hoogteBodem1 = (round(hoogtelist[1],2))-diepte
                afstandBodem1 = afstandlist[1]+offsetBodem

                # bodempunt 2 buitenzijde
                hoogteBodem2 = (round(hoogtelist[1],2))-diepte
                afstandBodem2 = afstandlist[2]-offsetBodem
                


                # tabel aanmaken voor localisatie
                arcpy.CreateTable_management(workspaceProfielen, "invoegtabel", "", "")
                arcpy.AddField_management("invoegtabel","locatie","TEXT", field_length=200)
                arcpy.AddField_management("invoegtabel","afstand","DOUBLE",field_is_nullable="NULLABLE")
                arcpy.AddField_management("invoegtabel","z_ahn","DOUBLE",field_is_nullable="NULLABLE")
                arcpy.AddField_management("invoegtabel","RID","DOUBLE", field_is_nullable="NULLABLE")

                tabelCursor = arcpy.da.InsertCursor("invoegtabel",["locatie","afstand","z_ahn","RID"])

                bodempunt1 = ("slootbodem_dijkzijde_buiten",afstandBodem1,hoogteBodem1,1)
                bodempunt2 = ("slootbodem_dijkzijde_buiten",afstandBodem2,hoogteBodem2,1)
                oeverpunt1 = ("insteek_sloot_dijkzijde_buiten",afstandOever1,hoogteOever1,1)
                oeverpunt2 = ("insteek_sloot_dijkzijde_buiten",afstandOever2,hoogteOever2,1)

                tabelCursor.insertRow(bodempunt1)
                tabelCursor.insertRow(bodempunt2)
                tabelCursor.insertRow(oeverpunt1)
                tabelCursor.insertRow(oeverpunt2)
                del tabelCursor



                # route event layer
                invoegtabelEvent = arcpy.MakeRouteEventLayer_lr("testRoute", "RID", "invoegtabel", "RID POINT afstand", "invoegtabel_event", "", "NO_ERROR_FIELD", "NO_ANGLE_FIELD", "NORMAL", "ANGLE", "LEFT", "POINT")

                # definitieve layer
                arcpy.CopyFeatures_management(invoegtabelEvent,"waterpunten_buiten_{}".format(output))


            else:
                print "Probleem in volgorde waterpunten, berekening overslaan"
                return "STOP"

        






    if snijpuntenWaterBinnen > 0:
        arcpy.MultipartToSinglepart_management("isectWaterBinnen","isectWaterBinnen_")
        # waterpunten lokaliseren
        arcpy.LocateFeaturesAlongRoutes_lr("isectWaterBinnen_", "testRoute", "rid", "0,1 Meters", "waterBinnenRouteTable", "RID POINT MEAS", "FIRST", "DISTANCE", "ZERO", "FIELDS", "M_DIRECTON")
        arcpy.JoinField_management("isectWaterBinnen_","OBJECTID","waterBinnenRouteTable","OBJECTID","MEAS")
        arcpy.AlterField_management("isectWaterBinnen_", 'MEAS', 'afstand')

        # z-waarde aan waterpunten koppelen (indien aanwezig)
        arcpy.CheckOutExtension("Spatial")
        ExtractValuesToPoints("isectWaterBinnen_", hoogtedata, "isectWaterBinnenZ_","INTERPOLATE", "VALUE_ONLY")
        arcpy.AlterField_management("isectWaterBinnenZ_", 'RASTERVALU', 'z_ahn')
        

        # koppel aan contourwaardes en geef z-waarde contour-waarde indien niet aanwezig (raster nodata)
        arcpy.SpatialJoin_analysis("isectWaterBinnenZ_", "testIsectFocalPoint_", "isectWaterBinnenZ", "JOIN_ONE_TO_ONE", "KEEP_ALL","","CLOSEST", "", "")

        waterpuntCursor = arcpy.da.UpdateCursor("isectWaterBinnenZ",["z_ahn","Contour"])
        for wRow in waterpuntCursor:
            if wRow[0] == None:
                wRow[0] = wRow[1]
                waterpuntCursor.updateRow(wRow)
        del waterpuntCursor


        # schoonmaken 
        fields = [f.name for f in arcpy.ListFields("isectWaterBinnenZ")]
        keepFields = ["OBJECTID","Shape","afstand","z_ahn","BGTPlusType"]
        for field in fields:
            if field in keepFields:
                pass
            else:
                arcpy.DeleteField_management("isectWaterBinnenZ",field)

        arcpy.AddField_management("isectWaterBinnenZ","locatie","TEXT", field_length=200)

        # verwijder overlappende punten, selectie op hoogte en meas!


        # meas van waterlijnpunten:
        arcpy.CopyFeatures_management("isectWaterBinnenZ", "oeverpuntenBinnen_")
        waterpuntCursor = arcpy.da.UpdateCursor("oeverpuntenBinnen_",["z_ahn","afstand","BGTPlusType","locatie"])
        for wRow in waterpuntCursor:
            
            if "oever" in wRow[2]:
                pass
            else: 
                waterpuntCursor.deleteRow()
        del waterpuntCursor




        arcpy.CopyFeatures_management("isectWaterBinnenZ", "waterlijnpuntenBinnen")
        waterpuntCursor = arcpy.da.UpdateCursor("waterlijnpuntenBinnen",["z_ahn","afstand","BGTPlusType","locatie"])
        for wRow in waterpuntCursor:
            
            
            if "water" in wRow[2]:
                pass
            else: 
                waterpuntCursor.deleteRow()
            
            
        del waterpuntCursor
        



        # overlap verwijderen 
        arcpy.MakeFeatureLayer_management("oeverpuntenBinnen_", "temp_oeverpuntenBinnen") 
        arcpy.SelectLayerByLocation_management("temp_oeverpuntenBinnen", "INTERSECT", "waterlijnpuntenBinnen", "", "NEW_SELECTION", "INVERT")
        arcpy.CopyFeatures_management("temp_oeverpuntenBinnen","oeverpuntenBinnen")


        waterpuntCursor = arcpy.da.UpdateCursor("oeverpuntenBinnen",["z_ahn","afstand","BGTPlusType","locatie"])
        for wRow in waterpuntCursor:
            wRow[3] = "oever"
            waterpuntCursor.updateRow(wRow)

        del waterpuntCursor

        waterpuntCursor = arcpy.da.UpdateCursor("waterlijnpuntenBinnen",["z_ahn","afstand","BGTPlusType","locatie"])
        for wRow in waterpuntCursor:
            wRow[3] = "waterlijn"
            waterpuntCursor.updateRow(wRow)
        del waterpuntCursor

        # samenvoegen punten
        arcpy.Merge_management(["waterlijnpuntenBinnen","oeverpuntenBinnen"],"waterpuntenTotaalBinnen")



    
        # check voor max vier punten op profieldeel, meer kan/hoeft niet, sort op afstand ASC (binnen naar buiten)
        waterpuntCursor = arcpy.da.UpdateCursor("waterpuntenTotaalBinnen",["z_ahn","afstand","BGTPlusType","locatie"],sql_clause=(None, 'ORDER BY afstand DESC'))
        wPointsBinnen = 0

        for wRow in waterpuntCursor:
            wPointsBinnen += 1
            if wPointsBinnen <= 4:
                pass
            else:
                waterpuntCursor.deleteRow()

        del waterpuntCursor

   

        # check waterlijnpunten

        aantalPunten = int(arcpy.GetCount_management("waterpuntenTotaalBinnen")[0])
        # indien 2: twee soorten 
        if aantalPunten == 2:
            print "2 waterpunten gevonden binnenzijde, uitgaan van brede waterloop"

            soortlist= [z[0] for z in arcpy.da.SearchCursor ("waterpuntenTotaalBinnen", ["locatie","afstand"],sql_clause=(None, 'ORDER BY afstand DESC'))]

            soort1 = soortlist[0]
            soort2 = soortlist[1]

            if soort1 == "oever" and soort2 == "waterlijn":
                print "Volgorde klopt, bereken talud en punten"

                # bereken bodempunt
                # bereken talud
                hoogtelist= [z[0] for z in arcpy.da.SearchCursor ("waterpuntenTotaalBinnen", ["z_ahn","afstand"],sql_clause=(None, 'ORDER BY afstand DESC'))]
                afstandlist = [z[1] for z in arcpy.da.SearchCursor ("waterpuntenTotaalBinnen", ["z_ahn","afstand"],sql_clause=(None, 'ORDER BY afstand DESC'))]
                
                
                # oeverpunt
                hoogteOever = hoogtelist[0]
                afstandOever = afstandlist[0]
                
                #bodempunt
                offsetBodem = (diepteBreed/standaardTalud)
                hoogteBodem = (round(hoogtelist[1],2))-diepteBreed
                afstandBodem = afstandlist[1]-offsetBodem
                


                # tabel aanmaken voor localisatie
                arcpy.CreateTable_management(workspaceProfielen, "invoegtabel", "", "")
                arcpy.AddField_management("invoegtabel","locatie","TEXT", field_length=200)
                arcpy.AddField_management("invoegtabel","afstand","DOUBLE",field_is_nullable="NULLABLE")
                arcpy.AddField_management("invoegtabel","z_ahn","DOUBLE",field_is_nullable="NULLABLE")
                arcpy.AddField_management("invoegtabel","RID","DOUBLE", field_is_nullable="NULLABLE")

                tabelCursor = arcpy.da.InsertCursor("invoegtabel",["locatie","afstand","z_ahn","RID"])
                bodempunt = ("slootbodem_dijkzijde_binnen",afstandBodem,hoogteBodem,1)
                oeverpunt = ("insteek_sloot_dijkzijde_binnen",afstandOever,hoogteOever,1)
                tabelCursor.insertRow(bodempunt)
                tabelCursor.insertRow(oeverpunt)
                del tabelCursor



                # route event layer
                invoegtabelEvent = arcpy.MakeRouteEventLayer_lr("testRoute", "RID", "invoegtabel", "RID POINT afstand", "invoegtabel_event", "", "NO_ERROR_FIELD", "NO_ANGLE_FIELD", "NORMAL", "ANGLE", "LEFT", "POINT")

                # definitieve layer
                arcpy.CopyFeatures_management(invoegtabelEvent,"waterpunten_binnen_{}".format(output))
                
        


            else:
                print "Probleem in volgorde waterpunten, berekening overslaan"
                return "STOP"

            

        if aantalPunten == 3:
            print "3 waterpunten gevonden binnenzijde, controle waterloopbreedte op waterlijn"
            # check voor een oeverpunt en twee waterlijnpunten, eerste punt moet oever zijn!

            soortlist= [z[0] for z in arcpy.da.SearchCursor ("waterpuntenTotaalBinnen", ["locatie","z_ahn","afstand"],sql_clause=(None, 'ORDER BY afstand DESC'))]
            hoogtelist = [z[1] for z in arcpy.da.SearchCursor ("waterpuntenTotaalBinnen", ["locatie","z_ahn","afstand"],sql_clause=(None, 'ORDER BY afstand DESC'))]
            afstandlist = [z[2] for z in arcpy.da.SearchCursor ("waterpuntenTotaalBinnen", ["locatie","z_ahn","afstand"],sql_clause=(None, 'ORDER BY afstand DESC'))]

            soort1 = soortlist[0]
            soort2 = soortlist[1]
            soort3 = soortlist[2]

            print soort1, soort2, soort3
            if soort1 == "oever" and soort2 == "waterlijn" and soort3 == "waterlijn":

                # doorgaan
                # bereken breedte
                afstandWaterlijnDijk = hoogtelist[1]
                afstandWaterlijnBuiten = hoogtelist[2]
                breedteWaterloop = abs(afstandWaterlijnDijk-afstandWaterlijnBuiten)

                if breedteWaterloop <= breedteSmal:
                    diepte = diepteSmal
                else:
                    diepte = diepteBreed


                # oeverpunt
                hoogteOever = hoogtelist[0]
                afstandOever = afstandlist[0]
                
                
                offsetBodem = (diepte/standaardTalud)
                
                #bodempunt 1 dijkzijde
                hoogteBodem1 = (round(hoogtelist[1],2))-diepte
                afstandBodem1 = afstandlist[1]-offsetBodem

                # bodempunt 2 buitenzijde
                hoogteBodem2 = (round(hoogtelist[2],2))-diepte
                afstandBodem2 = afstandlist[2]+offsetBodem
                


                # tabel aanmaken voor localisatie
                arcpy.CreateTable_management(workspaceProfielen, "invoegtabel", "", "")
                arcpy.AddField_management("invoegtabel","locatie","TEXT", field_length=200)
                arcpy.AddField_management("invoegtabel","afstand","DOUBLE",field_is_nullable="NULLABLE")
                arcpy.AddField_management("invoegtabel","z_ahn","DOUBLE",field_is_nullable="NULLABLE")
                arcpy.AddField_management("invoegtabel","RID","DOUBLE", field_is_nullable="NULLABLE")

                tabelCursor = arcpy.da.InsertCursor("invoegtabel",["locatie","afstand","z_ahn","RID"])

                bodempunt1 = ("slootbodem_dijkzijde_binnen",afstandBodem1,hoogteBodem1,1)
                bodempunt2 = ("slootbodem_dijkzijde_binnen",afstandBodem2,hoogteBodem2,1)
                oeverpunt = ("insteek_sloot_dijkzijde_binnen",afstandOever,hoogteOever,1)

                tabelCursor.insertRow(bodempunt1)
                tabelCursor.insertRow(bodempunt2)
                tabelCursor.insertRow(oeverpunt)
                del tabelCursor



                # route event layer
                invoegtabelEvent = arcpy.MakeRouteEventLayer_lr("testRoute", "RID", "invoegtabel", "RID POINT afstand", "invoegtabel_event", "", "NO_ERROR_FIELD", "NO_ANGLE_FIELD", "NORMAL", "ANGLE", "LEFT", "POINT")

                # definitieve layer
                arcpy.CopyFeatures_management(invoegtabelEvent,"waterpunten_binnen_{}".format(output))
               
            
            
            else:
                print "Probleem in volgorde waterpunten, berekening overslaan"
                return "STOP"
                



        if aantalPunten == 4:
            print "4 waterpunten gevonden binnenzijde, controle waterloopbreedte op waterlijn"
            # check voor twee oeverpunten en twee waterlijnpunten
            soortlist= [z[0] for z in arcpy.da.SearchCursor ("waterpuntenTotaalBinnen", ["locatie","z_ahn","afstand"],sql_clause=(None, 'ORDER BY afstand DESC'))]
            hoogtelist = [z[1] for z in arcpy.da.SearchCursor ("waterpuntenTotaalBinnen", ["locatie","z_ahn","afstand"],sql_clause=(None, 'ORDER BY afstand DESC'))]
            afstandlist = [z[2] for z in arcpy.da.SearchCursor ("waterpuntenTotaalBinnen", ["locatie","z_ahn","afstand"],sql_clause=(None, 'ORDER BY afstand DESC'))]
            
            soort1 = soortlist[0]
            soort2 = soortlist[1]
            soort3 = soortlist[2]
            soort4 = soortlist[3]

            if soort1 == "oever" and soort2 =="waterlijn" and soort3 =="waterlijn" and soort4 =="oever":
                # doorgaan
                # bereken breedte
                afstandWaterlijnDijk = hoogtelist[1]
                afstandWaterlijnBuiten = hoogtelist[2]
                breedteWaterloop = abs(afstandWaterlijnDijk-afstandWaterlijnBuiten)

                if breedteWaterloop <= breedteSmal:
                    diepte = diepteSmal
                else:
                    diepte = diepteBreed


                # oeverpunt dijkzijde
                hoogteOever1 = hoogtelist[0]
                afstandOever1 = afstandlist[0]

                # oeverpunt buitenzijde
                hoogteOever2 = hoogtelist[3]
                afstandOever2 = afstandlist[3]
                
                
                offsetBodem = (diepte/standaardTalud)
                
                #bodempunt 1 dijkzijde
                hoogteBodem1 = (round(hoogtelist[1],2))-diepte
                afstandBodem1 = afstandlist[1]-offsetBodem

                # bodempunt 2 buitenzijde
                hoogteBodem2 = (round(hoogtelist[1],2))-diepte
                afstandBodem2 = afstandlist[2]+offsetBodem
                


                # tabel aanmaken voor localisatie
                arcpy.CreateTable_management(workspaceProfielen, "invoegtabel", "", "")
                arcpy.AddField_management("invoegtabel","locatie","TEXT", field_length=200)
                arcpy.AddField_management("invoegtabel","afstand","DOUBLE",field_is_nullable="NULLABLE")
                arcpy.AddField_management("invoegtabel","z_ahn","DOUBLE",field_is_nullable="NULLABLE")
                arcpy.AddField_management("invoegtabel","RID","DOUBLE", field_is_nullable="NULLABLE")

                tabelCursor = arcpy.da.InsertCursor("invoegtabel",["locatie","afstand","z_ahn","RID"])

                bodempunt1 = ("slootbodem_dijkzijde_binnen",afstandBodem1,hoogteBodem1,1)
                bodempunt2 = ("slootbodem_dijkzijde_binnen",afstandBodem2,hoogteBodem2,1)
                oeverpunt1 = ("insteek_sloot_dijkzijde_binnen",afstandOever1,hoogteOever1,1)
                oeverpunt2 = ("insteek_sloot_dijkzijde_binnen",afstandOever2,hoogteOever2,1)

                tabelCursor.insertRow(bodempunt1)
                tabelCursor.insertRow(bodempunt2)
                tabelCursor.insertRow(oeverpunt1)
                tabelCursor.insertRow(oeverpunt2)
                del tabelCursor



                # route event layer
                invoegtabelEvent = arcpy.MakeRouteEventLayer_lr("testRoute", "RID", "invoegtabel", "RID POINT afstand", "invoegtabel_event", "", "NO_ERROR_FIELD", "NO_ANGLE_FIELD", "NORMAL", "ANGLE", "LEFT", "POINT")

                # definitieve layer
                arcpy.CopyFeatures_management(invoegtabelEvent,"waterpunten_binnen_{}".format(output))


            else:
                print "Probleem in volgorde waterpunten, berekening overslaan"
                return "STOP"






        





        














        
        waterpuntCursor = arcpy.da.UpdateCursor("waterpuntenTotaal",["z_ahn","afstand","BGTPlusType","locatie"],sql_clause=(None, 'ORDER BY afstand ASC'))
        wPointsBuiten = 0

        for wRow in waterpuntCursor:
            wPointsBuiten += 1
            if wPointsBuiten <= 4:
                pass
            else:
                waterpuntCursor.deleteRow()

        del waterpuntCursor


                







    print "Profiel gesplit op water en landdelen"








    
    # controleer of binnenzijde/buitenzijde snijdt met waterloop
    # 


def writeOutput(profiel,cPoints):
    # profiel voorzien van z-waardes op afstand van .. m
    arcpy.GeneratePointsAlongLines_management("testRoute", "puntenRoute", "DISTANCE", Distance= pointDistance)
  

    # profielpunten lokaliseren
    arcpy.LocateFeaturesAlongRoutes_lr("puntenRoute", "testRoute", "rid", "0,1 Meters", "profileRouteTable", "RID POINT MEAS", "FIRST", "DISTANCE", "ZERO", "FIELDS", "M_DIRECTON")
    arcpy.JoinField_management("puntenRoute","OBJECTID","profileRouteTable","OBJECTID","MEAS")
    arcpy.AlterField_management("puntenRoute", 'MEAS', 'afstand')

    # z-waarde aan profielpunten koppelen (indien aanwezig)
    arcpy.CheckOutExtension("Spatial")
    ExtractValuesToPoints("puntenRoute", hoogtedata, "puntenRouteZ","INTERPOLATE", "VALUE_ONLY")
    arcpy.AlterField_management("puntenRouteZ", 'RASTERVALU', 'z_ahn')


    # cPoints voorzien van z-waarde (indien aanwezig)
    ExtractValuesToPoints(cPoints, hoogtedata, "tempCpoints","INTERPOLATE", "VALUE_ONLY")
    arcpy.AlterField_management("tempCpoints", 'RASTERVALU', 'z_ahn')

    #cPoints lokaliseren
    arcpy.LocateFeaturesAlongRoutes_lr("tempCpoints", "testRoute", "rid", "0,1 Meters", "cPointRouteTable", "RID POINT MEAS", "FIRST", "DISTANCE", "ZERO", "FIELDS", "M_DIRECTON")
    arcpy.JoinField_management("tempCpoints","OBJECTID","cPointRouteTable","OBJECTID","MEAS")
    arcpy.AlterField_management("tempCpoints", 'MEAS', 'afstand')
    


    # koppel aan contourwaardes en geef z-waarde contour-waarde indien niet aanwezig (raster nodata)
    arcpy.SpatialJoin_analysis("tempCpoints", "testIsectFocalPoint_", cPoints, "JOIN_ONE_TO_ONE", "KEEP_ALL","","CLOSEST", "", "")
   
    cPointCursor = arcpy.da.UpdateCursor(cPoints,["z_ahn","Contour"])
    for cRow in cPointCursor:
        if cRow[0] == None:
            cRow[0] = cRow[1]
            cPointCursor.updateRow(cRow)
    del cPointCursor


    # verwijder onnodige velden
    veldenCpoint= [f.name for f in arcpy.ListFields(cPoints)]
    veldenCpointEnd = ["OID@","OBJECTID","Shape","cPoint","profielNaam","z_ahn","afstand"]
    for veld in veldenCpoint:
        if veld in veldenCpointEnd:
            pass
        else: 
            arcpy.DeleteField_management(cPoints,veld)



    # plotten van profiel en cPoints
    profiel = "puntenRouteZ"
    knikpunten = 'testknikpunten542'

    arrayProfiel = arcpy.da.FeatureClassToNumPyArray("puntenRouteZ", ('z_ahn','afstand'))
    dfProfiel = pd.DataFrame(arrayProfiel)
    sortProfiel = dfProfiel.sort_values(by=['afstand'])

    arrayCpoint = arcpy.da.FeatureClassToNumPyArray(cPoints, ('z_ahn','afstand','cPoint'))
    dfCpoint= pd.DataFrame(arrayCpoint)
    sortCpoint = dfCpoint.sort_values(by=['afstand'])

    plt.style.use('seaborn-whitegrid') #seaborn-ticks
    fig = plt.figure(figsize=(60, 10))
    ax1 = fig.add_subplot(111, label ="1")

    # cPoints
    buitenteen = sortCpoint.loc[sortCpoint['cPoint'] == 'buitenteen']
    binnenteen = sortCpoint.loc[sortCpoint['cPoint'] == 'binnenteen']
    binnenkruin = sortCpoint.loc[sortCpoint['cPoint'] == 'binnenkruin']
    buitenkruin = sortCpoint.loc[sortCpoint['cPoint'] == 'buitenkruin']

    insteekbbBinnen = sortCpoint.loc[sortCpoint['cPoint'] == 'bovenkantBermBinnen']
    insteekbbBuiten = sortCpoint.loc[sortCpoint['cPoint'] == 'bovenkantBermBuiten']
    kruinbBinnen = sortCpoint.loc[sortCpoint['cPoint'] == 'onderkantBermBinnen']
    kruinbBuiten = sortCpoint.loc[sortCpoint['cPoint'] == 'onderkantBermBuiten']

    ax1.plot(sortProfiel['afstand'],sortProfiel['z_ahn'],label="AHN3-profiel")


    if not buitenteen.empty:
        ax1.plot(buitenteen['afstand'],buitenteen['z_ahn'],'bo',markersize=10,color='yellow',label="Buitenteen")
    if not binnenteen.empty:
        ax1.plot(binnenteen['afstand'],binnenteen['z_ahn'],'bo',markersize=10,color='orange',label="Binnenteen")
    if not binnenkruin.empty:
        ax1.plot(binnenkruin['afstand'],binnenkruin['z_ahn'],'bo',markersize=10,color='sienna',label="Binnenkruin")
    if not buitenkruin.empty:
        ax1.plot(buitenkruin['afstand'],buitenkruin['z_ahn'],'bo',markersize=10,color='sandybrown',label="Buitenkruin")
    if not insteekbbBinnen.empty:
        ax1.plot(insteekbbBinnen['afstand'],insteekbbBinnen['z_ahn'],'bo',markersize=10,color='navy',label="Insteek binnenberm")
    if not insteekbbBuiten.empty:
        ax1.plot(insteekbbBuiten['afstand'],insteekbbBuiten['z_ahn'],'bo',markersize=10,color='violet',label="Insteek buitenberm")
    if not kruinbBinnen.empty:
        ax1.plot(kruinbBinnen['afstand'],kruinbBinnen['z_ahn'],'bo',markersize=10,color='hotpink',label="Kruin binnenberm")
    if not kruinbBuiten.empty:
        ax1.plot(kruinbBuiten['afstand'],kruinbBuiten['z_ahn'],'bo',markersize=10,color='mediumblue',label="Kruin buitenberm")

    ax1.legend(frameon=False, loc='upper left',prop={'size': 30})



    # plt.show()
    plt.savefig("{}/{}.jpg".format(outputFigures,outPath))
    plt.close()
    


    




profielIterator = arcpy.da.SearchCursor(profielen, profielVelden)
for row in profielIterator:



    geom = row[0]
    arcpy.CopyFeatures_management(geom,"tempProfiel")
    arcpy.AddField_management("tempProfiel","RID","DOUBLE", field_is_nullable="NULLABLE")
    tempCursor = arcpy.da.UpdateCursor("tempProfiel","RID")
    for tempRow in tempCursor:
        tempRow[0] = 1
        tempCursor.updateRow(tempRow)
    del tempCursor

    profiel = "tempProfiel"
    profielNummer = int(row[1])
    outName = "profiel_{}".format(profielNummer)
    # outPath = workspaceProfielen+"/"+outName
    outPath = outName

    print outName

    
    
    if arcpy.Exists(outPath):
        arcpy.Delete_management(outPath)
    # create InsertCursor
    arcpy.CreateFeatureclass_management(workspaceProfielen, outName, "POINT",spatial_reference= spatialRef)
    arcpy.AddField_management(outPath,"cPoint","TEXT", field_length=200)
    arcpy.AddField_management(outPath,"profielNaam","TEXT", field_length=200)

    profielCursor = arcpy.da.UpdateCursor(outPath,"profielNaam")
    for pRow in profielCursor:
        row[0] = outName
        profielCursor.updateRow(pRow)
   
    test = profielControle("tempProfiel")
    if test == "DOORGAAN":
        taludDelen("tempProfiel")
        getKruin("tempProfiel")
        getWaterPoints("tempProfiel",outName)
        # geomCheck = voorbewerkingTest("tempProfiel")
        # if geomCheck == "DOORGAAN":

        #     getBitBut("tempProfiel")
            
        #     # voeg naam toe aan rijen in profiel
        #     profielCursor = arcpy.da.UpdateCursor(outPath,"profielNaam")
        #     for pRow in profielCursor:
        #         pRow[0] = outName
        #         profielCursor.updateRow(pRow)

        #     writeOutput("tempProfiel",outPath)








