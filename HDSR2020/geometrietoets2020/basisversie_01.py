import arcpy
import os
import math
from arcpy.sa import *
from itertools import groupby
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt 


sys.path.append('HDSR2020')
from basisRWK2020 import generate_profiles, copy_trajectory_lr, split_profielen

arcpy.env.overwriteOutput = True
arcpy.env.workspace = r"D:\Projecten\HDSR\2020\gisData\geomtoetsV2.gdb"
workspace = r"D:\Projecten\HDSR\2020\gisData\geomtoetsV2.gdb"

baseFigures = r"C:/Users/Vincent/Desktop/geomtoets_v2/gt_results/"


  


trajectenHDSR = "RWK_areaal_2024_geomtoets"
afstandKruinSegment = 0.5 # maximale afstand die tussen kruinsegmenten mag zijn om samen te voegen
minKruinBreedte = 1.5
maxNodata = 3
ondergrensReferentie = 4 # aantal m onder toetsniveau
profielInterval = 25
profiel_lengte_land = 40
profiel_lengte_rivier = 1000
code_hdsr = "Naam"
bodemdalingsveld = "bodemdaling_mmjr"
toetsniveaus = "th2024"
toetsniveaus_bodemdaling = "tn_bodemdaling"
jaren_bodemdaling = 5 # uitgaande van vliegjaar ahn3: 2015
waterlopenBGTBoezem = r"D:\Projecten\HDSR\2020\gisData\basisData.gdb\bgt_waterdeel_boezem"
rasterAHN3BAG2m = r"D:\Projecten\HDSR\2020\gisData\basisData.gdb\BAG2mPlusWaterlopenAHN3"
bodemdalingskaart = r'D:\GIS\losse rasters\bodemdalingskaart_app_data_geotiff_Bodemdalingskaart_10de_percentiel_mm_per_jaar_verticale_richting_v2018002.tif'



def bepaal_bodemdaling(trajecten,bodemdalingskaart,code,bodemdalingsveld,jaren_bodemdaling,toetsniveaus,toetsniveaus_bodemdaling):
    # check op veld bodemdaling en voeg voor de zekerheid toe als nieuwe double
    fields = [f.name for f in arcpy.ListFields(trajecten)]

    if bodemdalingsveld in fields:
        arcpy.DeleteField_management(trajecten,bodemdalingsveld)
    else:
        pass

    if toetsniveaus_bodemdaling in fields:
        arcpy.DeleteField_management(trajecten,toetsniveaus_bodemdaling)
    else:
        pass
    

    # maak middelpunten op de trajecten om bodemdaling te koppelen
    arcpy.FeatureVerticesToPoints_management(trajecten, "trajecten_midpoints", "MID")

    # koppel bodemdalingswaarde uit raster aan middelpunten
    arcpy.CheckOutExtension("Spatial")
    ExtractValuesToPoints("trajecten_midpoints", bodemdalingskaart, "trajecten_midpoints_bd","", "VALUE_ONLY")
    arcpy.AlterField_management("trajecten_midpoints_bd", 'RASTERVALU', bodemdalingsveld)

    # check of waarde ingevuld is, anders 0 als bodemdalingswaarde gebruiken
    tempCursor = arcpy.da.UpdateCursor("trajecten_midpoints_bd",[bodemdalingsveld])
    for tRow in tempCursor:
        try:
            int(tRow[0])

        except:
            tRow[0] = 0
        
        tempCursor.updateRow(tRow)

    del tempCursor


    # koppel middelpunten terug aan trajecten
    arcpy.JoinField_management(trajecten,code,"trajecten_midpoints_bd",code,bodemdalingsveld)

    # voeg veld toe met toetspeil+bodemdaling
    arcpy.AddField_management(trajecten, toetsniveaus_bodemdaling,"DOUBLE", 2, field_is_nullable="NULLABLE")

    # bereken nieuwe toetspeil met bodemdaling
    tempCursor = arcpy.da.UpdateCursor(trajecten,[toetsniveaus,bodemdalingsveld,toetsniveaus_bodemdaling])
    for tRow in tempCursor:
        try:
            bodemdaling_mm_jaar = round(tRow[1],2)
            bodemdaling_periode = (bodemdaling_mm_jaar/100)*jaren_bodemdaling
            toetsniveau = round(tRow[0],2)
            if bodemdaling_periode >= 0:
         
                toetsniveau_nieuw =  toetsniveau - abs(bodemdaling_periode)
            if bodemdaling_periode <= 0:
        
                toetsniveau_nieuw = toetsniveau + abs(bodemdaling_periode)
            

           
            tRow[2] = toetsniveau_nieuw
            

        except:
            tRow[2] = 0

        
        tempCursor.updateRow(tRow)

    del tempCursor

    print "Bodemdaling gekoppeld aan trajecten: {} met periode van {} jaar".format(trajecten,jaren_bodemdaling)
  



def maak_plotmap(baseFigures,trajectnaam):

    plotmap = baseFigures+trajectnaam
    if not os.path.exists(plotmap):
        os.makedirs(plotmap)

    return plotmap
    print "Plotmap gemaakt voor {}".format(trajectnaam)


