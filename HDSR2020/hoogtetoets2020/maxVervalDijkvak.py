import arcpy
import sys
sys.path.append('.')
import pandas as pd

from basisfuncties import average

arcpy.env.workspace = r'D:\Projecten\HDSR\2020\gisData\basisData.gdb'

arcpy.env.overwriteOutput = True

profielen = 'profielenTotaal'
dijkvakken = 'RWK_areaal_2024'


code_hdsr = ''
# iterate over dijkvakken



with arcpy.da.UpdateCursor(dijkvakken,['Naam','gemVerval','maxVerval']) as dijkvakcursor:
    for row in dijkvakcursor:

        dijkvak = row[0]
        lyr = arcpy.MakeFeatureLayer_management(profielen, 'profielenLyr') 
        
        print dijkvak
        where = '"' + "Naam" + '" = ' + "'" + dijkvak + "'"
        selected = arcpy.SelectLayerByAttribute_management(lyr, "NEW_SELECTION", where)
        arcpy.CopyFeatures_management(selected,"output_test")
        

        peilLijst = []
        vervalLijst = []

        with arcpy.da.SearchCursor("output_test",['minPeil','maxVervalProfiel']) as profielcursor:
            for item in profielcursor:
                if item[0] == -999:
                    pass
                else:
                    peilLijst.append(item[0])
                    vervalLijst.append(item[1])

        if peilLijst:
            gemVerval = average(vervalLijst)
            maxVerval = max(vervalLijst)

            row[1] = round(gemVerval,2)
            row[2] = round(maxVerval,2)

            del gemVerval, maxVerval, profielcursor
        else:
            row[1] = -999
            row[2] = -999

        dijkvakcursor.updateRow(row)



    
