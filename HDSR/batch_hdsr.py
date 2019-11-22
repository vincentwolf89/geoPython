import arcpy
import math
from arcpy.sa import *
import xlwt
import pandas as pd
from itertools import groupby
# uitzetten melding pandas
pd.set_option('mode.chained_assignment', None)
from basisfuncties import*

arcpy.env.workspace = r'D:\Projecten\HDSR\data\oplevering_v1.gdb'
arcpy.env.overwriteOutput = True


profiel_interval = 25
profiel_lengte = 30
invoerpunten = 'punten_profielen'
stapgrootte_punten = 0.5
profiel_lengte_land = 20
profiel_lengte_rivier = 10
afronding = 1
min_afstand = -5
max_afstand = 5
min_achterland = 5
max_achterland = 20
raster = r'D:\Projecten\HDSR\data\ahn_hdsr.gdb\AHN3grondfilter'
code_hdsr = 'Naam'
toetspeil = 'TP2024'
trajecten = 'test'
# specifieke invoer bepaling bit/but
verschil_maxkruin = 0.2
excelmap = 'C:/Users/Vincent/Desktop/xlsx_uitvoer/'

with arcpy.da.SearchCursor(trajecten,['SHAPE@',code_hdsr]) as cursor:
    for row in cursor:
        # lokale variabelen per dijktraject
        code = code_hdsr
        id = row[1]
        trajectlijn = 'deeltraject_'+str(row[1])
        profielen = 'profielen_'+str(row[1])
        uitvoerpunten = 'punten_profielen_z_'+str(row[1])
        uitvoer_maxpunten = 'max_kruinhoogte_'+str(row[1])
        uitvoer_binnenkruin = 'binnenkruin_'+str(row[1])
        uitvoer_buitenkruin = 'buitenkruin_'+str(row[1])
        uitvoer_binnenteen = 'binnenteen_' + str(row[1])
        resultfile = excelmap+str(row[1])+'.xls'
        excel = excelmap+str(row[1])+'.xlsx'
        where = '"' + code_hdsr + '" = ' + "'" + str(id) + "'"

        # selecteer betreffend traject
        arcpy.Select_analysis(trajecten, trajectlijn, where)

        # doorlopen stappen
        generate_profiles(profiel_interval, profiel_lengte_land, profiel_lengte_rivier, trajectlijn, code_hdsr,toetspeil, profielen)
        copy_trajectory_lr(trajectlijn, code_hdsr)
        set_measurements_trajectory(profielen, trajectlijn, code_hdsr, stapgrootte_punten,toetspeil)
        extract_z_arcpy(invoerpunten, uitvoerpunten, raster)
        add_xy(uitvoerpunten, code_hdsr)
        # to_excel(uitvoerpunten, resultfile,sorteervelden='profielnummer A; afstand A')
        excel_writer(uitvoerpunten, code, excel, id)
        kruinhoogte_groepen(uitvoerpunten, stapgrootte_punten, afronding, code_hdsr)
        max_kruinhoogte_test(uitvoerpunten, profielen, code_hdsr,uitvoer_maxpunten,min_afstand,max_afstand,toetspeil)
        kruinbepalen(uitvoerpunten,code_hdsr,uitvoer_binnenkruin,uitvoer_buitenkruin,verschil_maxkruin,min_afstand,max_afstand)
        binnenteenbepalen(uitvoerpunten, code_hdsr, min_achterland, max_achterland, uitvoer_binnenteen, min_afstand,max_afstand,uitvoer_binnenkruin)
        koppeling_hbn_hdsr(profielen,toetspeil)