def maak_basisprofielen(trajectlijn,code,toetsniveau,toetsniveau_bodemdaling,profielen,refprofielen, bgt_waterdeel_boezem,trajectnaam,bodemdalingsveld,bodemdaling_perjaar,profiel_interval,profiel_lengte_land,profiel_lengte_rivier):
    ## 1 referentieprofielen maken
    generate_profiles(profiel_interval=profiel_interval,profiel_lengte_land=140,profiel_lengte_rivier=1000,trajectlijn=trajectlijn,code=code,
    toetspeil=toetsniveau,profielen="tempRefProfielen")
    
    ## 2 normale profielen maken 
    generate_profiles(profiel_interval=25,profiel_lengte_land=profiel_lengte_land,profiel_lengte_rivier=profiel_lengte_rivier,trajectlijn=trajectlijn,code=code,
    toetspeil=toetsniveau,profielen=profielen)



    ## 3 profielen knippen buitenzijde: BGT-waterdeel
    copy_trajectory_lr(trajectlijn=trajectlijn,code=code)
    split_profielen(profielen=profielen,trajectlijn=trajectlijn,code=code)

    # 3a snijpunten van rivierzijde profieldelen en boezemwaterlopen
    arcpy.Intersect_analysis(["profieldeel_rivier",bgt_waterdeel_boezem], "tempSplitBoezem", "ALL", "", "POINT")
    arcpy.SplitLineAtPoint_management(profielen, "tempSplitBoezem", "tempProfielenSplit", "1 Meters")
    arcpy.MakeFeatureLayer_management("tempProfielenSplit", "tempProfiellayer") 
    
    # 3b selecteer deel uit splitsing dat snijdt met trajectlijn
    arcpy.SelectLayerByLocation_management("tempProfiellayer", "INTERSECT", trajectlijn, "1 Meters", "NEW_SELECTION", "NOT_INVERT")
    arcpy.CopyFeatures_management("tempProfiellayer", "tempProfielen")


    arcpy.AddField_management("tempProfielen","objectid_str","TEXT", field_length=50)
    arcpy.AddField_management("tempProfielen","profielnummer_str","TEXT", field_length=50)
    tempCursor = arcpy.da.UpdateCursor("tempProfielen",["OBJECTID","objectid_str","profielnummer","profielnummer_str"])

    for tRow in tempCursor:
        profielnummer = str(int(tRow[2]))
        tRow[3] = "profiel_"+profielnummer
        
        objectid = str(int(tRow[0]))
        tRow[1] = "objectid_"+objectid
        
        tempCursor.updateRow(tRow)

    del tempCursor

    arcpy.AddField_management("traject_punten","profielnummer_str","TEXT", field_length=50)
    tempCursor = arcpy.da.UpdateCursor("traject_punten",["profielnummer","profielnummer_str"])

    for tRow in tempCursor:
        profielnummer = str(int(tRow[0]))
        tRow[1] = "profiel_"+profielnummer
        tempCursor.updateRow(tRow)

    del tempCursor


    #3c selecteer profielen met meer dan 1 deel
    dfCheck = pd.DataFrame(columns=['aantal_profieldelen'])
    tempCursor = arcpy.da.UpdateCursor("tempProfielen",["objectid_str","profielnummer_str"])
    for profielnummer, group in groupby(tempCursor, lambda x: x[1]):

        aantalDelen = 0

        for gRow in group:
            aantalDelen += 1

        dfCheck.loc[profielnummer] = aantalDelen
    
    del tempCursor
    dfCheck = dfCheck.drop(dfCheck[dfCheck.aantal_profieldelen < 2].index)



        



    # 3d verwijder profielen zonder isect met boezem
    tempCursor = arcpy.da.UpdateCursor("tempProfielen",["objectid_str","profielnummer_str"])
    for tRow in tempCursor:
        
        objectid = tRow[0]
        profielnummer = tRow[1]

        if profielnummer in dfCheck.index:
          

            # # selecteer betreffend profiel en kopieer naar tijdelijke laag
            where = '"' + 'objectid_str' + '" = ' + "'" + objectid + "'"
            arcpy.Select_analysis("tempProfielen", "tempprofiel", where)
            
            
            # selecteer trajectpunt en kopieer naar tijdelijke laag
            where = '"' + 'profielnummer_str' + '" = ' + "'" + profielnummer + "'"
            arcpy.Select_analysis("traject_punten", "profielrefpunt", where)

            # isect, als 0 dan verwijderen
            arcpy.Intersect_analysis(["tempprofiel","profielrefpunt"], "splitprofiellos", "ALL", "", "POINT")

            isects = int(arcpy.GetCount_management("splitprofiellos")[0])
            if isects == 0:
                tempCursor.deleteRow()
        else:
            pass

    del tempCursor

    

    # 3e verwijder profielen die niet afgesneden zijn
    beginLengte = int(round(profiel_lengte_land+profiel_lengte_rivier,0))
    tempCursor = arcpy.da.UpdateCursor("tempProfielen",["SHAPE@LENGTH"])
    for tRow in tempCursor:
        if int(round(tRow[0],0))== beginLengte:
            tempCursor.deleteRow()
        else:
            pass
    
    del tempCursor

    # 4 routes maken normale profielen (dit is tevens de defintieve profielenlaag waaraan oordelen worden gekoppeld)
    profielCursor = arcpy.da.UpdateCursor("tempProfielen", ["van","tot","SHAPE@LENGTH"])
    for tRow in profielCursor:
        lengte = tRow[2]
        tRow[0] = 0
        tRow[1] = lengte
        profielCursor.updateRow(tRow)

    
    del profielCursor
    arcpy.CreateRoutes_lr("tempProfielen", "profielnummer", profielen,"TWO_FIELDS", "van", "tot", "UPPER_LEFT", "1", "0", "IGNORE", "INDEX")
    arcpy.AddField_management(profielen,"geometrieOordeel","TEXT", field_length=50)
    
    # veld voor trajectnaam en bodemdaling in mm/jaar toevoegen aan profielen
    arcpy.AddField_management(profielen,"dijktraject", "TEXT", field_length=200)
    arcpy.AddField_management(profielen, bodemdalingsveld,"DOUBLE", 2, field_is_nullable="NULLABLE")
    arcpy.AddField_management(profielen, toetsniveaus,"DOUBLE", 2, field_is_nullable="NULLABLE")
    arcpy.AddField_management(profielen, toetsniveaus_bodemdaling,"DOUBLE", 2, field_is_nullable="NULLABLE")
    
    tempCursor = arcpy.da.UpdateCursor(profielen,["dijktraject",bodemdalingsveld,toetsniveaus,toetsniveaus_bodemdaling])
    for tRow in tempCursor:
        tRow[0] = trajectnaam
        tRow[1] = round(bodemdaling_perjaar,2)
        tRow[2] = toetsniveau
        tRow[3] = toetsniveau_bodemdaling
        tempCursor.updateRow(tRow)
    del tempCursor




    # 5 routes maken refprofielen
    profielCursor = arcpy.da.UpdateCursor("tempRefProfielen", ["van","tot","SHAPE@LENGTH"])
    for tRow in profielCursor:
        lengte = tRow[2]
        tRow[0] = 0
        tRow[1] = lengte
        profielCursor.updateRow(tRow)

    
    del profielCursor
    arcpy.CreateRoutes_lr("tempRefProfielen", "profielnummer", "refprofielen","TWO_FIELDS", "van", "tot", "UPPER_LEFT", "1", "0", "IGNORE", "INDEX")

    print "Profielen gemaakt voor {}".format(trajectnaam)





