import arcpy
from arcpy.sa import *
from itertools import groupby
import pandas as pd

sys.path.append('HDSR2020')
from basisRWK2020 import generate_profiles, copy_trajectory_lr, splitProfielen



arcpy.env.overwriteOutput = True
arcpy.env.workspace = r"D:\Projecten\HDSR\2020\gisData\geomToets.gdb"


trajectenHDSR = "testTraject2"
code_hdsr = "Naam"
toetsniveaus = "th2024"
rasterWaterstaatswerk = "WWBAG2mPlusWaterlopenAHN3"
rasterTotaal = r"D:\Projecten\HDSR\2020\gisData\basisData.gdb\BAG2mPlusWaterlopenAHN3"
waterstaatswerkHDSR = "waterstaatswerkHDSR"
waterlopenBGT = "bgt_waterdeel"



minimaleKruinBreedte = 1.5
maximaalTaludBuitenzijde = 0.5


def controleerKruinBreedte(profielen, waterstaatswerk,opBovenTn,profielenUitvoer,kruinDelenUitvoer):
        # knip profielen op waterstaatswerk
        arcpy.Intersect_analysis([profielen,waterstaatswerk], "tempSplitPoints", "ALL", "", "POINT")
        arcpy.SplitLineAtPoint_management(profielen, "tempSplitPoints", "tempProfielen", "1 Meters")
        arcpy.MakeFeatureLayer_management("tempProfielen", "tempProfiellayer") 
   
        arcpy.SelectLayerByLocation_management("tempProfiellayer", "WITHIN", waterstaatswerk, "", "NEW_SELECTION", "NOT_INVERT")
        arcpy.CopyFeatures_management("tempProfiellayer", "profielDelenWS")

        # knip profielen op vlak "opBovenTn"
        arcpy.Intersect_analysis([profielen,opBovenTn], "tempSplitPoints", "ALL", "", "POINT")
        arcpy.SplitLineAtPoint_management(profielen, "tempSplitPoints", "tempProfielen", "1 Meters")
        arcpy.MakeFeatureLayer_management("tempProfielen", "tempProfiellayer") 
   
        arcpy.SelectLayerByLocation_management("tempProfiellayer", "WITHIN", opBovenTn, "", "NEW_SELECTION", "NOT_INVERT")
        arcpy.CopyFeatures_management("tempProfiellayer", "profielDelenOpBovenTn")

        # check per profielnummer of een gedeelte op of boven toetsniveau aanwezig is. Profiel voorzien van opmerking (voldoende/onvoldoende)
        profielenTraject = {}

        profielDeelCursor = arcpy.da.UpdateCursor("profielDelenOpBovenTn",["profielnummer","SHAPE@LENGTH"],sql_clause=(None, 'ORDER BY profielnummer ASC'))
        
        for profielnummer, group in groupby(profielDeelCursor, lambda x: x[0]):
            
            profielDelenVoldoende = 0 # lege lijst voor aantal profieldelen per profiel dat voldoet aan breedte-eis
            profielDelenOnvoldoende = 0 # lege lijst voor aantal profieldelen per profiel dat niet voldoet aan breedte-eis
            
           
            for row in group:
                if row[1] >= minimaleKruinBreedte:
                    profielDelenVoldoende += 1
                if row[1] < minimaleKruinBreedte:
                    profielDelenOnvoldoende += 1
            
            if profielDelenVoldoende > 0:
                profielenTraject[profielnummer] = "voldoende", profielDelenVoldoende

            if profielDelenVoldoende == 0:
                profielenTraject[profielnummer] = "onvoldoende", profielDelenOnvoldoende
                


        # print profielenTraject

        del profielDeelCursor    
        
        arcpy.AddField_management("profielen","krBreedte","TEXT", field_length=150)
        arcpy.AddField_management("profielen","ctrlEis","TEXT", field_length=150)
        
        profielCursor = arcpy.da.UpdateCursor("profielen",["profielnummer","krBreedte","ctrlEis"])

        for pRow in profielCursor:
            try:
                profielnummer = int(pRow[0])
                oordeel = profielenTraject[profielnummer][0]
                profieldelen = profielenTraject[profielnummer][1]

                if oordeel == "voldoende" and profieldelen ==1:
                    pRow[1] = "voldoende"
                    pRow[2] = "1 kruindeel"

    

                if oordeel == "voldoende" and profieldelen > 1:
                    pRow[1] = "voldoende"
                    pRow[2] = "meerdere voldoende kruindelen, controleer resultaat"

                
                if oordeel =="onvoldoende" and profieldelen > 1:
                    pRow[1] = "onvoldoende"
                    pRow[2] = "meerdere onvoldoende kruindelen, controleer resultaat"

                
                
                if oordeel =="onvoldoende" and profieldelen == 1 :
                    pRow[1] = "onvoldoende"
                    pRow[2] = "1 kruindeel"

            
                profielCursor.updateRow(pRow)

            except KeyError:
                pRow[1] = "onvoldoende"
                pRow[2] = "geen kruindeel"
                profielCursor.updateRow(pRow)
                print "Geen kruindelen aanwezig voor profielnummer {}".format(profielnummer)



        # kopieer profielen als vaste laag 
        arcpy.Copy_management("profielen",profielenUitvoer)

        # kopieer profieldeel op-boven tn als vaste laag (?) 
        arcpy.Copy_management("profielDelenOpBovenTn", kruinDelenUitvoer)


