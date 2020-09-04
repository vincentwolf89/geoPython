import os

import arcpy
from arcpy.sa import *
arcpy.CheckOutExtension('Spatial')


arcpy.env.overwriteOutput = True
arcpy.env.workspace = r'D:\Projecten\HDSR\2020\gisData\rastersBAG.gdb'


pandenPlus5 = r"D:\Projecten\HDSR\2020\gisData\basisData.gdb\pandenBag30mplus2"
raster = r"D:\Projecten\HDSR\2019\data\hoogteData.gdb\AHN3grondfilter"

totalRasters = float(arcpy.GetCount_management(pandenPlus5)[0])


counter = 1
with arcpy.da.UpdateCursor(pandenPlus5,['SHAPE@','Identificatie']) as pandenCursor:
    for row in pandenCursor:
        
        pand = row[0]
        pandNaam = row[1]
        tempPand = "tempPand"
        

        rasterOutput = str(pandNaam)


        # copy feature
        arcpy.CopyFeatures_management(pand, tempPand)


        # clip raster
        arcpy.Clip_management(raster,"", "tempraster", tempPand, "-3,402823e+038", "ClippingGeometry", "MAINTAIN_EXTENT")

        # get mean raster
        try:

            rasterProperties = arcpy.GetRasterProperties_management("tempraster","MEAN")
            gemiddeldeRaster = rasterProperties.getOutput(0)
        
            try:
                gemiddeldeRaster
                arcpy.AddField_management(tempPand,"gemRaster","DOUBLE",2,field_is_nullable="NULLABLE")

                with arcpy.da.UpdateCursor(tempPand,['gemRaster']) as tempPandCursor:
                    for row in tempPandCursor:
                        row[0] = gemiddeldeRaster
                        tempPandCursor.updateRow(row)
                        break


                        
                
                rasterPand = "rasterPand{}".format(counter)
                rasterMerge = "pandMerge{}".format(counter)

                arcpy.PolygonToRaster_conversion(tempPand, "gemRaster", rasterPand,"", "", 0.5)


                outCon = Con(IsNull("tempraster"),rasterPand, "tempraster")

     
                outCon.save(rasterMerge)
                counter +=1



                print "raster gemaakt voor pand {}".format(counter)
                print ((counter/totalRasters)*100)," % gereed"
                
                arcpy.Delete_management("tempraster")
                arcpy.Delete_management(rasterPand)
                

            
            
            except NameError:
                pass
        except arcpy.ExecuteError:
            print "geen statistieken aanwezig"
            pass

       

        
        
        
        
        