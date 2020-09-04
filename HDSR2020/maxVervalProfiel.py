import arcpy
import sys
sys.path.append('.')
import pandas as pd

from basisfuncties import average

arcpy.env.workspace = r'D:\Projecten\HDSR\2020\gisData\basisData.gdb'

arcpy.env.overwriteOutput = True

profielen = 'profielenTotaal'
peilgebieden = 'peilgebiedenRwk'


code_hdsr = ''
# iterate over profielen

with arcpy.da.UpdateCursor(profielen,['SHAPE@','OBJECTID','minPeil']) as profielcursor:
    for row in profielcursor:

        profiel = row[0]
        id = row[1]
        
        arcpy.MakeFeatureLayer_management(peilgebieden, 'peilgebiedenLyr') 
        selected = arcpy.SelectLayerByLocation_management('peilgebiedenLyr', 'intersect', profiel)


        # arcpy.CopyFeatures_management('peilgebiedenLyr',"output_test")


        arcpy.Statistics_analysis(selected, "output_table", "peilHt MIN", "")
        
        
        with arcpy.da.SearchCursor("output_table",['MIN_peilHt']) as peilcursor:
            for item in peilcursor:
                laagstePeil = item[0]
                print item[0], id
                break

        try:
            laagstePeil
            row[2] = laagstePeil
            profielcursor.updateRow(row)
            print "succesvol laagste peil bepaald"
            del laagstePeil
        except NameError:
            pass

        del peilcursor
                  
 

        


        # lokale variabelen per dijktraject
        # code = code_hdsr
        # id = row[1]
        # where = '"' + code_hdsr + '" = ' + "'" + str(id) + "'"

        # # selecteer betreffend traject
        # arcpy.Select_analysis(trajecten, trajectlijn, where)

# select intersecting peilgebieden per profiel

# select peilgebied met laagste peilHt waarde en koppel terug aan profiel


