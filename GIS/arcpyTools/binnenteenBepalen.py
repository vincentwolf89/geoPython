import sys
sys.path.append('.')


import arcpy
import math
from arcpy.sa import *
import pandas as pd
from itertools import groupby
# uitzetten melding pandas
pd.set_option('mode.chained_assignment', None)
from basisfuncties import*

arcpy.env.workspace = r'D:\Projecten\WSRL\temp_sh.gdb'
arcpy.env.overwriteOutput = True


invoer = "punten_profielen_z"
code = "dijktraject"
uitvoer_binnenkruin = "binnenkruin_sh"
uitvoer_buitenkruin = "buitenkruin_sh"
verschil_maxkruin = 0.8
min_afstand = -10
max_afstand = 10

min_achterland = 10
max_achterland = 200
uitvoer_binnenteen = "binnenteen_sh"



# kruinbepalen(invoer, code, uitvoer_binnenkruin, uitvoer_buitenkruin,verschil_maxkruin,min_afstand,max_afstand)
binnenteenbepalen(invoer,code,min_achterland,max_achterland,uitvoer_binnenteen,min_afstand,max_afstand,uitvoer_binnenkruin)