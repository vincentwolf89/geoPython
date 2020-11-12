import arcpy
from itertools import groupby

sys.path.append('HDSR2020')
from basisRWK2020 import generate_profiles



arcpy.env.overwriteOutput = True
arcpy.env.workspace = r"D:\Projecten\HDSR\2020\gisData\geomToets.gdb"


trajectenHDSR = "testTrajecten"
code_hdsr = "Naam"
toetsniveaus = "th2024"
rasterWaterstaatswerk = "WWBAG2mPlusWaterlopenAHN3"
waterstaatswerkHDSR = "waterstaatswerkHDSR"
minimaleKruinBreedte = 1.5


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

        profielDeelCursor = arcpy.da.UpdateCursor("profielDelenOpBovenTn",["profielnummer","SHAPE@LENGTH"])
        
        for profielnummer, group in groupby(profielDeelCursor, lambda x: x[0]):
            
            profielDelenVoldoende = 0 # lege lijst voor aantal profieldelen per profiel dat voldoet aan breedte-eis
            profielDelenOnvoldoende = 0 # lege lijst voor aantal profieldelen per profiel dat niet voldoet aan breedte-eis
            
            voldoendeBreedte = False
            for row in group:
                if row[1] >= minimaleKruinBreedte:
                    voldoendeBreedte = True
                    profielDelenVoldoende += 1
                if row[1] < minimaleKruinBreedte:
                    voldoendeBreedte = False
                    profielDelenOnvoldoende += 1
            
            if voldoendeBreedte is True:
                profielenTraject[profielnummer] = "voldoende", profielDelenVoldoende

            if voldoendeBreedte is False:
                profielenTraject[profielnummer] = "onvoldoende", profielDelenOnvoldoende
                


        # print profielenTraject

        del profielDeelCursor    
        
        arcpy.AddField_management("profielen","krBreedte","TEXT", field_length=150)
        arcpy.AddField_management("profielen","ctrlEis","TEXT", field_length=150)
        
        profielCursor = arcpy.da.UpdateCursor("profielen",["profielnummer","krBreedte","ctrlEis"])

        for pRow in profielCursor:
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

         
            
            if oordeel =="onvoldoende" and profieldelen < 1 :
                pRow[1] = "onvoldoende"
                pRow[2] = "geen kruindeel"

            
            profielCursor.updateRow(pRow)

        # kopieer profielen als vaste laag 
        arcpy.Copy_management("profielen",profielenUitvoer)

        # kopieer profieldeel op-boven tn als vaste laag (?) 
        arcpy.Copy_management("profielDelenOpBovenTn", kruinDelenUitvoer)


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


        #
        controleerKruinBreedte(profielen,waterstaatswerkHDSR,opBovenTn,profielenUitvoer,kruinDelenUitvoer)
        



        print id

 




        





