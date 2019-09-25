import arcpy
import numpy as np
from arcpy.sa import *
from itertools import groupby
import math
import matplotlib.pyplot as plt
from os import path
import sys
import pandas as pd

arcpy.env.overwriteOutput = True

arcpy.env.workspace = 'C:/Users/vince/Desktop/GIS/stph_sept_2019.gdb'

# voeg veld voor type run toe en geef naam run
runs = ['basis_2m','basis_10m','basis_20m','langs_2m','langs_10m','langs_20m']
veldnaam = 'type_run'
for run in runs:
    bestaande_velden = arcpy.ListFields(run)
    for veld in bestaande_velden:
        if veld.name == veldnaam:
            arcpy.DeleteField_management(run, veldnaam)
        else:
            pass

arcpy.AddField_management('basis_2m', veldnaam, "TEXT", field_length=50)
arcpy.AddField_management('basis_10m', veldnaam, "TEXT", field_length=50)
arcpy.AddField_management('basis_20m', veldnaam, "TEXT", field_length=50)
arcpy.AddField_management('langs_2m', veldnaam, "TEXT", field_length=50)
arcpy.AddField_management('langs_10m', veldnaam, "TEXT", field_length=50)
arcpy.AddField_management('langs_20m', veldnaam, "TEXT", field_length=50)


arcpy.CalculateField_management('basis_2m', "type_run", "'"+"basis_2m"+"'", "PYTHON")
arcpy.CalculateField_management('basis_10m', "type_run", "'"+"basis_10m"+"'", "PYTHON")
arcpy.CalculateField_management('basis_20m', "type_run", "'"+"basis_20m"+"'", "PYTHON")
arcpy.CalculateField_management('langs_2m', "type_run", "'"+"langs_2m"+"'", "PYTHON")
arcpy.CalculateField_management('langs_10m', "type_run", "'"+"basis_10m"+"'", "PYTHON")
arcpy.CalculateField_management('langs_20m', "type_run", "'"+"langs_20m"+"'", "PYTHON")

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
df_final = reduce(lambda left,right: pd.merge(left,right,on='uniek_id',how='outer'), dfs)



sorted = df_final.sort_values(by=['uniek_id'])
sorted.set_index('uniek_id',inplace=True)



# get the column name of min values in every row
minValueIndexObj = sorted.idxmin(axis=1)
minValuesObj = sorted.min(axis=1)




for index, row in sorted.iterrows():
    ix = row.idxmin()
    val = row.min()
    if ix == "beta_max_b2m":
        minimaal_basis2m.append(index)
    else:
        continue

for index, row in sorted.iterrows():
    ix = row.idxmin()
    val = row.min()
    if ix == "beta_max_b10m":
        minimaal_basis10m.append(index)
    else:
        continue

for index, row in sorted.iterrows():
    ix = row.idxmin()
    val = row.min()
    if ix == "beta_max_b20m":
        minimaal_basis20m.append(index)
    else:
        continue

for index, row in sorted.iterrows():
    ix = row.idxmin()
    val = row.min()
    if ix == "beta_max_la2m":
        minimaal_langs2m.append(index)
    else:
        continue
for index, row in sorted.iterrows():
    ix = row.idxmin()
    val = row.min()
    if ix == "beta_max_la10m":
        minimaal_langs10m.append(index)
    else:
        continue
for index, row in sorted.iterrows():
    ix = row.idxmin()
    val = row.min()
    if ix == "beta_max_la20m":
        minimaal_langs20m.append(index)
    else:
        continue



# kopieer de feature classes om overblijvende profielen te tonen
arcpy.CopyFeatures_management("basis_2m", "basis_2m_edit")
arcpy.CopyFeatures_management("basis_10m", "basis_10m_edit")
arcpy.CopyFeatures_management("basis_20m", "basis_20m_edit")
arcpy.CopyFeatures_management("langs_2m", "langs_2m_edit")
arcpy.CopyFeatures_management("langs_10m", "langs_10m_edit")
arcpy.CopyFeatures_management("langs_20m", "langs_20m_edit")



# # check voor dubbelgangers
# for item in minimaal_basis2m:
#     if item not in minimaal_basis10m or item not in


# verwijder de niet-minimale beta's uit feature classes (update cursor)
velden = ["uniek_id"]
with arcpy.da.UpdateCursor("basis_2m_edit", velden) as cursor1:
    for row in cursor1:
        if row[0] not in minimaal_basis2m:
            cursor1.deleteRow()
        else:
            continue
with arcpy.da.UpdateCursor("basis_10m_edit", velden) as cursor2:
    for row in cursor2:
        if row[0] not in minimaal_basis10m:
            cursor2.deleteRow()
        else:
            continue
with arcpy.da.UpdateCursor("basis_20m_edit", velden) as cursor3:
    for row in cursor3:
        if row[0] not in minimaal_basis20m:
            cursor3.deleteRow()
        else:
            continue
with arcpy.da.UpdateCursor("langs_2m_edit", velden) as cursor4:
    for row in cursor4:
        if row[0] not in minimaal_langs2m:
            cursor4.deleteRow()
        else:
            continue
with arcpy.da.UpdateCursor("langs_10m_edit", velden) as cursor5:
    for row in cursor5:
        if row[0] not in minimaal_langs10m:
            cursor5.deleteRow()
        else:
            continue
with arcpy.da.UpdateCursor("langs_20m_edit", velden) as cursor6:
    for row in cursor6:
        if row[0] not in minimaal_langs20m:
            cursor6.deleteRow()
        else:
            continue
# merge alle 6 feature classes en dissolve


feature1 = "basis_2m_edit"
feature2 = "basis_10m_edit"
feature3 = "basis_20m_edit"
feature4 = "langs_2m_edit"
feature5 = "langs_10m_edit"
feature6 = "langs_20m_edit"



arcpy.Merge_management([feature1,feature2,feature3,feature4,feature5,feature6], "merge")
arcpy.DeleteIdentical_management("merge", ["uniek_id"])
# arcpy.Dissolve_management("merge", "dissolve", ['uniek_id'])
# na dissolve, join met merge en delete identical in arcmap

