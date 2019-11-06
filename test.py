import arcpy
import math
from arcpy.sa import *
import xlwt
import pandas as pd
from itertools import groupby
# uitzetten melding pandas
pd.set_option('mode.chained_assignment', None)
from basisfuncties import*

arcpy.env.workspace = r'D:\Projecten\HDSR\data\test_batch.gdb'
arcpy.env.overwriteOutput = True


profiel_interval = 15
profiel_lengte = 35

invoerpunten = 'punten_profielen'

stapgrootte_punten = 0.5
afronding = 1
raster = r'D:\Projecten\HDSR\data\ahn_hdsr.gdb\AHN3grondfilter'
code = 'SUBSECT_ID'








trajecten = 'trajecten_test'
with arcpy.da.SearchCursor(trajecten,['SHAPE@','SUBSECT_ID']) as cursor:
    for row in cursor:
        code = 'SUBSECT_ID'
        id = row[1]
        trajectlijn = 'deeltraject_'+str(row[1])
        profielen = 'profielen_'+str(row[1])
        uitvoerpunten = 'punten_profielen_z_'+str(row[1])
        resultfile = 'C:/Users/Vincent/Desktop/xls_uitvoer/'+str(row[1])+'.xls'

        where = '"' + code + '" = ' + "'" + str(id) + "'"
        # arcpy.CopyFeatures_management(row[0], trajectlijn)
        arcpy.Select_analysis(trajecten, trajectlijn, where)


        generate_profiles(profiel_interval, profiel_lengte, trajectlijn, code, profielen)
        copy_trajectory_lr(trajectlijn, code)
        set_measurements_trajectory(profielen, trajectlijn, code, stapgrootte_punten)
        extract_z_arcpy(invoerpunten, uitvoerpunten, raster)
        add_xy(uitvoerpunten, code)
        to_excel(uitvoerpunten, resultfile)

        kruinhoogte_groepen(uitvoerpunten, stapgrootte_punten, afronding, code)
        max_kruinhoogte(uitvoerpunten, profielen, code)
        # break