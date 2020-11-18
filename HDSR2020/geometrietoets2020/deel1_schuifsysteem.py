import arcpy
from arcpy.sa import *
from itertools import groupby
import pandas as pd
import matplotlib.pyplot as plt 

sys.path.append('HDSR2020')
from basisRWK2020 import generate_profiles, copy_trajectory_lr, split_profielen

arcpy.env.overwriteOutput = True
arcpy.env.workspace = r"D:\Projecten\HDSR\2020\gisData\geomToets.gdb"
workspace = r"D:\Projecten\HDSR\2020\gisData\geomToets.gdb"






trajectenHDSR = "testTraject2"
afstandKruinSegment = 0.5 
minKruinBreedte = 1.5
code_hdsr = "Naam"
toetsniveaus = "th2024"
waterlopenBGTBoezem = "bgt_waterdeel_boezem"
rasterWaterstaatswerk = "WWBAG2mPlusWaterlopenAHN3"
rasterAHN3BAG2m = r"D:\Projecten\HDSR\2020\gisData\basisData.gdb\BAG2mPlusWaterlopenAHN3"

outputFigures = r"C:\Users\Vincent\Desktop\demoGeomtoets"

def maak_profielen(trajectlijn,code,toetsniveau,profielen,refprofielen, bgt_waterdeel_boezem):
    # referentieprofielen maken
    generate_profiles(profiel_interval=25,profiel_lengte_land=140,profiel_lengte_rivier=1000,trajectlijn=trajectlijn,code=code,
    toetspeil=toetsniveau,profielen="tempRefProfielen")
    
    # normale profielen maken 
    generate_profiles(profiel_interval=25,profiel_lengte_land=40,profiel_lengte_rivier=1000,trajectlijn=trajectlijn,code=code,
    toetspeil=toetsniveau,profielen=profielen)

    # profielen knippen buitenzijde: BAG
    copy_trajectory_lr(trajectlijn=trajectlijn,code=code)
    split_profielen(profielen=profielen,trajectlijn=trajectlijn,code=code)

    # snijpunten van rivierzijde profieldelen en boezemwaterlopen
    arcpy.Intersect_analysis(["profieldeel_rivier",bgt_waterdeel_boezem], "tempSplitBoezem", "ALL", "", "POINT")
    arcpy.SplitLineAtPoint_management(profielen, "tempSplitBoezem", "tempProfielenSplit", "1 Meters")
    arcpy.MakeFeatureLayer_management("tempProfielenSplit", "tempProfiellayer") 
   
    arcpy.SelectLayerByLocation_management("tempProfiellayer", "INTERSECT", trajectlijn, "", "NEW_SELECTION", "NOT_INVERT")
    arcpy.CopyFeatures_management("tempProfiellayer", "tempProfielen")

    # routes maken normale profielen
    profielCursor = arcpy.da.UpdateCursor("tempProfielen", ["van","tot","SHAPE@LENGTH"])
    for row in profielCursor:
        lengte = row[2]
        row[0] = 0
        row[1] = lengte
        profielCursor.updateRow(row)

    
    del profielCursor
    arcpy.CreateRoutes_lr("tempProfielen", "profielnummer", "profielen","TWO_FIELDS", "van", "tot", "UPPER_LEFT", "1", "0", "IGNORE", "INDEX")

    # routes maken refprofielen
    profielCursor = arcpy.da.UpdateCursor("tempRefProfielen", ["van","tot","SHAPE@LENGTH"])
    for row in profielCursor:
        lengte = row[2]
        row[0] = 0
        row[1] = lengte
        profielCursor.updateRow(row)

    
    del profielCursor
    arcpy.CreateRoutes_lr("tempRefProfielen", "profielnummer", "refprofielen","TWO_FIELDS", "van", "tot", "UPPER_LEFT", "1", "0", "IGNORE", "INDEX")




