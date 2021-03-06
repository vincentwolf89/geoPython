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

arcpy.env.workspace = r'D:\Projecten\HDSR\2020\gisData\inputDAM.gdb'
arcpy.env.overwriteOutput = True


profiel_interval = 25
stapgrootte_punten = 0.1
profiel_lengte_land = 500
profiel_lengte_rivier = 200

trajectlijn = r"D:\Projecten\HDSR\2020\gisData\cPointsPilot.gdb\pilotTrajecten"
code = "Naam"

raster = r'D:\Projecten\HDSR\2020\gisData\basisData.gdb\BAG2mPlusWaterlopenAHN3'

# uitvoer/invoer
profielen = r"D:\Projecten\HDSR\2020\gisData\cPointsPilot.gdb\profielenPilot"

# defaultuitvoer
invoerpunten = "punten_profielen"
uitvoerpunten = "punten_profielen_z"
excel = r'D:\Projecten\WSRL\safe\lekdata\uitvoerProfielen\profielenLekV3.xlsx'
veldnamen =['profielnummer', 'afstand', 'z_ahn', 'x', 'y']


## runner
# generate_profiles(profiel_interval,profiel_lengte_land,profiel_lengte_rivier,trajectlijn,code,5,profielen)

copy_trajectory_lr(trajectlijn,code,10)

set_measurements_trajectory(profielen,trajectlijn,code,stapgrootte_punten,10)

extract_z_arcpy(invoerpunten,uitvoerpunten,raster)

add_xy(uitvoerpunten, code,trajectlijn)

# excelWriterTraject(uitvoerpunten,excel,veldnamen)







