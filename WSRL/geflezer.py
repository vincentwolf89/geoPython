import arcpy
import pandas as pd
import numpy as np
import math

# from basisfuncties import*
# arcpy.env.workspace = r'D:\Projecten\WSRL\sprok_sterrenschans.gdb'
# arcpy.env.overwriteOutput = True

gefmap = r'C:\Users\Vincent\Desktop\test.txt'
max_dZ = 1

deklaag = 0
gef = open(gefmap, "r")
bovenkant = []
onderkant = []
type = []
laag = []


for regel in gef:
    if regel.startswith('#') or regel.isspace() == True:
        pass
    else:

        delen = regel.split(';')

        soort = delen[2]
        soort_global = soort[1]
        bovenkant_ = float(delen[0])
        onderkant_ = float(delen[1])
        dikte_laag = abs(bovenkant_-onderkant_)

        bovenkant.append(bovenkant_)
        onderkant.append(onderkant_)
        type.append(soort_global)
        laag.append(dikte_laag)


        # if soort_global is not "Z":
        #     deklaag += dikte_laag
        #
        # elif soort_global is "Z" and dikte_laag <= 0.9:
        #     # print soort_global, dikte_laag
        #     break



        # print bovenkant_,onderkant_, soort_global, dikte_laag



dict = {'bovenkant': bovenkant, 'onderkant': onderkant, 'type': type,'dikte_laag': laag}
df = pd.DataFrame(dict)
df['type_onderliggend'] = df['type'].shift(-1)



print df
for index, row in df.iterrows():
    s = row['type']
    d = row['dikte_laag']
    if s is not 'Z':
        deklaag += d
    elif s is 'Z' and d <= max_dZ:
        deklaag += d
    elif s is 'Z' and d > max_dZ:
        break

print deklaag