def bepaal_kruinvlak_toetsniveau(trajectlijn,rasterWaterstaatswerk,toetsniveau,profielen,refprofielen):
    # maak buffer van traject om raster te knippen
    arcpy.Buffer_analysis(trajectlijn, "tempBufferTrajectlijn", "10 Meters", "FULL", "ROUND", "NONE", "", "PLANAR")

    # knip buffer uit totaalraster
    arcpy.Clip_management(rasterWaterstaatswerk,"", "tempRaster", "tempBufferTrajectlijn", "-3,402823e+038", "ClippingGeometry", "MAINTAIN_EXTENT")
    

    # raster calculator, selecteer deel op en boven toetsniveau
    raster = arcpy.Raster("tempRaster")
    outraster = raster >= toetsniveau
    outraster.save("tempRasterCalc")

    # arcpy.gp.FocalStatistics_sa("tempRasterCalc", "tempRasterCalcFocal", "Rectangle 3 3 CELL", "MEAN", "DATA")

    # raster vertalen naar polygon en alleen deel boven toetsniveau overhouden (gridcode = 1)
    arcpy.RasterToPolygon_conversion("tempRasterCalc", "tempRasterPoly", "SIMPLIFY", "Value")
    arcpy.Select_analysis("tempRasterPoly", "temp_opBovenTn", "gridcode = 1")


    # knip profielen op vlak "opBovenTn"
    arcpy.Intersect_analysis([profielen,"temp_opBovenTn"], "tempSplitKruin", "ALL", "", "POINT")
    arcpy.SplitLineAtPoint_management(profielen, "tempSplitKruin", "splitTempProfielen", "1 Meters")
    arcpy.MakeFeatureLayer_management("splitTempProfielen", "tempProfiellayer") 

    arcpy.SelectLayerByLocation_management("tempProfiellayer", "WITHIN", "temp_opBovenTn", "", "NEW_SELECTION", "NOT_INVERT")
    arcpy.CopyFeatures_management("tempProfiellayer", "profielDelenOpBovenTn")

    # samenvoegen delen die 0,5 m van elkaar afliggen
    sr = arcpy.SpatialReference(28992)
    arcpy.CreateFeatureclass_management(workspace, "kruindelenTraject", "POLYLINE",spatial_reference= sr)
    arcpy.AddField_management("kruindelenTraject","profielnummer","DOUBLE", 2, field_is_nullable="NULLABLE")
    kruindelenCursor = arcpy.da.InsertCursor("kruindelenTraject", ["profielnummer","SHAPE@"])


    kruinCursor = arcpy.da.UpdateCursor("profielDelenOpBovenTn",["profielnummer","SHAPE@"],sql_clause=(None, 'ORDER BY profielnummer ASC'))
    
    for profielnummer, group in groupby(kruinCursor, lambda x: x[0]):

        kruinDelenGroep = []
        for kRow in group:
            kruinDelenGroep.append(kRow[1])
        
        # samenvoegen
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


            kruindelenCursor.insertRow([profielnummer,kruinDeel])
            print profielnummer 
            

        except ValueError:
            pass



