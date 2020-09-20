import arcpy
import matplotlib.pyplot as plt 
import pandas as pd
import numpy as np
from itertools import groupby
sys.path.append('.')
from basisfuncties import average
from arcpy.sa import *

arcpy.env.workspace = r'D:\Projecten\HDSR\2020\gisData\testgdb.gdb'
arcpy.env.overwriteOutput = True
profiel = "testprofiel"
trajectLijn = r"D:\Projecten\HDSR\2020\gisData\basisData.gdb\RWK_areaal_2024"
taludValue = 0.09

inritDistance = 3 #meter
pandDistance = 2 #meter 

hoogtedata = r"D:\Projecten\HDSR\2020\gisData\basisData.gdb\BAG2mPlusWaterlopenAHN3"
# hoogtedata = r"D:\GIS\losse rasters\ahn3clip\ahn3clip_2m"

bgtPanden = r"D:\Projecten\HDSR\2020\gisData\basisData.gdb\bgt_pand"
bgtWaterdelen = r"D:\Projecten\HDSR\2020\gisData\basisData.gdb\bgt_waterdeel"
bgtWaterdelenOndersteunend = r"D:\Projecten\HDSR\2020\gisData\basisData.gdb\bgt_ondersteunendWaterdeel"
bgtWaterdelenTotaal = r"D:\Projecten\HDSR\2020\gisData\basisData.gdb\bgt_waterdeel_totaal"
bgtWegdelen = r"D:\Projecten\HDSR\2020\gisData\basisData.gdb\bgt_wegdeel"
bgtWegdelenInritten = r"D:\Projecten\HDSR\2020\gisData\basisData.gdb\bgt_wegdeel_inritten"

taludLijnLijst = []
taludPuntLijst = []

def profielControle():
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
                print ("Geen belemerringen gevonden voor verdere berekeningen")
                return ("DOORGAAN")



def taludDelen():
    

    # raster clippen op profiel
    arcpy.Buffer_analysis(profiel, "bufferProfiel", "15 Meters", "FULL", "FLAT", "NONE", "", "PLANAR")
    arcpy.Clip_management(hoogtedata,"", "testClip", "bufferProfiel", "-3,402823e+038", "ClippingGeometry", "MAINTAIN_EXTENT")

    # focal op clip
    arcpy.gp.FocalStatistics_sa("testClip", "testClipFocal", "Rectangle 3 3 CELL", "MEAN", "DATA")

    # contour op focal
    arcpy.Contour_3d("testClipFocal", "testClipFocalContour", "0,01", "0", "1")

    # intersect op profiel en focal
    arcpy.Intersect_analysis(["testprofiel","testClipFocalContour"], "testIsectFocal", "ALL", "", "POINT")
    arcpy.MultipartToSinglepart_management("testIsectFocal","testIsectFocalPoint")


    # maak route van profiel
    arcpy.CreateRoutes_lr(profiel, "RID", 'testRoute', "LENGTH", "", "", "UPPER_LEFT", "1", "0", "IGNORE", "INDEX")

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
                        print ("gemiddele MEAS is {}".format(averageMEAS))
                        


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
                   





def getKruin():
    # check of trajectlijn snijdt met taluddelen, indien zo afbreken
    arcpy.MakeFeatureLayer_management(trajectLijn, 'temp_trajectLijn') 
    arcpy.SelectLayerByLocation_management('temp_trajectLijn', "INTERSECT", "taludLijnenTotaal", "", "NEW_SELECTION", "NOT_INVERT")
    taludIsectsTraject = int(arcpy.GetCount_management("temp_trajectLijn").getOutput(0))




    if taludIsectsTraject > 0:
        print ("Trajectlijn snijdt met taluddelen, berekening voor profiel .. afbreken")
        return ("STOP")

    else: 


        #split profiel met bestaande knikpunten
        arcpy.SplitLineAtPoint_management(profiel, "taludPuntenTotaal", "splitProfielDelen", 1)

        # selecteer snijdend deel met trajectlijn
        arcpy.MakeFeatureLayer_management("splitProfielDelen", "temp_splitProfielDelen") 
        arcpy.SelectLayerByLocation_management("temp_splitProfielDelen", "INTERSECT", trajectLijn, "", "NEW_SELECTION", "NOT_INVERT")
        arcpy.CopyFeatures_management("temp_splitProfielDelen", "kruinLijn")

        # binnen- en buitenkruin bepalen (profielen liggen van binnen naar buiten)
        arcpy.FeatureVerticesToPoints_management("kruinLijn", "binnenkruin", "START")
        arcpy.FeatureVerticesToPoints_management("kruinLijn", "buitenkruin", "END")

        # lokaliseer binnenkruin
        arcpy.LocateFeaturesAlongRoutes_lr("binnenkruin", "testRoute", "rid", "0,1 Meters", "bitTable", "RID POINT MEAS", "FIRST", "DISTANCE", "ZERO", "FIELDS", "M_DIRECTON")
        arcpy.JoinField_management("binnenkruin","OBJECTID","bitTable","OBJECTID","MEAS")

        # lokaliseer buitenkruin
        arcpy.LocateFeaturesAlongRoutes_lr("buitenkruin", "testRoute", "rid", "0,1 Meters", "butTable", "RID POINT MEAS", "FIRST", "DISTANCE", "ZERO", "FIELDS", "M_DIRECTON")
        arcpy.JoinField_management("buitenkruin","OBJECTID","butTable","OBJECTID","MEAS")

        
        
