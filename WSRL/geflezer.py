import arcpy
import pandas as pd
import numpy as np
import math

# from basisfuncties import*
# arcpy.env.workspace = r'D:\Projecten\WSRL\sprok_sterrenschans.gdb'
# arcpy.env.overwriteOutput = True

gefmap = r'C:\Users\Vincent\Desktop\test.txt'
max_dZ = 1
soorten_grof = ['Z','G']

deklaag = 0
grove_laag = 0

gef = open(gefmap, "r")
bovenkant = []
onderkant = []
typ = []
laag = []
bovenkant_grof = []


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
        typ.append(soort_global)
        laag.append(dikte_laag)


        # if soort_global is not "Z":
        #     deklaag += dikte_laag
        #
        # elif soort_global is "Z" and dikte_laag <= 0.9:
        #     # print soort_global, dikte_laag
        #     break



        # print bovenkant_,onderkant_, soort_global, dikte_laag



dict = {'bovenkant': bovenkant, 'onderkant': onderkant, 'type': typ,'dikte_laag': laag}
df = pd.DataFrame(dict)
df['type_onderliggend'] = df['type'].shift(-1)
df['dikte_onderliggend'] = df['dikte_laag'].shift(-1)



print df
for index, row in df.iterrows():
    t = row['type']
    d = row['dikte_laag']
    to = row['type_onderliggend']
    do = row['dikte_onderliggend']
    dikte_som = d+do

    # dikte grove laag bepalen
    if t in soorten_grof:
        if to in soorten_grof or pd.isna(to)==True and d <= max_dZ:
            bovenkant_grof.append(index)
            grove_laag += d
        elif d > max_dZ:
            bovenkant_grof.append(index)




print grove_laag
print bovenkant_grof[0]

for index, row in df.iterrows():
    d = row['dikte_laag']
    if index < bovenkant_grof[0]:
        deklaag += d

print deklaag


