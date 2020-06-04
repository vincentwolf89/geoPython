import sys
sys.path.append('.')


import arcpy
import math
from arcpy.sa import *
import xlwt
import pandas as pd
from itertools import groupby
# uitzetten melding pandas
pd.set_option('mode.chained_assignment', None)
from basisfuncties import*

arcpy.env.workspace = r'D:\Projecten\WSRL\temp_sh.gdb'
arcpy.env.overwriteOutput = True


profiel_interval = 25
stapgrootte_punten = 0.5
profiel_lengte_land = 200
profiel_lengte_rivier = 200

trajectlijn = "trajectlijnSHv2"
code = "dijktraject"

raster = r'D:\Projecten\WSRL\temp_sh.gdb\ahn3clipsh1'

# uitvoer/invoer
profielen = "profielen"
invoerpunten = "punten_profielen"
uitvoerpunten = "punten_profielen_z"
excel = r'C:\Users\Vincent\Desktop\profielenShV1.xlsx'
veldnamen =['profielnummer','metreringDp', 'afstand', 'z_ahn', 'x', 'y']


## runner
generate_profiles(profiel_interval,profiel_lengte_land,profiel_lengte_rivier,trajectlijn,code,5,profielen)

copy_trajectory_lr(trajectlijn,code)

set_measurements_trajectory(profielen,trajectlijn,code,stapgrootte_punten,5)

extract_z_arcpy(invoerpunten,uitvoerpunten,raster)

add_xy(uitvoerpunten, code,trajectlijn)

excelWriterTraject(uitvoerpunten,excel,veldnamen)