def controleerBuitenTalud(profielenUitvoer,waterlopenvlak,trajectlijn,code,hoogtedata,kruindelen):
    
    # snijpunten profielen met watervlak 
    arcpy.Intersect_analysis([profielenUitvoer,waterlopenvlak], "tempIsectWaterloop", "ALL", "", "POINT")
    arcpy.MultipartToSinglepart_management("tempIsectWaterloop","tempIsectWaterloopPoint")


    # maak route van profiel
    veldenProfielen = [f.name for f in arcpy.ListFields(profielenUitvoer)]
    veldenRoute = ["van","tot"]
    for veld in veldenRoute:
        if veld in veldenProfielen:
            pass
        else: 
            arcpy.AddField_management(profielenUitvoer,veld,"DOUBLE", 2, field_is_nullable="NULLABLE")

    profielCursor = arcpy.da.UpdateCursor(profielenUitvoer, ["van","tot","SHAPE@LENGTH"])
    for row in profielCursor:
        lengte = row[2]
        row[0] = 0
        row[1] = lengte
        profielCursor.updateRow(row)

    
    del profielCursor
    arcpy.CreateRoutes_lr(profielenUitvoer, "profielnummer", 'profielRoutes',"TWO_FIELDS", "van", "tot", "UPPER_LEFT", "1", "0", "IGNORE", "INDEX")

    # localiseer isect over route
    arcpy.LocateFeaturesAlongRoutes_lr("tempIsectWaterloopPoint", "profielRoutes", "profielnummer", "0,1 Meters", "testOutTable", "RID POINT MEAS", "FIRST", "DISTANCE", "ZERO", "FIELDS", "M_DIRECTON")
    arcpy.JoinField_management("tempIsectWaterloopPoint","OBJECTID","testOutTable","OBJECTID","MEAS")

    # controleer of punt buitentalud/binnentalud is
    copy_trajectory_lr(trajectlijn=trajectlijn,code=code_hdsr)
    splitProfielen(profielen=profielenUitvoer,trajectlijn=trajectlijn,code=code_hdsr)

    arcpy.MakeFeatureLayer_management("tempIsectWaterloopPoint", "temp_tempIsectWaterloopPoint") 
    arcpy.SelectLayerByLocation_management("temp_tempIsectWaterloopPoint", "WITHIN", "profieldeel_rivier", "", "NEW_SELECTION", "NOT_INVERT")
    arcpy.CopyFeatures_management("temp_tempIsectWaterloopPoint", "isectWaterloopBuiten")

    # zekerheidscheck: controleer of er 1 snijpunt per profiel is: degene met de laagste MEAS
    # ter voorkoming van mogelijk snijpunt met waterlijn overzijde... 
    
    iSectBoezemCursor = arcpy.da.SearchCursor("isectWaterloopBuiten",["profielnummer","MEAS"],sql_clause=(None, 'ORDER BY profielnummer ASC'))
    removeList = []
    
    # eerst kijken of er meerdere snijpunten per profiel zijn:
    for profielnummer, group in groupby(iSectBoezemCursor, lambda x: x[0]):
        
        profielnummer = int(profielnummer)

        aantalIsectsProfiel = 0
   
 
        
        for iRow in group:
            newRow = pd.Series({"profielnummer": iRow[0], "meas": iRow[1]})
 
            aantalIsectsProfiel += 1

   

        if aantalIsectsProfiel > 1:
            removeList.append(profielnummer)

    del iSectBoezemCursor    
    

    # daarna alleen dichtstbijzijnde snijpunt aan buitenzijde overhouden:
    isectRemoveCursor = arcpy.da.UpdateCursor("isectWaterloopBuiten",["profielnummer","MEAS"],sql_clause=(None, 'ORDER BY profielnummer ASC'))

    for profielnummer, group in groupby(isectRemoveCursor, lambda x: x[0]):
        profielnummer = int(profielnummer)
        
        count = 0

        
        firstMEAS = round(group.next()[1],2)
        for iRow in group:
            MEAS = round(iRow[1],2)
            if MEAS == firstMEAS:
                pass
            else:
                isectRemoveCursor.deleteRow()


    del isectRemoveCursor

    # boezemniveau bepalen: gemiddelde van hoogtewaarde van alle boezemsnijpunten per traject
    arcpy.CheckOutExtension("Spatial")
    ExtractValuesToPoints("isectWaterloopBuiten", hoogtedata, "isectWaterloopBuitenZ","INTERPOLATE", "VALUE_ONLY")
    arcpy.AlterField_management("isectWaterloopBuitenZ", 'RASTERVALU', 'z_ahn')

    arcpy.Statistics_analysis("isectWaterloopBuitenZ", "gemBoezemPeil", "z_ahn MEAN", "")
    try:
        gemBoezemPeil = [z[0] for z in arcpy.da.SearchCursor ("gemBoezemPeil", ["MEAN_z_ahn"])][0]
        print gemBoezemPeil
    except IndexError:
        print "Geen boezem aanwezig, wat doen we hier?"


    # pandas truckje om OBJECTID's met maxlengte te vinden (en te verwijderen)
    array = arcpy.da.FeatureClassToNumPyArray(kruindelen, ('profielnummer','SHAPE@LENGTH','OBJECTID'))
    df = pd.DataFrame(array)
    sortDf = df.sort_values(by=['profielnummer'])
    idx = sortDf.groupby(['profielnummer'])['SHAPE@LENGTH'].transform(max) == sortDf['SHAPE@LENGTH']
    dfFinal = sortDf[idx]
    maxList = dfFinal["OBJECTID"].tolist()

 

    removeKruinDelenCursor = arcpy.da.UpdateCursor(kruindelen,["OBJECTID"])

    for iRow in removeKruinDelenCursor:
        if int(iRow[0]) in maxList:
            pass
        else:
            removeKruinDelenCursor.deleteRow()

    del removeKruinDelenCursor

  
    arcpy.FeatureVerticesToPoints_management(kruindelen, "kruinPunten", "END")

    # maaiveldhoogte berekenen kruinPunten
    # samenvoegen kruinpunten en isectWaterlopenBuiten
    # hoek berekenen tussen punten 
    # hoek terugkoppelen aan profiellijn




        
        


    




