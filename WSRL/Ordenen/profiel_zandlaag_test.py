import arcpy
import os
import xlrd
arcpy.env.overwriteOutput = True

arcpy.env.workspace = r'C:/Users/vince/Desktop/GIS/zandlagen_safe.gdb'

#create namelist
invoegen = ["stph_100m", "zandlaag_xls_xz0_route"]
aantallen = range(0,39)
#print range
for i in aantallen:
    naam = "zandlaag_xls_xz"+str(i)+"_route"
    #invoegen.append(naam)


# run intersect

#list_features = []
intersectOutput = "testlaag_lijn"
clusterTolerance = 1.5
arcpy.Intersect_analysis(invoegen, intersectOutput, "", clusterTolerance, "point")