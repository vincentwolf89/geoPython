import arcpy
import os

arcpy.env.workspace = r'C:\Users\vince\Desktop\GIS\13_1_invoer.gdb'


folder = r'C:\Users\vince\Desktop\klaarzetten 13-1\uitvoer\grensprofielen_tussenraaien'

spRef = "PROJCS['RD_New',GEOGCS['GCS_Amersfoort',DATUM['D_Amersfoort',SPHEROID['Bessel_1841',6377397.155,299.1528128]],PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]],PROJECTION['Double_Stereographic'],PARAMETER['False_Easting',155000.0],PARAMETER['False_Northing',463000.0],PARAMETER['Central_Meridian',5.38763888888889],PARAMETER['Scale_Factor',0.9999079],PARAMETER['Latitude_Of_Origin',52.15616055555555],UNIT['Meter',1.0]];-30515500 -30279500 10000;-100000 10000;-100000 10000;0,001;0,001;0,001;IsHighPrecision"

for filename in os.listdir(folder):
    file = (os.path.join(folder, filename))
    outlayer = 'templaag_'+filename
    savedlayer = filename.replace('.csv','')

    outloc = r'C:\Users\vince\Desktop\GIS\13_1_invoer.gdb'
    arcpy.MakeXYEventLayer_management(file, 'x in RD', 'y in RD', outlayer, spRef, "")
    arcpy.FeatureClassToFeatureClass_conversion(outlayer,outloc,savedlayer)