def maak_referentieprofielen(profielen,refprofielen,rasterWaterstaatswerk,toetsniveau, minKruinBreedte,refprofielenpunten):
    # maak kruinpunten 
    arcpy.FeatureVerticesToPoints_management("kruindelenTraject", "kruindelenTrajectEindpunten", "BOTH_ENDS")

    # lokaliseer kruinpunten op profielroute
    arcpy.LocateFeaturesAlongRoutes_lr("kruindelenTrajectEindpunten", refprofielen, "profielnummer", "0,1 Meters", "kruindelenTable", "RID POINT MEAS", "FIRST", "DISTANCE", "ZERO", "FIELDS", "M_DIRECTON")
    arcpy.JoinField_management("kruindelenTrajectEindpunten","OBJECTID","kruindelenTable","OBJECTID","MEAS")

    # onderscheid maken binnen/buitenkant
    arcpy.AddField_management("kruindelenTrajectEindpunten","locatie","TEXT", field_length=50)
    arcpy.AddField_management("kruindelenTrajectEindpunten","z_ref","DOUBLE", 2, field_is_nullable="NULLABLE")

    
    kruinDict = {}

    kruinPuntenCursor = arcpy.da.SearchCursor("kruindelenTrajectEindpunten",["profielnummer","MEAS","locatie"],sql_clause=(None, 'ORDER BY profielnummer ASC'))

    for profielnummer, group in groupby(kruinPuntenCursor, lambda x: x[0]):
        profielnummer = int(profielnummer)
        firstMEAS = round(group.next()[1],2)
        secondMEAS = round(group.next()[1],2)

        measList = [firstMEAS,secondMEAS]
        minMeas = min(measList)
        maxMeas = max(measList)

        kruinDict[profielnummer] = minMeas, maxMeas
    
    del kruinPuntenCursor

    kruinPuntenCursor = arcpy.da.UpdateCursor("kruindelenTrajectEindpunten",["profielnummer","MEAS","locatie","z_ref"],sql_clause=(None, 'ORDER BY profielnummer ASC'))
    
    for kRow in kruinPuntenCursor:
        if int(kRow[0]) in kruinDict:
            if round(kRow[1],2) == kruinDict[int(kRow[0])][0]:
            
                kRow[2] = "kruin binnenzijde"
            if round(kRow[1],2) == kruinDict[int(kRow[0])][1]:
                kRow[2] = "kruin buitenzijde"

        kRow[3] = toetsniveau
        kruinPuntenCursor.updateRow(kRow)

    del kruinPuntenCursor

    
    
    
    # invoegen eindpunten refprofiel:
    # ophalen measwaarde kruinpunt buiten: binnen = - 106,5 (105+1,5m profielbreedte), buiten = +30



    arcpy.CreateTable_management(workspace, "refProfielTabel", "", "")
   
   
    arcpy.AddField_management("refProfielTabel","profielnummer", "DOUBLE", 2, field_is_nullable="NULLABLE")
    arcpy.AddField_management("refProfielTabel","locatie","TEXT", field_length=50)
    arcpy.AddField_management("refProfielTabel","afstand","DOUBLE", 2, field_is_nullable="NULLABLE")

    refPuntenCursor = arcpy.da.InsertCursor("refProfielTabel", ["profielnummer","locatie","afstand"])
  

    for profielnr, waardes in kruinDict.iteritems():
        measKruinBuiten = waardes[1]
        measKruinBinnen = measKruinBuiten-minKruinBreedte
        measRefPuntBuiten = measKruinBuiten+30
        measRefPuntBinnen = measKruinBinnen-105

       
        refPuntenCursor.insertRow([profielnr,"eindpunt binnenzijde",measRefPuntBinnen])
        refPuntenCursor.insertRow([profielnr,"eindpunt buitenzijde",measRefPuntBuiten])
        refPuntenCursor.insertRow([profielnr,"kruinpunt binnenzijde",measKruinBinnen])
        refPuntenCursor.insertRow([profielnr,"kruinpunt buitenzijde",measKruinBuiten])



    del refPuntenCursor
    # losse route per profiel maken

    arcpy.MakeRouteEventLayer_lr(refprofielen, "profielnummer", "refProfielTabel", "profielnummer POINT afstand", "tempRefProfielen", "", "NO_ERROR_FIELD", "NO_ANGLE_FIELD", "NORMAL", "ANGLE", "LEFT", "POINT")
    arcpy.CopyFeatures_management("tempRefProfielen", refprofielenpunten)


    # koppelen hoogtewaardes
    arcpy.AddField_management("refProfielenPunten","z_ref", "DOUBLE", 2, field_is_nullable="NULLABLE")

    refPuntenCursor = arcpy.da.UpdateCursor("refProfielenPunten",["locatie","z_ref"])

    for rRow in refPuntenCursor:
        if "kruinpunt" in rRow[0]:
            rRow[1] = toetsniveau
        if "eindpunt" in rRow[0]:
            rRow[1] = -15
        
        refPuntenCursor.updateRow(rRow)

    del refPuntenCursor