def bepaal_kruinvlak_toetsniveau(trajectlijn,hoogtedata,toetsniveau,profielen,refprofielen,trajectnaam):
    ## 1 maak buffer van traject om raster te knippen
    arcpy.Buffer_analysis(trajectlijn, "tempBufferTrajectlijn", "15 Meters", "FULL", "ROUND", "NONE", "", "PLANAR")

    ## 2 knip buffer uit totaalraster
    arcpy.Clip_management(hoogtedata,"", "tempRaster", "tempBufferTrajectlijn", "-3,402823e+038", "ClippingGeometry", "MAINTAIN_EXTENT")
    

    ## 3 raster calculator, selecteer deel op en boven toetsniveau
    raster = arcpy.Raster("tempRaster")
    outraster = raster >= toetsniveau
    outraster.save("tempRasterCalc")


    ## 4 raster vertalen naar polygon en alleen deel boven toetsniveau overhouden (gridcode = 1)
    arcpy.RasterToPolygon_conversion("tempRasterCalc", "tempRasterPoly", "SIMPLIFY", "Value")
    arcpy.Select_analysis("tempRasterPoly", "temp_opBovenTn", "gridcode = 1")


    ## 5  knip profielen op vlak "opBovenTn"
    arcpy.Intersect_analysis([profielen,"temp_opBovenTn"], "tempSplitKruin", "ALL", "", "POINT")
    arcpy.SplitLineAtPoint_management(profielen, "tempSplitKruin", "splitTempProfielen", "1 Meters")
    arcpy.MakeFeatureLayer_management("splitTempProfielen", "tempProfiellayer") 

    arcpy.SelectLayerByLocation_management("tempProfiellayer", "WITHIN", "temp_opBovenTn", "", "NEW_SELECTION", "NOT_INVERT")
    arcpy.CopyFeatures_management("tempProfiellayer", "profielDelenOpBovenTn")

    ## 6 check of profieldelen "opBovenTn" aanwezig zijn
    aantalOpBovenTn = int(arcpy.GetCount_management("profielDelenOpBovenTn")[0])

    if aantalOpBovenTn > 0:
    

        ## 7 samenvoegen delen die 0,5 m van elkaar afliggen
        sr = arcpy.SpatialReference(28992)
        if arcpy.Exists("kruindelenTraject"):
            arcpy.Delete_management("kruindelenTraject")

        arcpy.CreateFeatureclass_management(workspace, "kruindelenTraject", "POLYLINE",spatial_reference= sr)
        arcpy.AddField_management("kruindelenTraject","profielnummer","DOUBLE", 2, field_is_nullable="NULLABLE")
        arcpy.AddField_management("kruindelenTraject","maxBreedte","DOUBLE", 2, field_is_nullable="NULLABLE")
        kruindelenCursor = arcpy.da.InsertCursor("kruindelenTraject", ["profielnummer","maxBreedte","SHAPE@"])


        kruinCursor = arcpy.da.UpdateCursor("profielDelenOpBovenTn",["profielnummer","SHAPE@"],sql_clause=(None, 'ORDER BY profielnummer ASC'))
        
        for profielnummer, group in groupby(kruinCursor, lambda x: x[0]):

            kruinDelenGroep = []
            for kRow in group:
                kruinDelenGroep.append(kRow[1])
            
            #  samenvoegen
            arcpy.Merge_management(kruinDelenGroep,"kruinGroep")

            # near tabel maken
            arcpy.Near_analysis("kruinGroep", "kruinGroep", "", "NO_LOCATION", "NO_ANGLE", "PLANAR")

            # nears met < 0,5 m verwijderen

            profielCursorKruin = arcpy.da.UpdateCursor("kruinGroep",["NEAR_DIST","SHAPE@LENGTH"])

            for pRow in profielCursorKruin:
                if (pRow[0] > afstandKruinSegment) and (pRow[1] < minKruinBreedte):
                    profielCursorKruin.deleteRow()
                else:
                    pass

            del profielCursorKruin

            # indien twee of meer delen aanwezig zijn die wel lang genoeg zijn maar te ver uit elkaar liggen: langste overhouden
            
            try:
                minLengte = round(min([z[0] for z in arcpy.da.SearchCursor ("kruinGroep", ["SHAPE@LENGTH"])]),2)
                maxLengte = round(max([z[0] for z in arcpy.da.SearchCursor ("kruinGroep", ["SHAPE@LENGTH"])]),2)

                profielCursorKruin = arcpy.da.UpdateCursor("kruinGroep",["NEAR_DIST","SHAPE@LENGTH"])

                for pRow in profielCursorKruin:
                    if (pRow[0] > afstandKruinSegment) and (round(pRow[1],2) == maxLengte):
                        pass
                    if (pRow[0] > afstandKruinSegment) and (round(pRow[1],2) < maxLengte):
                        profielCursorKruin.deleteRow()

                del profielCursorKruin
            
            except ValueError:
                pass


            
            
            # punten van lijnen maken
            arcpy.FeatureVerticesToPoints_management("kruinGroep", "kruinGroepPunten", "BOTH_ENDS")
            arcpy.AddField_management("kruinGroepPunten", "profielnummer", "DOUBLE", 2, field_is_nullable="NULLABLE")
            tempCursor = arcpy.da.UpdateCursor("kruinGroepPunten","profielnummer")
            for tRow in tempCursor:
                tRow[0] = profielnummer
                tempCursor.updateRow(tRow)

            del tempCursor
            # eindpunten overhouden door afstandberekening
            arcpy.LocateFeaturesAlongRoutes_lr("kruinGroepPunten", refprofielen, "profielnummer", "0,1 Meters", "kruinTable", "RID POINT MEAS", "FIRST", "DISTANCE", "ZERO", "FIELDS", "M_DIRECTON")
            arcpy.JoinField_management("kruinGroepPunten","OBJECTID","kruinTable","OBJECTID","MEAS")


            try:
                minMeas = round(min([z[0] for z in arcpy.da.SearchCursor ("kruinGroepPunten", ["MEAS"])]),2)
                maxMeas = round(max([z[0] for z in arcpy.da.SearchCursor ("kruinGroepPunten", ["MEAS"])]),2)

                eindMeas = [minMeas,maxMeas]

                tempCursor = arcpy.da.UpdateCursor("kruinGroepPunten",["profielnummer","MEAS"])
                for tRow in tempCursor:
                    if round(tRow[1],2) in eindMeas:
                        pass
                    else:
                        tempCursor.deleteRow()

                del tempCursor

                # lijn maken van afstandpunten
                arcpy.PointsToLine_management("kruinGroepPunten", "kruinGroepLijn", "", "", "NO_CLOSE")

                # lijn toevoegen aan kruindelen met insertcursor
                kruinDeel = [z[0] for z in arcpy.da.SearchCursor ("kruinGroepLijn", ["SHAPE@"])][0]
                maxBreedte = [z[0] for z in arcpy.da.SearchCursor ("kruinGroepLijn", ["SHAPE@LENGTH"])][0]

                kruindelenCursor.insertRow([profielnummer, maxBreedte, kruinDeel])
                
                

            except ValueError:
                pass

        
        del kruinCursor
        print "Kruinvlak bepaald voor {} ".format(trajectnaam)
        return "kruindelenTraject"
    else:
        print "Onvoldoende hoogte voor berekeningen {} ".format(trajectnaam)
        return "stop"

        
 



