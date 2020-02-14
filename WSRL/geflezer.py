import arcpy
import pandas as pd
import numpy as np
import math
import os, sys

# from basisfuncties import*
# arcpy.env.workspace = r'D:\Projecten\WSRL\sprok_sterrenschans.gdb'
# arcpy.env.overwriteOutput = True

gefmap = r'C:\Users\Vincent\Desktop\02-Gef\MB'
max_dZ = 1
soorten_grof = ['Z','G']



# gef = open(gefmap, "r")
# bovenkant = []
# onderkant = []
# typ = []
# laag = []
# bovenkant_grof = []

def gef_txt(gefmap):
    for gef in os.listdir(gefmap):
        ingef = os.path.join(gefmap, gef)
        if not os.path.isfile(ingef): continue
        nieuwenaam = ingef.replace('.GEF', '.txt')
        output = os.rename(ingef, nieuwenaam)

def bovenkant_deklaag(gefmap):


    for file in os.listdir(gefmap):
        # print file
        ingef = os.path.join(gefmap, file)
        gef = open(ingef, "r")
        deklaag = 0
        grove_laag = 0

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




        dict = {'bovenkant': bovenkant, 'onderkant': onderkant, 'type': typ,'dikte_laag': laag}
        df = pd.DataFrame(dict)
        df['type_onderliggend'] = df['type'].shift(-1)
        df['dikte_onderliggend'] = df['dikte_laag'].shift(-1)


        # print df


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




        # print grove_laag
        # print bovenkant_grof[0]


        for index, row in df.iterrows():
            d = row['dikte_laag']

            if len(bovenkant_grof) > 0:
                if index < bovenkant_grof[0]:
                    deklaag += d
            elif len(bovenkant_grof) is 0 and t not in soorten_grof:
                deklaag += d
                print "geen grove laag", file

        print "deklaag is", deklaag, file





bovenkant_deklaag(gefmap)