# selecteer keringlijn
with arcpy.da.SearchCursor(trajectenHDSR,['SHAPE@',code_hdsr,toetsniveaus]) as cursor:
    for row in cursor:
        
        
        # lokale variabelen per dijktraject
        code = code_hdsr
        toetsniveau = float(row[2])
        id = row[1]
        
        # uitvoer voor controleruns
        # trajectlijn = 'deeltraject_'+str(row[1])
        # buffertrajectlijn = 'buffer_deeltraject_'+str(row[1])
        opBovenTn = 'opBovenTn_deeltraject_'+str(row[1])
        
        
        # uitvoer voor definitieve runs
        profielen = "profielen"
        trajectlijn = "tempTrajectlijn"
        buffertrajectlijn = "tempBuffer"
        profielenUitvoer = 'profielen_'+str(row[1])
        kruinDelenUitvoer = 'kruindelen_'+str(row[1])
        
        
        # selecteer betreffend traject
        where = '"' + code_hdsr + '" = ' + "'" + str(id) + "'"
        arcpy.Select_analysis(trajectenHDSR, trajectlijn, where)

        # maak buffer van traject om raster te knippen
        arcpy.Buffer_analysis(trajectlijn, buffertrajectlijn, "10 Meters", "FULL", "ROUND", "NONE", "", "PLANAR")

        # knip buffer uit totaalraster
        arcpy.Clip_management(rasterWaterstaatswerk,"", "tempRaster", buffertrajectlijn, "-3,402823e+038", "ClippingGeometry", "MAINTAIN_EXTENT")
        

        # raster calculator, selecteer deel op en boven toetsniveau
        raster = arcpy.Raster("tempRaster")
        outraster = raster >= toetsniveau
        outraster.save("tempRasterCalc")

        # raster vertalen naar polygon en alleen deel boven toetsniveau overhouden (gridcode = 1)
        arcpy.RasterToPolygon_conversion("tempRasterCalc", "tempRasterPoly", "SIMPLIFY", "Value")
        arcpy.Select_analysis("tempRasterPoly", opBovenTn, "gridcode = 1")

        # profielen maken op trajectlijn
        generate_profiles(profiel_interval=10,profiel_lengte_land=15,profiel_lengte_rivier=15,trajectlijn=trajectlijn,code=code,toetspeil=toetsniveau,profielen=profielen)


        


        # functies runnen
        controleerKruinBreedte(profielen=profielen,waterstaatswerk = waterstaatswerkHDSR, opBovenTn = opBovenTn, profielenUitvoer =profielenUitvoer,kruinDelenUitvoer= kruinDelenUitvoer)
        
        controleerBuitenTalud(profielenUitvoer=profielenUitvoer,waterlopenvlak=waterlopenBGT,trajectlijn=trajectlijn,code=code_hdsr,hoogtedata=rasterTotaal,kruindelen=kruinDelenUitvoer)


        print id

 




        





