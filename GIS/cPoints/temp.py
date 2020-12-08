import os
import arcpy

arcpy.env.workspace = r"D:\Projecten\HDSR\2020\gisData\cPointsPilotClean.gdb"

dir = r"C:\Users\Vincent\Desktop\cPointsPilot"

list = os.listdir(dir)
profielen = []
for item in list:
    profiel = item.split(".jpg")[0]
    profielen.append(profiel)


featureclasses = arcpy.ListFeatureClasses()

for item in featureclasses:
    if item in profielen:
        print item
    else:

        arcpy.Delete_management(item)