def maak_referentieprofielen(profielen,refprofielen,toetsniveau, minKruinBreedte,refprofielenpunten,kruindelentraject,ondergrensReferentie,trajectnaam):
    ## 1 maak kruinpunten 
    arcpy.FeatureVerticesToPoints_management(kruindelentraject, "kruindelenTrajectEindpunten", "BOTH_ENDS")

    ## 2  lokaliseer kruinpunten op profielroute
    arcpy.LocateFeaturesAlongRoutes_lr("kruindelenTrajectEindpunten", refprofielen, "profielnummer", "0,1 Meters", "kruindelenTable", "RID POINT MEAS", "FIRST", "DISTANCE", "ZERO", "FIELDS", "M_DIRECTON")
    arcpy.JoinField_management("kruindelenTrajectEindpunten","OBJECTID","kruindelenTable","OBJECTID","MEAS")

    # 3 onderscheid maken binnen/buitenkant
    arcpy.AddField_management("kruindelenTrajectEindpunten","locatie","TEXT", field_length=50)
    arcpy.AddField_management("kruindelenTrajectEindpunten","z_ref","DOUBLE", 2, field_is_nullable="NULLABLE")
    arcpy.AddField_management("kruindelenTrajectEindpunten","profielnummer_str","TEXT", field_length=50)

    
    kruinDict = {}

    kruinPuntenCursor = arcpy.da.SearchCursor("kruindelenTrajectEindpunten",["profielnummer","MEAS","locatie"],sql_clause=(None, 'ORDER BY profielnummer ASC'))

    for profielnr, group in groupby(kruinPuntenCursor, lambda x: x[0]):
        profielnr = int(profielnr)
        firstMEAS = round(group.next()[1],2)
        secondMEAS = round(group.next()[1],2)

        measList = [firstMEAS,secondMEAS]
        minMeas = min(measList)
        maxMeas = max(measList)

        kruinDict[profielnr] = minMeas, maxMeas
    
    del kruinPuntenCursor


    kruinPuntenCursor = arcpy.da.UpdateCursor("kruindelenTrajectEindpunten",["profielnummer","MEAS","locatie","z_ref","profielnummer_str"],sql_clause=(None, 'ORDER BY profielnummer ASC'))
    
    for kRow in kruinPuntenCursor:
        if int(kRow[0]) in kruinDict:
            if round(kRow[1],2) == kruinDict[int(kRow[0])][0]:
            
                kRow[2] = "kruin binnenzijde"
            if round(kRow[1],2) == kruinDict[int(kRow[0])][1]:
                kRow[2] = "kruin buitenzijde"

        kRow[3] = toetsniveau
        kRow[4] = "profiel_"+str(int(kRow[0]))
        kruinPuntenCursor.updateRow(kRow)

    del kruinPuntenCursor

  

    
    
    
    ## 4 invoegen van eindpunten voor referentieprofiel, vanuit landzijde
    # z_ref eindpunten = toetsniveau -15m, z_ref kruin= toetsniveau, kruinbreedte = minkruinbreedte.
    # offset eindpunt binnen = 28 (4*1:7), offset buiten = 1.5+(4*1:2)

    if arcpy.Exists("refProfielTabel"):
        arcpy.Delete_management("refProfielTabel")

    arcpy.CreateTable_management(workspace, "refProfielTabel", "", "")
   
   
    arcpy.AddField_management("refProfielTabel","profielnummer", "DOUBLE", 2, field_is_nullable="NULLABLE")
    arcpy.AddField_management("refProfielTabel","locatie","TEXT", field_length=50)
    arcpy.AddField_management("refProfielTabel","afstand","DOUBLE", 2, field_is_nullable="NULLABLE")

    refPuntenCursor = arcpy.da.InsertCursor("refProfielTabel", ["profielnummer","locatie","afstand"])
  

    for profielnr, waardes in kruinDict.iteritems():
        

        # vanuit binnenzijde
        measKruinBinnen = waardes[0]
        measKruinBuiten = measKruinBinnen+minKruinBreedte
        measRefPuntBuiten = measKruinBuiten+8
        measRefPuntBinnen = measKruinBinnen-28



        # # vanuit buitenzijde
        # measKruinBuiten = waardes[1]
        # measKruinBinnen = measKruinBuiten-minKruinBreedte
        # measRefPuntBuiten = measKruinBuiten+30
        # measRefPuntBinnen = measKruinBinnen-105

       
        refPuntenCursor.insertRow([profielnr,"eindpunt binnenzijde",measRefPuntBinnen])
        refPuntenCursor.insertRow([profielnr,"eindpunt buitenzijde",measRefPuntBuiten])
        refPuntenCursor.insertRow([profielnr,"kruinpunt binnenzijde",measKruinBinnen])
        refPuntenCursor.insertRow([profielnr,"kruinpunt buitenzijde",measKruinBuiten])



    del refPuntenCursor

    
    ## 5 losse route per profiel maken

    arcpy.MakeRouteEventLayer_lr(refprofielen, "profielnummer", "refProfielTabel", "profielnummer POINT afstand", "temproutelayer", "", "NO_ERROR_FIELD", "NO_ANGLE_FIELD", "NORMAL", "ANGLE", "LEFT", "POINT")
    arcpy.CopyFeatures_management("temproutelayer", refprofielenpunten)
    arcpy.Delete_management("temproutelayer")

    ## 6 koppelen hoogtewaardes
    arcpy.AddField_management("refProfielenPunten","z_ref", "DOUBLE", 2, field_is_nullable="NULLABLE")

    refPuntenCursor = arcpy.da.UpdateCursor("refProfielenPunten",["locatie","z_ref"])

    for rRow in refPuntenCursor:
        if "kruinpunt" in rRow[0]:
            rRow[1] = toetsniveau
        if "eindpunt" in rRow[0]:
            rRow[1] = toetsniveau-ondergrensReferentie
        
        refPuntenCursor.updateRow(rRow)

    del refPuntenCursor


    print "Referentieprofielen gemaakt voor {}".format(trajectnaam)

