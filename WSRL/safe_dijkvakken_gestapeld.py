


# importeren van benodigde modules
import arcpy
import math
from arcpy.sa import *
import xlwt
import pandas as pd
from itertools import groupby

# uitzetten melding pandas
pd.set_option('mode.chained_assignment', None)

# importeer alle basisfuncties
from basisfuncties import*

# definieer de werkomgeving
arcpy.env.workspace = r'D:\Projecten\WSRL\safe_temp.gdb'
# sta arcpy toe oude data te overschrijven
arcpy.env.overwriteOutput = True

# invoer voor hoogtetoets
profiel_interval = 25
stapgrootte_punten = 1
profiel_lengte_land = 200
profiel_lengte_rivier = 100 # 10 default

# min_afstand = -5 # minimale waarde voor bandbreedte kruinpunten
# max_afstand = 5 # maximale waarde voor bandbreedte kruinpunten
# min_achterland = 5 # minimale waarde voor afstand t.b.v. bepaling hoogte achterland
# max_achterland = 20 # maximale waarde voor afstand t.b.v. bepaling hoogte achterland

excelmap = 'D:/Projecten/WSRL/safe/uitvoer_priovakken/' # gewenste map voor .xlsx-uitvoer
raster = r'C:\Users\Vincent\Desktop\ahn3clip_safe' # hoogtegrid
bodemdalingskaart = r'D:\GIS\losse rasters\bodemdalingskaart_app_data_geotiff_Bodemdalingskaart_10de_percentiel_mm_per_jaar_verticale_richting_v2018002.tif'
afstand_zichtjaar = 10 # het aantal jaren waarmee de bodemdaling (per jaar) moet worden vermenigvuldigd.
code_wsrl = 'prio_nummer' # naamgeving van traject
# toetspeil = 'th2024' # naam van kolom met toetspeil/toetshoogte
trajecten = 'priovakken' # door te rekenen trajecten

naam_totaalprofielen = 'prioprofielen_safe_jan2020'
toetspeil = 999

totaal_profielen =[]

# cursor om de batch door te rekenen
with arcpy.da.SearchCursor(trajecten,['SHAPE@',code_wsrl]) as cursor:
    for row in cursor:
        # lokale variabelen per dijktraject
        code = code_wsrl
        id = row[1]
        trajectlijn = 'deeltraject_'+str(row[1])
        profielen = 'profielen_'+str(row[1])
        uitvoerpunten = 'punten_profielen_z_'+str(row[1])
        uitvoer_maxpunten = 'max_kruinhoogte_'+str(row[1])
        uitvoer_binnenkruin = 'binnenkruin_'+str(row[1])
        uitvoer_buitenkruin = 'buitenkruin_'+str(row[1])
        uitvoer_binnenteen = 'binnenteen_' + str(row[1])
        resultfile = excelmap+str(row[1])+'.xls'
        excel = excelmap+'priovak_'+str(row[1])+'.xlsx'
        where = '"' + code_wsrl + '" = ' + "'" + str(id) + "'"

        invoerpunten = 'punten_profielen'

        # selecteer betreffend traject
        arcpy.Select_analysis(trajecten, trajectlijn, where)

        # doorlopen stappen
        generate_profiles(profiel_interval, profiel_lengte_land, profiel_lengte_rivier, trajectlijn, code_wsrl,toetspeil, profielen)
        copy_trajectory_lr(trajectlijn, code_wsrl)
        set_measurements_trajectory(profielen, trajectlijn, code_wsrl, stapgrootte_punten,toetspeil)
        extract_z_arcpy(invoerpunten, uitvoerpunten, raster)
        add_xy(uitvoerpunten, code_wsrl)
        excel_writer(uitvoerpunten, code, excel, id,trajecten,toetspeil)
        # kruinhoogte_groepen(uitvoerpunten, stapgrootte_punten, afronding, code_wsrl)
        # max_kruinhoogte(uitvoerpunten, profielen, code_wsrl,uitvoer_maxpunten,min_afstand,max_afstand,toetspeil)
        # kruinbepalen(uitvoerpunten,code_wsrl,uitvoer_binnenkruin,uitvoer_buitenkruin,verschil_maxkruin,min_afstand,max_afstand)
        # binnenteenbepalen(uitvoerpunten, code_wsrl, min_achterland, max_achterland, uitvoer_binnenteen, min_afstand,max_afstand,uitvoer_binnenkruin)
        # koppeling_hbn_hdsr(profielen,toetspeil)
        # bereken_restlevensduur(profielen,bodemdalingskaart,afstand_zichtjaar,toetspeil)

        # voeg profielen van betreffend traject toe aan lijst met alle profielen
        totaal_profielen.append(profielen)
        # print profielen

# voeg alle profielen samen tot een lijst
arcpy.Merge_management(totaal_profielen, naam_totaalprofielen)