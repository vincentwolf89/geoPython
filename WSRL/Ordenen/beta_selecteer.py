import arcpy
import numpy as np
from arcpy.sa import *
from itertools import groupby
import math
import matplotlib.pyplot as plt
from os import path
import sys
import pandas as pd
from Basisfuncties import*

arcpy.env.overwriteOutput = True

arcpy.env.workspace = 'C:/Users/vince/Desktop/GIS/stph_juli_2019.gdb'





# importeer feature classes
basis_2m = arcpy.da.FeatureClassToNumPyArray('basis_2m', ('uniek_id','beta_max'))
basis_10m = arcpy.da.FeatureClassToNumPyArray('basis_10m', ('uniek_id','beta_max'))
basis_20m = arcpy.da.FeatureClassToNumPyArray('basis_20m', ('uniek_id','beta_max'))
langs_2m = arcpy.da.FeatureClassToNumPyArray('langs_2m', ('uniek_id','beta_max'))
langs_10m = arcpy.da.FeatureClassToNumPyArray('langs_10m', ('uniek_id','beta_max'))
langs_20m = arcpy.da.FeatureClassToNumPyArray('langs_20m', ('uniek_id','beta_max'))


# maak pandas
df_basis_2m = pd.DataFrame(basis_2m)
df_basis_10m = pd.DataFrame(basis_10m)
df_basis_20m = pd.DataFrame(basis_20m)
df_langs_2m = pd.DataFrame(langs_2m)
df_langs_10m = pd.DataFrame(langs_10m)
df_langs_20m = pd.DataFrame(langs_20m)

# lege lijsten
minimaal_basis2m = []
minimaal_basis10m = []
minimaal_basis20m = []
minimaal_langs2m = []
minimaal_langs10m = []
minimaal_langs20m = []


# unieke velden voor beta's
df_basis_2m.rename(columns={'uniek_id': 'uniek_id', 'beta_max': 'beta_max_b2m'}, inplace=True)
df_basis_10m.rename(columns={'uniek_id': 'uniek_id', 'beta_max': 'beta_max_b10m'}, inplace=True)
df_basis_20m.rename(columns={'uniek_id': 'uniek_id', 'beta_max': 'beta_max_b20m'}, inplace=True)
df_langs_2m.rename(columns={'uniek_id': 'uniek_id', 'beta_max': 'beta_max_la2m'}, inplace=True)
df_langs_10m.rename(columns={'uniek_id': 'uniek_id', 'beta_max': 'beta_max_la10m'}, inplace=True)
df_langs_20m.rename(columns={'uniek_id': 'uniek_id', 'beta_max': 'beta_max_la20m'}, inplace=True)

dfs = [df_basis_2m, df_basis_10m, df_basis_20m, df_langs_2m,df_langs_10m,df_langs_20m]
df_final = reduce(lambda left,right: pd.merge(left,right,on='uniek_id'), dfs)

sorted = df_final.sort_values(by=['uniek_id'])
sorted.set_index('uniek_id',inplace=True)
#


with arcpy.da.UpdateCursor("mg_stph", ['uniek_id','beta_max', 'scenario']) as cursor:
    for row in cursor:
        beta = round(row[1],2)
        for index, rij in sorted.iterrows():
            ix = rij.idxmin()
            val = round(rij.min(),2)

            if beta == val:
                print "found", ix, row[0]
                row[2] = str(ix)[9:]
                cursor.updateRow(row)
                break

naam_run = 'mg_stph'
controle_stph(naam_run)