def getBitBut():

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

    

    ## binnenzijde
    where = '"' + "locatie" + '" = ' + "'" + "binnenzijde" + "'"
    arcpy.Select_analysis("taludLijnenProfielBasis", "taludLijnenBinnenkant", where)
    taludDelenBinnenkant = int(arcpy.GetCount_management("taludLijnenBinnenkant").getOutput(0))

    if taludDelenBinnenkant == 1:
        # binnenteen = laagste punt taluddeel

        # afsnijden eventueel waterdeel
        arcpy.Intersect_analysis(["taludLijnenBinnenkant",bgtWaterdelenTotaal], "isectTaludeelBinnen", "ALL", "", "POINT")
        bitWaterKruising = int(arcpy.GetCount_management("taludLijnenBinnenkant").getOutput(0))
        if bitWaterKruising > 0:
            arcpy.SplitLineAtPoint_management("taludLijnenBinnenkant", "isectTaludeelBinnen", "taludLijnenBinnenkantSplit", 1)
            arcpy.MakeFeatureLayer_management("taludLijnenBinnenkantSplit", "temp_taludLijnenBinnenkantSplit") 
            arcpy.SelectLayerByLocation_management("temp_taludLijnenBinnenkantSplit", "WITHIN", bgtWaterdelenTotaal, "", "NEW_SELECTION", "INVERT")
            arcpy.CopyFeatures_management("temp_taludLijnenBinnenkantSplit", "taludLijnenBinnenkant")

        else:
            pass


        arcpy.FeatureVerticesToPoints_management("taludLijnenBinnenkant", "binnenTaludPoints", "BOTH_ENDS")
        arcpy.LocateFeaturesAlongRoutes_lr("binnenTaludPoints", "testRoute", "rid", "0,1 Meters", "binnenTaludPointsTable", "RID POINT MEAS", "FIRST", "DISTANCE", "ZERO", "FIELDS", "M_DIRECTON")
        arcpy.JoinField_management("binnenTaludPoints","OBJECTID","binnenTaludPointsTable","OBJECTID","MEAS")
        
        # Koppel z-waardes
        arcpy.CheckOutExtension("Spatial")
        ExtractValuesToPoints("binnenTaludPoints", hoogtedata, "binnenTaludPointsZ","INTERPOLATE", "VALUE_ONLY")
        # Pas het veld 'RASTERVALU' aan naar 'z_ahn'
        arcpy.AlterField_management("binnenTaludPointsZ", 'RASTERVALU', 'z_ahn')

        zListBit = [z[0] for z in arcpy.da.SearchCursor ("binnenTaludPointsZ", ["z_ahn"])] 
        # for item in zListBit:
        #     print item, type(item)

        # print max(zListBit)
       
        bitCursor = arcpy.da.UpdateCursor("binnenTaludPointsZ",["MEAS","z_ahn"])

        if len(zListBit) ==2:
            print "Voldoende hoogtewaardes voor oordeel bit met hoogtevergelijk"
            for row in bitCursor:
                if (round(row[0],2) == round(bikMEAS,2)) and (round(max(zListBit),2)==round(row[1],2)):
                    bitCursor.deleteRow()
                    
                else:
                    pass
        else:
            print "Onvoldoende hoogtewaardes voor oordeel bit met hoogtevergelijk" 
            for row in bitCursor:
                if (round(row[0],2) == round(bikMEAS,2)):
                    bitCursor.deleteRow()
                else:
                    pass
        
        
        arcpy.CopyFeatures_management("binnenTaludPointsZ", "binnenteen")


    if taludDelenBinnenkant > 1:
        # bepaal verloop taluddelen
        pass

    if taludDelenBinnenkant < 1:
        # berekening afbreken
        pass



    ## buitenzijde
    # bepaal of meerdere taluddelen aanwezig zijn
    
    where = '"' + "locatie" + '" = ' + "'" + "buitenzijde" + "'"
    arcpy.Select_analysis("taludLijnenProfielBasis", "taludLijnenBuitenkant", where)
    taludDelenBuitenkant = int(arcpy.GetCount_management("taludLijnenBuitenkant").getOutput(0))

    if taludDelenBuitenkant == 1:
        # buitenteen = laagste punt taluddeel

        # afsnijden eventueel waterdeel
        arcpy.Intersect_analysis(["taludLijnenBuitenkant",bgtWaterdelenTotaal], "isectTaludeelBuiten", "ALL", "", "POINT")
        butWaterKruising = int(arcpy.GetCount_management("taludLijnenBuitenkant").getOutput(0))
        if bitWaterKruising > 0:
            arcpy.SplitLineAtPoint_management("taludLijnenBuitenkant", "isectTaludeelBuiten", "taludLijnenBuitenkantSplit", 1)
            arcpy.MakeFeatureLayer_management("taludLijnenBuitenkantSplit", "temp_taludLijnenBuitenkantSplit") 
            arcpy.SelectLayerByLocation_management("temp_taludLijnenBuitenkantSplit", "WITHIN", bgtWaterdelenTotaal, "", "NEW_SELECTION", "INVERT")
            arcpy.CopyFeatures_management("temp_taludLijnenBuitenkantSplit", "taludLijnenBuitenkant")

        else:
            pass


        arcpy.FeatureVerticesToPoints_management("taludLijnenBuitenkant", "buitenTaludPoints", "BOTH_ENDS")
        arcpy.LocateFeaturesAlongRoutes_lr("buitenTaludPoints", "testRoute", "rid", "0,1 Meters", "buitenTaludPointsTable", "RID POINT MEAS", "FIRST", "DISTANCE", "ZERO", "FIELDS", "M_DIRECTON")
        arcpy.JoinField_management("buitenTaludPoints","OBJECTID","buitenTaludPointsTable","OBJECTID","MEAS")
        
        # Koppel z-waardes
        arcpy.CheckOutExtension("Spatial")
        ExtractValuesToPoints("buitenTaludPoints", hoogtedata, "buitenTaludPointsZ","INTERPOLATE", "VALUE_ONLY")
        # Pas het veld 'RASTERVALU' aan naar 'z_ahn'
        arcpy.AlterField_management("buitenTaludPointsZ", 'RASTERVALU', 'z_ahn')

        zListBut = [z[0] for z in arcpy.da.SearchCursor ("buitenTaludPointsZ", ["z_ahn"])] 
        # for item in zListBut:
        #     print item, type(item)

        # print max(zListBut)
       
        butCursor = arcpy.da.UpdateCursor("buitenTaludPointsZ",["MEAS","z_ahn"])
    	
        
        if len(zListBut) ==2:
            print "Voldoende hoogtewaardes voor oordeel but met hoogtevergelijk"
            for row in butCursor:
                if (round(row[0],2) == round(bukMEAS,2)) and (round(max(zListBut),2)==round(row[1],2)):
                    butCursor.deleteRow()
                    
                else:
                    pass
        else:
            print "Onvoldoende hoogtewaardes voor oordeel but met hoogtevergelijk" 
            for row in butCursor:
                if (round(row[0],2) == round(bukMEAS,2)):
                    butCursor.deleteRow()
                    
                else:
                    pass


        
        arcpy.CopyFeatures_management("buitenTaludPointsZ", "buitenteen")


    if taludDelenBuitenkant > 1:
        # bepaal verloop taluddelen
        pass

    if taludDelenBuitenkant < 1:
        # berekening afbreken
        pass

    


test = profielControle()
if test =="DOORGAAN":

    taludDelen()
    getKruin()
    getBitBut()
        