def fitten_refprofiel(profielen, refprofielen, refprofielenpunten,hoogtedata,kruinpunten,plotmap,trajectnaam,toetsniveau,ondergrensReferentie,maxNodata):

    ## 1 maken van bandbreedtepunten (totaal)

    # eindpunten van profielen
    arcpy.FeatureVerticesToPoints_management(profielen, "grensRivierzijde", "END")

    whereKruin = '"' + 'locatie' + '" = ' + "'" + "kruin binnenzijde" + "'"
    arcpy.Select_analysis("kruindelenTrajectEindpunten", "grensLandzijde", whereKruin)

    arcpy.Merge_management(["grensLandzijde","grensRivierzijde"],"grensPunten")

    # velden bewerken voor koppeling df
    fields = [f.name for f in arcpy.ListFields("grensPunten")]

    for field in fields:
        if "MEAS" in field:
            arcpy.DeleteField_management("grensPunten",field)
        if "afstand" in field:
            arcpy.DeleteField_management("grensPunten",field)
        if "profielnummer_str" in field:
            arcpy.DeleteField_management("grensPunten",field)

        

    arcpy.AddField_management("grensPunten","profielnummer_str","TEXT", field_length=50)

    grensCursor = arcpy.da.UpdateCursor("grensPunten",["profielnummer","profielnummer_str"])

    for gRow in grensCursor:
        gRow[1] = "profiel_"+str(int(gRow[0]))
        grensCursor.updateRow(gRow)

    del grensCursor


    ## 2 stringveld aanmaken voor profielen en refprofielen voor individuele selectie
    arcpy.AddField_management(profielen,"profielnummer_str","TEXT", field_length=50)
    arcpy.AddField_management(refprofielen,"profielnummer_str","TEXT", field_length=50)
    arcpy.AddField_management(refprofielenpunten,"profielnummer_str","TEXT", field_length=50)

    profielCursor = arcpy.da.UpdateCursor(profielen,["profielnummer","profielnummer_str"])

    for pRow in profielCursor:
        pRow[1] = "profiel_"+str(int(pRow[0]))

        profielCursor.updateRow(pRow)
    
    del profielCursor

    profielCursor = arcpy.da.UpdateCursor(refprofielen,["profielnummer","profielnummer_str"])

    for pRow in profielCursor:
        pRow[1] = "profiel_"+str(int(pRow[0]))

        profielCursor.updateRow(pRow)
    
    del profielCursor

    profielCursor = arcpy.da.UpdateCursor(refprofielenpunten,["profielnummer","profielnummer_str"])

    for pRow in profielCursor:
        pRow[1] = "profiel_"+str(int(pRow[0]))

        profielCursor.updateRow(pRow)
    
    del profielCursor


    ## 3 ref_afstand toevoegen voor koppeling df
    fields = [f.name for f in arcpy.ListFields(refprofielenpunten)]

    if "afstand_ref" in fields:
        pass
    else:
        arcpy.AddField_management(refprofielenpunten,"afstand_ref","DOUBLE", 2, field_is_nullable="NULLABLE")


    tempCursor = arcpy.da.UpdateCursor(refprofielenpunten, ["afstand","afstand_ref"])
    for tRow in tempCursor:
            tRow[0] = round(tRow[0] * 2) / 2
            tRow[1] = round(tRow[0] * 2) / 2
            tempCursor.updateRow(tRow)
    del tempCursor

    

    ## 4 maak kruinpunten voor terugkoppeling locatie kruin
    sr = arcpy.SpatialReference(28992)
    arcpy.CreateFeatureclass_management(workspace, kruinpunten, "POINT",spatial_reference= sr)
    arcpy.AddField_management(kruinpunten,"dijktraject", "TEXT", field_length=200)
    arcpy.AddField_management(kruinpunten,"profielnummer","DOUBLE", 2, field_is_nullable="NULLABLE")
    arcpy.AddField_management(kruinpunten,"afstand","DOUBLE", 2, field_is_nullable="NULLABLE")
    kruinpuntenCursor = arcpy.da.InsertCursor(kruinpunten, ["dijktraject","profielnummer","afstand","SHAPE@"])

    ## 5 per profiel verder werken

    with arcpy.da.SearchCursor(profielen,["SHAPE@","profielnummer_str"]) as profielCursor:
        for pRow in profielCursor:


         


            profielnummer = pRow[1]
            # if profielnummer == "profiel_20":
            tempprofiel = "tempprofiel"
            temprefpunten = "temprefpunten"
            temprefprofiel = "temprefprofiel"
            tempbandbreedte = "tempbandbreedte"

        
                
            # selecteer betreffend profiel en kopieer naar tijdelijke laag
            where = '"' + 'profielnummer_str' + '" = ' + "'" + profielnummer + "'"
            arcpy.Select_analysis(profielen, tempprofiel, where)


            # selecteer referentiepunten van betreffend profiel en kopieer naar tijdelijke laag
            arcpy.Select_analysis(refprofielenpunten, temprefpunten, where)
            # arcpy.JoinField_management(temprefpunten,"profielnummer","kruindelenTraject","profielnummer","maxBreedte")


            # selecteer betreffend referentieprofiel voor localisatie profielpunten
            arcpy.Select_analysis(refprofielen, temprefprofiel, where)


            # selecteer betreffende kruinpunten(bandbreedte) voor localisatie
            arcpy.Select_analysis("grensPunten", tempbandbreedte, where)

    

            # creer routes voor punten profiel, dit is het echte profiel en NIET het refprofiel...! 
            arcpy.AddField_management(tempprofiel,"van","DOUBLE", 2, field_is_nullable="NULLABLE")
            arcpy.AddField_management(tempprofiel,"tot","DOUBLE", 2, field_is_nullable="NULLABLE")
            
            tempCursor = arcpy.da.UpdateCursor(tempprofiel, ["van","tot","SHAPE@LENGTH"])
            for tRow in tempCursor:
                lengte = tRow[2]
                tRow[0] = 0
                tRow[1] = lengte
                tempCursor.updateRow(tRow)
            
            del tempCursor
            arcpy.CreateRoutes_lr(tempprofiel, "profielnummer_str", 'tempRoute',"TWO_FIELDS", "van", "tot", "UPPER_LEFT", "1", "0", "IGNORE", "INDEX")

            # creer routes voor refprofiel, hierop wordt uiteindelijk alles gelokaliseerd 
            arcpy.AddField_management(temprefprofiel,"van","DOUBLE", 2, field_is_nullable="NULLABLE")
            arcpy.AddField_management(temprefprofiel,"tot","DOUBLE", 2, field_is_nullable="NULLABLE")
            
            tempCursor = arcpy.da.UpdateCursor(temprefprofiel, ["van","tot","SHAPE@LENGTH"])
            for tRow in tempCursor:
                lengte = tRow[2]
                tRow[0] = 0
                tRow[1] = lengte
                tempCursor.updateRow(tRow)
            
            del tempCursor
            arcpy.CreateRoutes_lr(temprefprofiel, "profielnummer_str", 'tempRefRoute',"TWO_FIELDS", "van", "tot", "UPPER_LEFT", "1", "0", "IGNORE", "INDEX")



            # profiel voorzien van z-waardes op afstand van 0.5 m
            arcpy.GeneratePointsAlongLines_management("tempRoute", "puntenRoute", "DISTANCE", Distance= 0.5)
        
            # profielpunten lokaliseren
            arcpy.LocateFeaturesAlongRoutes_lr("puntenRoute", "tempRefRoute", "profielnummer_str", "0,1 Meters", "profileRouteTable", "RID POINT MEAS", "FIRST", "DISTANCE", "ZERO", "FIELDS", "M_DIRECTON")
            arcpy.JoinField_management("puntenRoute","OBJECTID","profileRouteTable","OBJECTID","MEAS")
            arcpy.AlterField_management("puntenRoute", 'MEAS', 'afstand')


            # z-waarde aan profielpunten koppelen (indien aanwezig)
            arcpy.CheckOutExtension("Spatial")
            ExtractValuesToPoints("puntenRoute", hoogtedata, "puntenRouteZ","INTERPOLATE", "VALUE_ONLY")
            arcpy.AlterField_management("puntenRouteZ", 'RASTERVALU', 'z_ahn')


            # afstand afronden op .05 m om koppeling te garanderen in df
            tempCursor = arcpy.da.UpdateCursor("puntenRouteZ", ["afstand"])
            for tRow in tempCursor:
                tRow[0] = round(tRow[0] * 2) / 2
                tempCursor.updateRow(tRow)
            del tempCursor


            # bandbreedte lokaliseren
            arcpy.LocateFeaturesAlongRoutes_lr(tempbandbreedte, "tempRefRoute", "profielnummer_str", "0,1 Meters", "bandbreedteTable", "RID POINT MEAS", "FIRST", "DISTANCE", "ZERO", "FIELDS", "M_DIRECTON")
            arcpy.JoinField_management(tempbandbreedte,"OBJECTID","bandbreedteTable","OBJECTID","MEAS")
            arcpy.AlterField_management(tempbandbreedte, 'MEAS', 'afstand')

            tempCursor = arcpy.da.UpdateCursor(tempbandbreedte, ["afstand"])
            for tRow in tempCursor:
                tRow[0] = round(tRow[0] * 2) / 2
                tempCursor.updateRow(tRow)
            del tempCursor
            


            ## plotten 

            
            # gewone profiel
            arrayProfile = arcpy.da.FeatureClassToNumPyArray("puntenRouteZ", ('afstand','z_ahn'))
            profileDf = pd.DataFrame(arrayProfile)
            sortProfileDf = profileDf.sort_values(by=['afstand'],ascending=[True])

            # referentieprofiel
            arrayRefProfile = arcpy.da.FeatureClassToNumPyArray("temprefpunten", ('profielnummer','afstand','afstand_ref','z_ref'))
            refDf = pd.DataFrame(arrayRefProfile)
            sortrefDf = refDf.sort_values(by=['profielnummer','afstand_ref'],ascending=[True, True])

            # bandbreedte
            arrayBandbreedte = arcpy.da.FeatureClassToNumPyArray(tempbandbreedte, ('afstand','z_ref'))
            bandbreedteDf = pd.DataFrame(arrayBandbreedte)
            sortBandbreedteDf = bandbreedteDf.sort_values(by=['afstand'], ascending =[True])

            # plotbereik instellen
            minPlotX = sortProfileDf['afstand'].min()-10
            maxPlotX = sortProfileDf['afstand'].max()+10

        
            minPlotY = sortProfileDf['z_ahn'].min()-5
            # check of refprofiel zichtbaar is in plot
            if minPlotY >= toetsniveau:
                minPlotY = toetsniveau -2
            maxPlotY = sortProfileDf['z_ahn'].max()+1


            # minimale en maximale afstanden bepalen voor opbouw basisdataframe
            minList = [sortProfileDf['afstand'].min(),sortrefDf['afstand'].min()]
            maxList = [sortProfileDf['afstand'].max(),sortrefDf['afstand_ref'].max()]
            minAfstand = min(minList)
            maxAfstand = max(maxList)


            baseList = np.arange(minAfstand, maxAfstand, 0.5).tolist()
            baseSeries = pd.Series(baseList) 


            # opbouw dataframe
            frame = {'afstand': baseSeries} 
            baseDf = pd.DataFrame(frame) 

            # koppelen dataframes profielen en refprofielen
            baseMerge1 = baseDf.merge(sortProfileDf, on=['afstand'],how='outer')
            baseMerge2 = baseMerge1.merge(sortrefDf, on=['afstand'],how='outer')

            
            # verschil bepalen tussen gewone profiel en referentieprofiel
            firstAfstand = baseMerge2['afstand_ref'].first_valid_index()
            lastAfstand = baseMerge2['afstand_ref'].last_valid_index()

            # interpoleren van punten tussen de vier referentiepunten
            baseMerge2.loc[firstAfstand:lastAfstand, 'afstand_ref'] = baseMerge2.loc[firstAfstand:lastAfstand, 'afstand_ref'].interpolate()
            baseMerge2.loc[firstAfstand:lastAfstand, 'z_ref'] = baseMerge2.loc[firstAfstand:lastAfstand, 'z_ref'].interpolate()
            baseMerge2['difference'] = baseMerge2.z_ahn - baseMerge2.z_ref

            
            
            # plot opbouwen
            plt.style.use('seaborn-whitegrid') #seaborn-ticks
            fig = plt.figure(figsize=(80, 10))
            ax1 = fig.add_subplot(111, label ="1")
            
            ax1.plot(baseMerge2['afstand'],baseMerge2['z_ahn'],label="AHN3-profiel",color="dimgrey",linewidth=5)
            # ax1.plot(baseMerge2['afstand'],baseMerge2['z_ref'],label="Initieel referentieprofiel",color="orange",linewidth=3.5)


            # bandbreedte plotten
            try:
                leftBorder = sortBandbreedteDf.iloc[0]['afstand']
                rightBorder = sortBandbreedteDf.iloc[1]['afstand']

                ax1.axvline(leftBorder, color='coral', linestyle=':',linewidth=3,label="Iteratiegrens landzijde")
                ax1.axvline(rightBorder, color='seagreen', linestyle=':',linewidth=3, label="Iteratiegrens boezemzijde")

            except IndexError:
                pass
            

            # check of referentiepunten aanwezig zijn
            aantalRefpunten = int(arcpy.GetCount_management(temprefpunten)[0])
            if aantalRefpunten > 0:
                ingepastRefprofiel = True
            if aantalRefpunten == 0:
                ingepastRefprofiel = False

            
            
            # itereren tot referentieprofiel past, indien mogelijk en nodig
            iteraties = 1
            maxBreedte = abs(sortBandbreedteDf['afstand'].max() - sortBandbreedteDf['afstand'].min())
            resterend = round(maxBreedte* 2) / 2 - minKruinBreedte
            isectTest = (baseMerge2['difference'] < 0).values.any()

            
            # test of ahn-waardes boven de kruin aanwezig zijn
            refKruin = baseMerge2.loc[baseMerge2['z_ref'] == toetsniveau]
            refTest = refKruin['z_ahn'].isnull().values.any()

            

            # check uiterste rivierzijde ahnwaarde, deze mag niet overschreden worden door eindpunt buitenzijde refprofiel
            knipNan = baseMerge2[baseMerge2['z_ahn'].notna()]
            rivierGrensRaster = knipNan['afstand'].max()
            landGrensRaster = knipNan['afstand'].min()

            # eindpunt buitenzijde refprofiel
            # als geen grensprofiel ingepast kan worden, geen oordeel
            if ingepastRefprofiel == False:
            
                oordeelCursor = arcpy.da.UpdateCursor(profielen,["profielnummer_str","geometrieOordeel"])
                for oRow in oordeelCursor:
                    if oRow[0] == profielnummer:
                        oRow[1] = "Geen oordeel"
                    
                    oordeelCursor.updateRow(oRow)
                
                del oordeelCursor

                # legenda aanzetten
                ax1.legend(frameon=False, loc='upper right',prop={'size': 20})

                # plt.show()

                plt.savefig("{}/{}.png".format(plotmap,profielnummer))
                
        
                plt.close()

                print profielnummer



            # als wel grensprofiel ingepast kan worden: doorgaan
            
            
            if ingepastRefprofiel == True:
                ax1.plot(baseMerge2['afstand'],baseMerge2['z_ref'],label="Initieel referentieprofiel",color="orange",linewidth=3.5)
                refBasis = baseMerge2.loc[baseMerge2['z_ref'] == toetsniveau-ondergrensReferentie]
                buitenzijdeRefprofiel = round(float(refBasis['afstand'].max()),1)


                print "Riviergrensraster is {}m en buitenzijde grensprofiel is {}m".format(rivierGrensRaster,buitenzijdeRefprofiel)

                # default buitenTest = True!
                buitenTest = True
                
                if buitenzijdeRefprofiel > rivierGrensRaster:
                    buitenTest = True
                if buitenzijdeRefprofiel <= rivierGrensRaster:
                    buitenTest = False

            
    

            
                # check of nan-waardes boven refprofiel aanwezig zijn
                indexLinkerzijdeRp = baseMerge2['z_ref'].first_valid_index()
                indexRechterzijdeRp = baseMerge2['z_ref'].last_valid_index()
                linkerzijdeRp = baseMerge2.iloc[indexLinkerzijdeRp]['afstand']
                rechterzijdeRp = baseMerge2.iloc[indexRechterzijdeRp]['afstand']
                # print indexLinkerzijdeRp, linkerzijdeRp, indexRechterzijdeRp, rechterzijdeRp
                dfRef = baseMerge2.loc[indexLinkerzijdeRp:indexRechterzijdeRp]
                ahnTestRef = dfRef['z_ahn'].isnull().values.any()
                
                # test of 3 of meer aaneengesloten nodata punten in het ahnraster zitten boven refprofiel
                noData = 0
                ahnTest = False
                for index, dRow in dfRef.iterrows():
                    z_ahn = dRow['z_ahn']
                    if math.isnan(z_ahn) == True:
                        
                
    
                        noData +=1

                        if noData > maxNodata:
                            ahnTest = True
                            break

                    if math.isnan(z_ahn) == False:
                        noData = 0

            


                print "ahntest: {}".format(ahnTest)


                
                
                # alleen inpassen als refprofiel nog onder ahn past                                                                                                                               
                if buitenTest == False:
                    
                    while ((isectTest == True or refTest == True) and ingepastRefprofiel == True and resterend > 0):

                        print "Iteratie {}".format(iteraties)

                        # schuif het refprofiel naar rechts en test op isects

                        baseMerge2['afstand_ref'] = baseMerge2['afstand_ref'].shift(+1)
                        baseMerge2['z_ref'] = baseMerge2['z_ref'].shift(+1)
                        baseMerge2['difference'] = baseMerge2.z_ahn - baseMerge2.z_ref
                        
                        isectTest = (baseMerge2['difference'] < 0).values.any()


                        # optellen 
                        iteraties += 1
                        resterend -= 0.5
                        print resterend

                        # test of ahn-waardes boven de kruin aanwezig zijn
                        refKruin = baseMerge2.loc[baseMerge2['z_ref'] == toetsniveau]
                        refTest = refKruin['z_ahn'].isnull().values.any()

                        # check uiterste rivierzijde ahnwaarde, deze mag niet overschreden worden door eindpunt buitenzijde refprofiel
                        refBasis = baseMerge2.loc[baseMerge2['z_ref'] == toetsniveau-ondergrensReferentie]
                        buitenzijdeRefprofiel = round(float(refBasis['afstand'].max()),1)

                        print "buitenzijderefprofiel is {} en riviergrens raster is {}".format(buitenzijdeRefprofiel,rivierGrensRaster)
                        if buitenzijdeRefprofiel >= rivierGrensRaster:
                            buitenTest = True
                            print "overschrijding, stoppen!"
                            break
                        if buitenzijdeRefprofiel < rivierGrensRaster:
                            buitenTest = False


                        # check of nan-waardes boven refprofiel aanwezig zijn
                        indexLinkerzijdeRp = baseMerge2['z_ref'].first_valid_index()
                        indexRechterzijdeRp = baseMerge2['z_ref'].last_valid_index()
                        linkerzijdeRp = baseMerge2.iloc[indexLinkerzijdeRp]['afstand']
                        rechterzijdeRp = baseMerge2.iloc[indexRechterzijdeRp]['afstand']
                        # print indexLinkerzijdeRp, linkerzijdeRp, indexRechterzijdeRp, rechterzijdeRp
                        dfRef = baseMerge2.loc[indexLinkerzijdeRp:indexRechterzijdeRp]
                        ahnTestRef = dfRef['z_ahn'].isnull().values.any()

                        # test of 3 of meer aaneengesloten nodata punten in het ahnraster zitten boven refprofiel
                        
                        
                        # test rekenen vanaf landgrens ahnraster
                        try:
                            landGrensRaster = int(landGrensRaster)
                        except:
                            landGrensRaster = 0

                        
                        dfRef = dfRef[dfRef.afstand >= landGrensRaster]
                        # test rekenen vanaf landgrens ahnraster

                        noData = 0
                        # ahnTest = False
                        for index, dRow in dfRef.iterrows():
                            z_ahn = dRow['z_ahn']
                            if math.isnan(z_ahn) == True:
                                print dRow['afstand']
                                
                                noData +=1

                                if noData > maxNodata:
                                    ahnTest = True
                                    break

                            if math.isnan(z_ahn) == False:
                                noData = 0

                        print "ahntest v1: {}".format(ahnTest)



                    baseDF = baseMerge2.copy()
                    baseMerge3 = baseMerge2.copy()
                

                    # tweede poging tot fitten profiel zonder gaten in ahn
                    if isectTest == False and refTest == False and ahnTest == True and buitenTest ==False:

                        # baseMerge3 = baseMerge2

                        isectTest_v2 = True
                        refTest_v2 = True
                        ahnTest_v2 = True
                    

                        
                        while ahnTest_v2==True and resterend > 0:

                        
                            # probeer passende fit te vinden: isectTest, refTesten ahnTest moeten false zijn
                            # schuif het refprofiel naar rechts en test op isects

                            

                            baseMerge3['afstand_ref'] = baseMerge3['afstand_ref'].shift(+1)
                            baseMerge3['z_ref'] = baseMerge3['z_ref'].shift(+1)
                            baseMerge3['difference'] = baseMerge3.z_ahn - baseMerge3.z_ref
                            
                            isectTest_v2 = (baseMerge3['difference'] < 0).values.any()


                            # optellen 
                            iteraties += 1
                            resterend -= 0.5
                            print resterend, " in tweede poging"

                            # test of ahn-waardes boven de kruin aanwezig zijn
                            refKruin_v2 = baseMerge3.loc[baseMerge3['z_ref'] == toetsniveau]
                            refTest_v2 = refKruin_v2['z_ahn'].isnull().values.any()

                            # check uiterste rivierzijde ahnwaarde, deze mag niet overschreden worden door eindpunt buitenzijde refprofiel
                            refBasis_v2 = baseMerge3.loc[baseMerge3['z_ref'] == toetsniveau-ondergrensReferentie]
                            buitenzijdeRefprofiel_v2 = round(float(refBasis_v2['afstand'].max()),1)
                            if buitenzijdeRefprofiel_v2 >= rivierGrensRaster:
                                buitenTest_v2 = True
                                print "overschrijding, stoppen!"
                                

                                break
                            if buitenzijdeRefprofiel_v2 < rivierGrensRaster:
                                buitenTest_v2 = False


                            # check of nan-waardes boven refprofiel aanwezig zijn
                            indexLinkerzijdeRp_v2 = baseMerge3['z_ref'].first_valid_index()
                            indexRechterzijdeRp_v2 = baseMerge3['z_ref'].last_valid_index()
                            linkerzijdeRp_v2 = baseMerge3.iloc[indexLinkerzijdeRp_v2]['afstand']
                            rechterzijdeRp_v2 = baseMerge3.iloc[indexRechterzijdeRp_v2]['afstand']
                            # print indexLinkerzijdeRp, linkerzijdeRp, indexRechterzijdeRp, rechterzijdeRp
                            dfRef_v2 = baseMerge3.loc[indexLinkerzijdeRp_v2:indexRechterzijdeRp_v2]
                            ahnTestRef_v2 = dfRef_v2['z_ahn'].isnull().values.any()

                            # test of 3 of meer aaneengesloten nodata punten in het ahnraster zitten boven refprofiel


                            # test rekenen vanaf landgrens ahnraster
                            try:
                                landGrensRaster = int(landGrensRaster)
                            except:
                                landGrensRaster = 0

                        
                            dfRef_v2 = dfRef_v2[dfRef_v2.afstand >= landGrensRaster]
                            # test rekenen vanaf landgrens ahnraster


                            noData = 0
                            # ahnTest = False
                            for index, dRow in dfRef_v2.iterrows():
                                z_ahn = dRow['z_ahn']
                                if math.isnan(z_ahn) == True:
                                    
                                    noData +=1

                                    if noData > maxNodata:
                                        ahnTest_v2 = True
                                        break

                                if math.isnan(z_ahn) == False:
                                    noData = 0

                            if noData <= maxNodata: 
                                ahnTest_v2 = False

                            print "ahntest v2: {}".format(ahnTest_v2)

                            if isectTest_v2 == False and refTest_v2 == False and ahnTest_v2 == False and buitenTest_v2 == False:
                                print "fit gevonden!"
                                isectTest = False
                                refTest = False
                                ahnTest = False
                                buitenTest = buitenTest_v2
                                
                                # del baseMerge2
                                baseMerge2 = baseMerge3.copy()
                                # resetDF = False
                                

                                break

                            # else:
                            #     resetDF = True
                            #     print "reset DF"


                        # if resetDF == True:
                        #     print "df resetten..."
                        #     baseMerge2 = baseDF
                            
                

                    # einde tweede poging


                        

                # als uiterste ahnwaarde aan rivierzijde direct wordt overschreden, niet doorgaan        
                if buitenTest == True:
                    pass

                
            
                

                # terugkoppelen of fit wel/niet gelukt is 
                oordeelCursor = arcpy.da.UpdateCursor(profielen,["profielnummer_str","geometrieOordeel"])
                for oRow in oordeelCursor:
                    if oRow[0] == profielnummer:

                        if isectTest == True or refTest == True or buitenTest == True:
                            oRow[1] = "Onvoldoende"
                        
                        if (isectTest == False and refTest == False and buitenTest == False and ingepastRefprofiel == True and ahnTest == False):
                            # if ahnTest == False:

                            oRow[1] = "Voldoende, aaneengesloten hoogtedata"

                        if (isectTest == False and refTest == False and buitenTest == False and ingepastRefprofiel == True and ahnTest == True):
                            # if ahnTest == True:
                            oRow[1] = "Voldoende, gaten in hoogtedata"

                        if isectTest == False and ingepastRefprofiel == False:
                            oRow[1] = "Onvoldoende"
                        
                        if refTest == False and ingepastRefprofiel == False:
                            oRow[1] = "Onvoldoende"
                    
                        oordeelCursor.updateRow(oRow)

                del oordeelCursor

                # kruinlocatie als punt weergeven indien gefit
                if (isectTest == False and refTest == False and buitenTest == False and ingepastRefprofiel == True and ahnTest == True):
                    # plot geel profiel, profiel past maar niet netjes
                    ax1.plot(baseMerge2['afstand'],baseMerge2['z_ref'],'--',label="Passend referentieprofiel, gaten in hoogtedata", color="yellow",linewidth=3.5)
                    
                    kruinHoogte = baseMerge2['z_ref'].max()
                    kruinDeel = baseMerge2.loc[baseMerge2['z_ref'] == kruinHoogte]
                    kruinLandzijde = kruinDeel['afstand'].min()
                    kruinRivierzijde = kruinDeel['afstand'].max()
                    kruinMidden = (kruinLandzijde + kruinRivierzijde) / 2



                    arcpy.CreateTable_management(workspace, "kruinpuntTable", "", "")
                    arcpy.AddField_management("kruinpuntTable","profielnummer_str", "TEXT", field_length=50)
                    arcpy.AddField_management("kruinpuntTable","afstand","DOUBLE", 2, field_is_nullable="NULLABLE")

                    kruinTabelCursor = arcpy.da.InsertCursor("kruinpuntTable", ["profielnummer_str","afstand"])
                
                    kruinTabelCursor.insertRow([profielnummer,kruinMidden])

                    del kruinTabelCursor
                    

                    arcpy.MakeRouteEventLayer_lr("tempRefRoute", "profielnummer_str", "kruinpuntTable", "profielnummer_str POINT afstand", "kruinpuntlayer", "", "NO_ERROR_FIELD", "NO_ANGLE_FIELD", "NORMAL", "ANGLE", "LEFT", "POINT")
                    arcpy.CopyFeatures_management("kruinpuntlayer", "tempkruinpunt")
                    arcpy.Delete_management("kruinpuntlayer")

                    # invoegen punt in totaalset
                    geom = [z[0] for z in arcpy.da.SearchCursor ("tempkruinpunt", ["SHAPE@XY"])][0]

                    profielnummer_strip = profielnummer.strip("profielnummer_")
                    profielnummer_int = int(profielnummer_strip)
                    kruinpuntenCursor.insertRow([trajectnaam,profielnummer_int,kruinMidden, geom])

                    del geom

                if (isectTest == False and refTest == False and buitenTest == False and ingepastRefprofiel == True and ahnTest == False):
                    # plot groen profiel, profiel past
                    ax1.plot(baseMerge2['afstand'],baseMerge2['z_ref'],'--',label="Passend referentieprofiel", color="green",linewidth=3.5)
                   

                    kruinHoogte = baseMerge2['z_ref'].max()
                    kruinDeel = baseMerge2.loc[baseMerge2['z_ref'] == kruinHoogte]
                    kruinLandzijde = kruinDeel['afstand'].min()
                    kruinRivierzijde = kruinDeel['afstand'].max()
                    kruinMidden = (kruinLandzijde + kruinRivierzijde) / 2



                    arcpy.CreateTable_management(workspace, "kruinpuntTable", "", "")
                    arcpy.AddField_management("kruinpuntTable","profielnummer_str", "TEXT", field_length=50)
                    arcpy.AddField_management("kruinpuntTable","afstand","DOUBLE", 2, field_is_nullable="NULLABLE")

                    kruinTabelCursor = arcpy.da.InsertCursor("kruinpuntTable", ["profielnummer_str","afstand"])
                
                    kruinTabelCursor.insertRow([profielnummer,kruinMidden])

                    del kruinTabelCursor
                    

                    arcpy.MakeRouteEventLayer_lr("tempRefRoute", "profielnummer_str", "kruinpuntTable", "profielnummer_str POINT afstand", "kruinpuntlayer", "", "NO_ERROR_FIELD", "NO_ANGLE_FIELD", "NORMAL", "ANGLE", "LEFT", "POINT")
                    arcpy.CopyFeatures_management("kruinpuntlayer", "tempkruinpunt")
                    arcpy.Delete_management("kruinpuntlayer")

                    # invoegen punt in totaalset
                    geom = [z[0] for z in arcpy.da.SearchCursor ("tempkruinpunt", ["SHAPE@XY"])][0]

                    profielnummer_strip = profielnummer.strip("profielnummer_")
                    profielnummer_int = int(profielnummer_strip)
                    kruinpuntenCursor.insertRow([trajectnaam,profielnummer_int,kruinMidden, geom])

                    del geom
                
                    # einde kruinlocatie
            
                
                if ((isectTest == True or refTest == True or buitenTest == True) and ingepastRefprofiel == True):
                    # plot rood profiel, profiel past niet
                    ax1.plot(baseMerge2['afstand'],baseMerge2['z_ref'],'--',label="Niet-passend referentieprofiel", color="red",linewidth=3.5)

                if (isectTest == False or refTest == False) and ingepastRefprofiel == False:
                    pass

                

                # verdere plotinstellingen
                try:
                    minPlotX, maxPlotX, minPlotY, maxPlotY
                    plt.xlim(minPlotX, maxPlotX)
                    plt.ylim(minPlotY, maxPlotY)

                except ValueError:
                    pass
                
                # legenda aanzetten
                ax1.legend(frameon=False, loc='upper right',prop={'size': 20})

                # plt.show()

                plt.savefig("{}/{}.png".format(plotmap,profielnummer))
                
        
                plt.close()

                print profielnummer
                
                
                
        del kruinpuntenCursor
            

        print "Indien mogelijk referentieprofielen gefit voor {}".format(trajectnaam)


