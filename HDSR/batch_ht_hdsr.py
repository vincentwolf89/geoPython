## hoogtetoets HDSR 2019
# hierin wordt de invoer gedefinieerd beschreven die gebruikt maakt van de basisfuncties in 'RWK_ht_2019.py'

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
from RWK_ht_2019 import*

# definieer de werkomgeving
arcpy.env.workspace = r'D:\Projecten\HDSR\data\test_oplevering.gdb'
# sta arcpy toe oude data te overschrijven
arcpy.env.overwriteOutput = True

# invoer voor hoogtetoets
profiel_interval = 25 # 25 default
stapgrootte_punten = 0.5 # afstand tussen de meetpunten
profiel_lengte_land = 20 # 20 default
profiel_lengte_rivier = 10 # 10 default
min_afstand = -5 # minimale waarde voor bandbreedte kruinpunten
max_afstand = 5 # maximale waarde voor bandbreedte kruinpunten
min_achterland = 5 # minimale waarde voor afstand t.b.v. bepaling hoogte achterland
max_achterland = 20 # maximale waarde voor afstand t.b.v. bepaling hoogte achterland

excelmap = 'D:/Projecten/HDSR/xlsx_uitvoer/' # gewenste map voor .xlsx-uitvoer
raster = r'D:\Projecten\HDSR\data\ahn_hdsr.gdb\AHN3grondfilter' # hoogtegrid
bodemdalingskaart = r'D:\GIS\losse rasters\bodemdalingskaart_app_data_geotiff_Bodemdalingskaart_10de_percentiel_mm_per_jaar_verticale_richting_v2018002.tif'
afstand_zichtjaar = 10 # het aantal jaren waarmee de bodemdaling (per jaar) moet worden vermenigvuldigd.
code_hdsr = 'Naam' # naamgeving van traject
toetspeil = 'th2024' # naam van kolom met toetspeil/toetshoogte
trajecten = 'test_111' # door te rekenen trajecten

# bij standaard gebruik niet veranderen
verschil_maxkruin = 0.2 # specifieke invoer bepaling binnenteen/buitenteen
invoerpunten = 'punten_profielen'
afronding = 1
totaal_profielen = []

# cursor om de batch door te rekenen
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
        excel_writer(uitvoerpunten, code, excel, id,trajecten,toetspeil)
        kruinhoogte_groepen(uitvoerpunten, stapgrootte_punten, afronding, code_hdsr)
        max_kruinhoogte(uitvoerpunten, profielen, code_hdsr,uitvoer_maxpunten,min_afstand,max_afstand,toetspeil)
        kruinbepalen(uitvoerpunten,code_hdsr,uitvoer_binnenkruin,uitvoer_buitenkruin,verschil_maxkruin,min_afstand,max_afstand)
        binnenteenbepalen(uitvoerpunten, code_hdsr, min_achterland, max_achterland, uitvoer_binnenteen, min_afstand,max_afstand,uitvoer_binnenkruin)
        koppeling_hbn_hdsr(profielen,toetspeil)
        bereken_restlevensduur(profielen,bodemdalingskaart,afstand_zichtjaar,toetspeil)

        # voeg profielen van betreffend traject toe aan lijst met alle profielen
        totaal_profielen.append(profielen)
        # print profielen

# voeg alle profielen samen tot een lijst
arcpy.Merge_management(totaal_profielen, 'profielen_RWK_areaal_2024')