def testplot(profielen, refprofielen, refprofielenpunten,rasterAHNBAG):


    # stringveld aanmaken voor profielen en refprofielen voor individuele selectie
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

    

    # per profielnummer refprofielplotten en gewone profiel plotten

    with arcpy.da.SearchCursor(profielen,["SHAPE@","profielnummer_str"]) as profielCursor:
        for pRow in profielCursor:

            profielnummer = pRow[1]
            tempprofiel = "tempprofiel"
            temprefpunten = "temprefpunten"
            temprefprofiel = "temprefprofiel"
            
            # selecteer betreffend profiel en kopieer naar tijdelijke laag
            where = '"' + 'profielnummer_str' + '" = ' + "'" + profielnummer + "'"
            arcpy.Select_analysis(profielen, tempprofiel, where)

            # selecteer referentiepunten van betreffend profiel en kopieer naar tijdelijke laag
            arcpy.Select_analysis(refprofielenpunten, temprefpunten, where)

            # selecteer betreffend referentieprofiel voor localisatie profielpunten
            arcpy.Select_analysis(refprofielen, temprefprofiel, where)
            





            # creer routes voor punten profiel
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

            # creer routes voor refprofiel
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
            ExtractValuesToPoints("puntenRoute", rasterAHNBAG, "puntenRouteZ","INTERPOLATE", "VALUE_ONLY")
            arcpy.AlterField_management("puntenRouteZ", 'RASTERVALU', 'z_ahn')



            # plotten 
            arrayRefProfile = arcpy.da.FeatureClassToNumPyArray("temprefpunten", ('profielnummer','afstand','z_ref'))
            refDf = pd.DataFrame(arrayRefProfile)
            sortrefDf = refDf.sort_values(by=['profielnummer','afstand'],ascending=[True, True])

            arrayProfile = arcpy.da.FeatureClassToNumPyArray("puntenRouteZ", ('afstand','z_ahn'))
            profileDf = pd.DataFrame(arrayProfile)
            sortProfileDf = profileDf.sort_values(by=['afstand'],ascending=[True])


            plt.style.use('seaborn-whitegrid') #seaborn-ticks
            fig = plt.figure(figsize=(80, 10))
        
        
            ax1 = fig.add_subplot(111, label ="1")

            ax1.plot(sortrefDf['afstand'],sortrefDf['z_ref'],label="Referentie-profiel",linewidth=3)
            ax1.plot(sortProfileDf['afstand'],sortProfileDf['z_ahn'],label="AHN3-profiel")



            # plt.show()

            plt.savefig("{}/{}.png".format(outputFigures,profielnummer))
            plt.close()

            print profielnummer




          






    # arrayRefProfile = arcpy.da.FeatureClassToNumPyArray("refProfielenPunten", ('profielnummer','afstand','z_ref'))
    # refDf = pd.DataFrame(arrayRefProfile)
    # sortrefDf = refDf.sort_values(by=['profielnummer','afstand'],ascending=[True, True])

    # groupedRef = sortrefDf.groupby(["profielnummer",])

    # for name, group in groupedRef:
        
    #     plt.style.use('seaborn-whitegrid') #seaborn-ticks
    #     fig = plt.figure(figsize=(60, 10))
        
        
    #     ax1 = fig.add_subplot(111, label ="1")
    #     ax1.plot(group['afstand'],group['z_ref'],label="Refprofiel")



    #     plt.show()




    










with arcpy.da.SearchCursor(trajectenHDSR,['SHAPE@',code_hdsr,toetsniveaus]) as cursor:
    for row in cursor:
        
        # lokale variabelen per dijktraject
        code = code_hdsr
        toetsniveau = float(row[2])
        id = row[1]
        
        profielen = "profielen"
        refprofielen = "refprofielen"
        trajectlijn = "tempTrajectlijn"

        refprofielenpunten = "refProfielenPunten"

        # selecteer betreffend traject en kopieer naar tijdelijke laag
        where = '"' + code_hdsr + '" = ' + "'" + str(id) + "'"
        arcpy.Select_analysis(trajectenHDSR, trajectlijn, where)


        ## stap 1: profielen op juiste maat maken
        # maak_profielen(trajectlijn=trajectlijn,code=code,toetsniveau=toetsniveau,profielen=profielen, refprofielen=refprofielen, bgt_waterdeel_boezem=waterlopenBGTBoezem)

        ## stap 2: bepaal gedeelte dat op-boven toetsniveau ligt
        # bepaal_kruinvlak_toetsniveau(trajectlijn=trajectlijn,rasterWaterstaatswerk=rasterWaterstaatswerk,toetsniveau=toetsniveau,profielen=profielen,refprofielen=refprofielen)

        ## stap 3: bepaal referentieprofiel (begin aan buitenzijde)
        # maak_referentieprofielen(profielen=profielen,refprofielen=refprofielen, rasterWaterstaatswerk=rasterWaterstaatswerk,toetsniveau=toetsniveau,minKruinBreedte=minKruinBreedte,refprofielenpunten= refprofielenpunten)

        testplot(profielen=profielen,refprofielen=refprofielen, refprofielenpunten=refprofielenpunten,rasterAHNBAG=rasterAHN3BAG2m)