# stap 1: bodemdaling voor totaaltrajecten bepalen
bepaal_bodemdaling(trajecten=trajectenHDSR,bodemdalingskaart=bodemdalingskaart,code=code_hdsr,bodemdalingsveld=bodemdalingsveld,jaren_bodemdaling=jaren_bodemdaling,toetsniveaus=toetsniveaus,toetsniveaus_bodemdaling=toetsniveaus_bodemdaling)

with arcpy.da.SearchCursor(trajectenHDSR,['SHAPE@',code_hdsr,toetsniveaus,bodemdalingsveld,toetsniveaus_bodemdaling]) as cursor:
    for row in cursor:
        
        # lokale variabelen per dijktraject
        code = code_hdsr
        toetsniveau = float(row[2])
        toetsniveau_bodemdaling = float(row[4])
        bodemdaling_perjaar = float(row[3]) # in mm
        id = row[1]
        
        profielen = "profielen_"+id
        refprofielen = "refprofielen"
        trajectlijn = "tempTrajectlijn"
        kruinpunten = "kruinpunten_"+id

        refprofielenpunten = "refProfielenPunten"

        # selecteer betreffend traject en kopieer naar tijdelijke laag
        where = '"' + code_hdsr + '" = ' + "'" + str(id) + "'"
        arcpy.Select_analysis(trajectenHDSR, trajectlijn, where)


      
        maak_basisprofielen(trajectlijn=trajectlijn,code=code,toetsniveau=toetsniveau,toetsniveau_bodemdaling=toetsniveau_bodemdaling, profielen=profielen,bodemdalingsveld=bodemdalingsveld, bodemdaling_perjaar=bodemdaling_perjaar, refprofielen=refprofielen, bgt_waterdeel_boezem=waterlopenBGTBoezem,trajectnaam=id,profiel_interval=profielInterval,profiel_lengte_land=profiel_lengte_land,profiel_lengte_rivier=profiel_lengte_rivier)

      
        
        hoogtetest = bepaal_kruinvlak_toetsniveau(trajectlijn=trajectlijn,hoogtedata=rasterAHN3BAG2m,toetsniveau=toetsniveau,profielen=profielen,refprofielen=refprofielen,trajectnaam=id)

        if hoogtetest == "stop":
            pass

        else: 

            maak_referentieprofielen(profielen=profielen,refprofielen=refprofielen, toetsniveau=toetsniveau_bodemdaling,minKruinBreedte=minKruinBreedte,refprofielenpunten= refprofielenpunten,kruindelentraject=hoogtetest,ondergrensReferentie=ondergrensReferentie,trajectnaam=id)

            plotmap = maak_plotmap(baseFigures=baseFigures,trajectnaam = id)

            fitten_refprofiel(profielen=profielen,refprofielen=refprofielen, refprofielenpunten=refprofielenpunten,hoogtedata=rasterAHN3BAG2m,kruinpunten=kruinpunten,plotmap=plotmap,trajectnaam = id,toetsniveau=toetsniveau_bodemdaling, ondergrensReferentie=ondergrensReferentie,maxNodata=maxNodata)