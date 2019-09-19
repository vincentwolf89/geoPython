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

invoer = 'eindresultaat_laagste_beta'
resultfile = "C:/Users/vince/Desktop/uitvoer_temp.xls"

veld_profiel = 'profielnummer'
veld_beta = 'beta_max'



def beta_schrijver():
    global list_profielid
    velden = ['koppel_id', 'dv_nummer', 'beta_max', 'uniek_id', 'D', 'd70', 'dpip', 'hp', 'L', 'k','mw', 'beta_dsn_piping', 'beta_dsn_opbarsten', 'L_voor', 'L_dijk', 'L_achter', 'dempingsfactor', 'kv_ov',
              'kritiek_vv', 'optredend_vv']

    dct = {}


    with arcpy.da.SearchCursor(invoer, velden) as cur:
        for k, g in groupby(cur, lambda x: x[0]):

            for row in g:



                id, dijkvak, betamax, profielid, D, d70, dpip, hp, L, k, mw, L_voor, L_dijk, L_achter, dempingsfactor, kv_ov, kv, ov = row[0], row[1], row[2], row[3], row[4],row[5], row[6], \
                                                                                                                                       row[7], row[8], row[9], row[10], row[13], row[14], row[15], row[16], row[17], row[18], row[19]
                key = id
                if id in dct:
                    max_beta = dct[id][2]
                    if betamax < max_beta:
                        dct[id] = (id, dijkvak, betamax, profielid, D, d70, dpip, hp, L, k, mw, L_voor, L_dijk, L_achter, dempingsfactor, kv_ov, kv, ov)
                else:
                    dct[id] = (id, dijkvak, betamax, profielid, D, d70, dpip, hp, L, k, mw, L_voor, L_dijk, L_achter, dempingsfactor, kv_ov, kv, ov)



    # definieer lege lijsten
    list_id = []
    # list_traject = []
    list_dv = []
    list_betamax = []
    list_profielid = []
    list_D = []
    list_d70 = []
    list_dpip = []
    list_hp = []
    list_L = []
    list_k =[]
    list_mw = []

    list_kv = []
    list_ov = []

    list_kv_ov = []

    list_L_voor = []
    list_L_dijk = []
    list_L_achter =[]
    list_dempingsfactor =[]

    # vul de lege lijsten
    for id, val in dct.items():
        list_id.append(val[0])
        # list_traject.append(val[1])
        list_dv.append(val[1])
        list_betamax.append(val[2])
        list_profielid.append(val[3])
        list_D.append(val[4])
        list_d70.append(val[5])
        list_dpip.append(val[6])
        list_hp.append(val[7])
        list_L.append(val[8])
        list_k.append(val[9])
        list_mw.append(val[10])
        list_L_voor.append(val[11])
        list_L_dijk.append(val[12])
        list_L_achter.append(val[13])
        list_dempingsfactor.append(val[14])

        list_kv_ov.append(val[15])

        list_kv.append(val[16])
        list_ov.append(val[17])






        # define styles
    style = xlwt.easyxf('font: bold 1')  # define style
    wb = xlwt.Workbook()  # open new workbook
    ws = wb.add_sheet("overzicht")  # add new sheet

    # write headers
    row = 0
    ws.write(row, 0, "koppel_id", style=style)
    ws.write(row, 1, "dijkvak", style=style)
    ws.write(row, 2, "profielnummer", style=style)
    ws.write(row, 3, "maximale_beta", style=style)
    ws.write(row, 4, "D [m]", style=style)
    ws.write(row, 5, "d70 [m]", style=style)
    ws.write(row, 6, "d_cover [m]", style=style)
    ws.write(row, 7, "h_exit [m NAP]", style=style)
    ws.write(row, 8, "L_totaal [m]", style=style)
    ws.write(row, 9, "k [m/s]", style=style)
    ws.write(row, 10, "maatgevende_waterstand [m NAP]", style=style)
    ws.write(row, 11, "L_voor [m]", style=style)
    ws.write(row, 12, "L_dijk [m]", style=style)
    ws.write(row, 13, "L_achter [m]", style=style)
    ws.write(row, 14, "dempingsfactor", style=style)
    ws.write(row, 15, "kritiekvv-optredendvv", style=style)
    ws.write(row, 16, "kritiekvv", style=style)
    ws.write(row, 17, "optredendvv", style=style)





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
    for i in list_betamax:
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
    row = 1
    for i in list_L_voor:
        ws.write(row, 11, i)
        row += 1
    row = 1
    for i in list_L_dijk:
        ws.write(row, 12, i)
        row += 1
    row = 1
    for i in list_L_achter:
        ws.write(row, 13, i)
        row += 1
    row = 1
    for i in list_dempingsfactor:
        ws.write(row, 14, i)
        row += 1
    row = 1
    for i in list_kv_ov:
        ws.write(row, 15, i)
        row += 1
    row = 1
    for i in list_kv:
        ws.write(row, 16, i)
        row += 1
    row = 1
    for i in list_ov:
        ws.write(row, 17, i)
        row += 1
    # save
    wb.save(resultfile)



def plot_maatgevende_profielen_stph():
    arcpy.CopyFeatures_management(invoer, "C:/Users/vince/Desktop/GIS/stph_eindresultaat.gdb/mg_stph")

    veld = ["uniek_id"]
    with arcpy.da.UpdateCursor("C:/Users/vince/Desktop/GIS/stph_eindresultaat.gdb/mg_stph", veld) as cursor:
        for row in cursor:
            if row[0] not in list_profielid:
                cursor.deleteRow()
            else:
                continue

beta_schrijver()
# plot_maatgevende_profielen_stph()