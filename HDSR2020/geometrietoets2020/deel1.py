import arcpy


sys.path.append('HDSR2020')

from basisRWK2020 import generate_profiles



arcpy.env.overwriteOutput = True
arcpy.env.workspace = r"D:\Projecten\HDSR\2020\gisData\geomToets.gdb"


trajectenHDSR = "testTrajecten"
code_hdsr = "Naam"
toetsniveaus = "th2024"
rasterWaterstaatswerk = "WWBAG2mPlusWaterlopenAHN3"

# selecteer keringlijn
with arcpy.da.SearchCursor(trajectenHDSR,['SHAPE@',code_hdsr,toetsniveaus]) as cursor:
    for row in cursor:
        
        
        # lokale variabelen per dijktraject
        code = code_hdsr
        toetsniveau = float(row[2])
        id = row[1]
        
        # uitvoer opbouw
        trajectlijn = 'deeltraject_'+str(row[1])
        buffertrajectlijn = 'buffer_deeltraject_'+str(row[1])
        opBovenTn = 'opBovenTn_deeltraject_'+str(row[1])
        profielen = 'profielen_'+str(row[1])
        
        
        # selecteer betreffend traject
        where = '"' + code_hdsr + '" = ' + "'" + str(id) + "'"
        arcpy.Select_analysis(trajectenHDSR, trajectlijn, where)

        # maak buffer van traject om raster te knippen
        arcpy.Buffer_analysis(trajectlijn, buffertrajectlijn, "10 Meters", "FULL", "FLAT", "NONE", "", "PLANAR")

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

        



        print trajectlijn
 




        







# bereken rasterdeel boven/op th: rasterKruin

# maak/gebruik profielen

# per profiel zone in rasterKruin bepalen