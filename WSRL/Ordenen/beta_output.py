import arcpy
import numpy
from arcpy.sa import *
from itertools import groupby
import math
from os import path
import sys
import pandas as pd
import os
import xlrd
from openpyxl import load_workbook
import os
import xlwt
#import win32com.client as win32

sys.setrecursionlimit(1000000000)


arcpy.env.overwriteOutput = True

# Set environment settings
arcpy.env.workspace = 'C:/Users/vince/Desktop/GIS/stph_eindresultaat.gdb'

invoer = 'eindresultaat'
resultfile = "C:/Users/vince/Desktop/beta_min_eindresultaat.xls"

veld_profiel = 'profielnummer'
veld_beta = 'beta_min'

#fields = ['koppel_id','beta_min', 'D', 'd70', 'dpip', 'hp', 'L', 'k', 'gamma_sat']
#fields = ['koppel_id', 'beta_min', 'naam_dwp', 'dpip', 'D']
velden = ['koppel_id', 'dv_nummer', 'beta_min', 'uniek_id', 'D', 'd70', 'dpip', 'hp', 'L', 'k','mw', 'beta_dsn_piping', 'beta_dsn_opbarsten']

dct = {}


with arcpy.da.SearchCursor(invoer, velden) as cur:
    for k, g in groupby(cur, lambda x: x[0]):

        for row in g:



            id, dijkvak, betamin, profielid, D, d70, dpip, hp, L, k, mw = row[0], row[1], row[2], row[3], row[4],row[5], row[6], row[7], row[8], row[9], row[10]
            key = id
            if id in dct:
                min_beta = dct[id][2]
                if betamin < min_beta:
                    dct[id] = (id, dijkvak, betamin, profielid, D, d70, dpip, hp, L, k, mw)
            else:
                dct[id] = (id, dijkvak, betamin, profielid, D, d70, dpip, hp, L, k, mw)



# definieer lege lijsten
list_id = []
# list_traject = []
list_dv = []
list_betamin = []
list_profielid = []
list_D = []
list_d70 = []
list_dpip = []
list_hp = []
list_L = []
list_k =[]
list_mw = []

# vul de lege lijsten
for id, val in dct.items():
    list_id.append(val[0])
    # list_traject.append(val[1])
    list_dv.append(val[1])
    list_betamin.append(val[2])
    list_profielid.append(val[3])
    list_D.append(val[4])
    list_d70.append(val[5])
    list_dpip.append(val[6])
    list_hp.append(val[7])
    list_L.append(val[8])
    list_k.append(val[9])
    list_mw.append(val[10])


    # define styles
style = xlwt.easyxf('font: bold 1')  # define style
wb = xlwt.Workbook()  # open new workbook
ws = wb.add_sheet("overzicht")  # add new sheet

# write headers
row = 0
ws.write(row, 0, "koppel_id", style=style)
ws.write(row, 1, "dijkvak", style=style)
ws.write(row, 2, "profielnummer", style=style)
ws.write(row, 3, "minimale_beta", style=style)
ws.write(row, 4, "D [m]", style=style)
ws.write(row, 5, "d70 [m]", style=style)
ws.write(row, 6, "d_cover [m]", style=style)
ws.write(row, 7, "h_exit [m NAP]", style=style)
ws.write(row, 8, "L_totaal [m]", style=style)
ws.write(row, 9, "k [m/s]", style=style)
ws.write(row, 10, "maatgevende_waterstand [m NAP]", style=style)




# write colums
row = 1
for i in list_id:
    ws.write(row, 0, i)
    row += 1

row = 1
for i in list_dv:
    ws.write(row, 1, i)
    row += 1

row = 1
for i in list_profielid:
    ws.write(row, 2, i)
    row += 1

row = 1
for i in list_betamin:
    ws.write(row, 3, i)
    row += 1

row = 1
for i in list_D:
    ws.write(row, 4, i)
    row += 1
row = 1
for i in list_d70:
    ws.write(row, 5, i)
    row += 1
row = 1
for i in list_dpip:
    ws.write(row, 6, i)
    row += 1
row = 1
for i in list_hp:
    ws.write(row, 7, i)
    row += 1
row = 1
for i in list_L:
    ws.write(row, 8, i)
    row += 1
row = 1
for i in list_k:
    ws.write(row, 9, i)
    row += 1
row = 1
for i in list_mw:
    ws.write(row, 10, i)
    row += 1
# save
wb.save(resultfile)



