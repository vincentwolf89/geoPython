import arcpy
import numpy as np
from arcpy.sa import *
from itertools import groupby
import math
import matplotlib.pyplot as plt
from os import path
import sys
import pandas as pd
from scipy.signal import savgol_filter
import matplotlib.ticker as ticker

sys.setrecursionlimit(1000000000)


arcpy.env.overwriteOutput = True


# Set environment settings
arcpy.env.workspace = 'C:/Users/vince/Desktop/GIS/profielscript_final.gdb'

profielen_invoer = "profielen_10m"
dv_indeling = "dv_indeling"
bovenlijn = "bovenlijn"


def generate_points():
    # Set local variables
    in_features = profielen_invoer
    out_fc_1 = 'punten_10m'


    # Execute GeneratePointsAlongLines by distance
    arcpy.GeneratePointsAlongLines_management(in_features, out_fc_1, 'DISTANCE',
                                            Distance= 2)
    print "punten om de 2 meter op ieder profiel gemaakt"


def knip_profielen():
  #intersect with dv indeling --> point
  inFeatures = [profielen_invoer, dv_indeling]
  intersectOutput = "nul_punten_profielen"
  clusterTolerance = 0.5
  arcpy.Intersect_analysis(inFeatures, intersectOutput, "", clusterTolerance, "point")

  #split profielen voor koppeling
  inFeatures = profielen_invoer
  pointFeatures = "nul_punten_profielen"
  outFeatureclass = "profielknips"
  searchRadius = "1"
  arcpy.SplitLineAtPoint_management(inFeatures, pointFeatures, outFeatureclass, searchRadius)

  #koppel aan profielknips
  targetFeatures = "profielknips"
  joinFeatures = bovenlijn
  outfc = "profielen_bovenlijn"

  velden = ['profielnummer','rivierzijde']  # defineeer de te behouden velden
  fieldmappings = arcpy.FieldMappings()


  fieldmappings.addTable(targetFeatures)
  fieldmappings.addTable(joinFeatures)
  keepers = velden

  for field in fieldmappings.fields:
    if field.name not in keepers:
      fieldmappings.removeFieldMap(fieldmappings.findFieldMapIndex(field.name))
  # voer de spatial join uit
  arcpy.SpatialJoin_analysis(targetFeatures, joinFeatures, outfc, "#", "#", fieldmappings, match_option="INTERSECT",
                             search_radius=1)


def values_points():
    # Set local variables
    inPointFeatures = "punten_10m"
    inRaster = "C:/Users/vince/Desktop/GIS/losse rasters/ahn3clip/ahn3clip_safe"
    outPointFeatures = "profielen_10m_punten_z"

    # Check out the ArcGIS Spatial Analyst extension license
    arcpy.CheckOutExtension("Spatial")

    # Execute ExtractValuesToPoints
    ExtractValuesToPoints(inPointFeatures, inRaster, outPointFeatures,
                          "INTERPOLATE", "VALUE_ONLY")
    print "z-waarde aan punten gekoppeld"


def velden():

    arcpy.env.outputCoordinateSystem = arcpy.Describe("profielen_10m_punten_z").spatialReference
    # Set local variables
    in_features = "profielen_10m_punten_z"
    properties = "POINT_X_Y_Z_M"
    length_unit = ""
    area_unit = ""
    coordinate_system = ""

    # Generate the extent coordinates using Add Geometry Properties tool
    arcpy.AddGeometryAttributes_management(in_features, properties, length_unit,
                                           area_unit,
                                           coordinate_system)


def koppel_centerline():
    targetFeatures = "profielen_10m_punten_z"
    joinFeatures = dv_indeling
    outfc = "profielen_10m_splitpunten_z_join1"


    # pas de veldnamen aan
    input = 'profielen_10m_punten_z'

    hoogte = 'RASTERVALU'
    hoogte_nieuw = 'z_ahn'

    x_oud = 'POINT_X'
    x_nieuw = 'x'

    y_oud = 'POINT_Y'
    y_nieuw = 'y'

    arcpy.AlterField_management(input, hoogte, hoogte_nieuw)
    arcpy.AlterField_management(input, x_oud, x_nieuw)
    arcpy.AlterField_management(input, y_oud, y_nieuw)


    # spatial join punten 2
    velden = ['z_ahn', 'type_lijn', 'x', 'y', 'profielnummer','MEAS']  # defineeer de te behouden velden
    fieldmappings = arcpy.FieldMappings()

    # stel de fieldmapping in
    fieldmappings.addTable(targetFeatures)
    fieldmappings.addTable(joinFeatures)
    keepers = velden

    # verwijder de niet-benodigde velden
    for field in fieldmappings.fields:
        if field.name not in keepers:
            fieldmappings.removeFieldMap(fieldmappings.findFieldMapIndex(field.name))
    # voer de spatial join uit
    arcpy.SpatialJoin_analysis(targetFeatures, joinFeatures, outfc, "#", "#", fieldmappings, match_option="INTERSECT",
                               search_radius=1)
    print "join compleet"

def koppel_bovenlijn():
    targetFeatures = "profielen_10m_splitpunten_z_join1"
    joinFeatures = "profielen_bovenlijn"
    outfc = "profielen_10m_splitpunten_z_join2"


    # spatial join punten 2
    velden = ['z_ahn', 'type_lijn', 'x', 'y', 'profielnummer', 'rivierzijde', 'MEAS']  # defineeer de te behouden velden
    fieldmappings = arcpy.FieldMappings()

    # stel de fieldmapping in
    fieldmappings.addTable(targetFeatures)
    fieldmappings.addTable(joinFeatures)
    keepers = velden

    # verwijder de niet-benodigde velden
    for field in fieldmappings.fields:
        if field.name not in keepers:
            fieldmappings.removeFieldMap(fieldmappings.findFieldMapIndex(field.name))
    # voer de spatial join uit
    arcpy.SpatialJoin_analysis(targetFeatures, joinFeatures, outfc, "#", "#", fieldmappings, match_option="INTERSECT",
                               search_radius=1)
    print "join compleet"


def voeg_velden_toe():
    # Set local variables
    inFeatures = "profielen_10m_splitpunten_z_join2"
    fieldName1 = "deltaX"
    fieldName2 = "deltaY"
    fieldName3 = "afstand"
    #fieldname4 = "omklap"
    fieldPrecision = 2


    # Execute AddField twice for two new fields
    arcpy.AddField_management(inFeatures, fieldName1, "FlOAT", fieldPrecision, field_is_nullable="NULLABLE")
    arcpy.AddField_management(inFeatures, fieldName2, "FlOAT", fieldPrecision, field_is_nullable="NULLABLE")
    arcpy.AddField_management(inFeatures, fieldName3, "FlOAT", fieldPrecision, field_is_nullable="NULLABLE")
    #arcpy.AddField_management(inFeatures, fieldname4, "FlOAT", fieldPrecision, field_is_nullable="NULLABLE")
    print "velden toegevoegd"


def bereken_waardes():
    tbl =  'profielen_10m_splitpunten_z_join2'
    fields = ['x', 'y', 'type_lijn', 'deltaX', 'deltaY', 'profielnummer', 'rivierzijde','afstand']
    listp = []
    listx = []
    listy = []
    with arcpy.da.UpdateCursor(tbl, fields) as cur:
        for k, g in groupby(cur, lambda x: x[5]):

            for row in g:
                if row[2] == 0:
                    p = str(row[5])
                    x_vast = (row[0])
                    y_vast = (row[1])
                    listx.append(x_vast)
                    listy.append(y_vast)
                    listp.append(p)
                    #print row[5]
                else:
                    continue
    #print listp
    dictionary_X = dict(zip(listp, listx))
    dictionary_Y = dict(zip(listp, listy))




    with arcpy.da.UpdateCursor(tbl, fields) as cur3:
        for k, g in groupby(cur3, lambda x: x[5]):

            for row in g:
                nummer = str(row[5])
                x_0 = (dictionary_X[(nummer)])
                y_0 = (dictionary_Y[(nummer)])

                row[3] = row[0] - x_0
                if row[3] < 0:
                    row[3] = row[3] * -1
                else:
                  pass

                row[4] = row[1] - y_0
                if row[4] < 0:
                    row[4] = row[4] * -1
                else:
                    pass

                row[7] = math.sqrt((row[3]) ** 2 + (row[4]) ** 2)

                if row[7] < 0 and row[6] == 1:
                    row[7] = row[7]*-1
                elif row[7] > 0 and row[6] == None:
                    row[7] = row[7]*-1
                else:
                    pass


                # if row[7] < 0:
                # row[5] = row[5]*-1
                # else:
                # pass
                cur3.updateRow(row)




invoer = profielen_invoer
dijkvakken = 'overgangen_stbi_meas'
mg_profielen = 'mg_prof_oud_meas'

langsconstructies = 'test_constructie_plot'
traject_kis = 'test_kis_plot'

dijktraject = '16-4'
outpath = "C:/Users/vince/Desktop/geometrie_16_4_test.png"


# lijsten
locatie = []
dijkpaal =[]
traject = []
afstand_but = []
afstand_bit = []
afstand_bik = []
afstand_buk = []

list_afstand_bik_buk = []
list_afstand_bit_buk =[]

# data dijkbreedtes
array = arcpy.da.FeatureClassToNumPyArray(invoer, ('afstand','dijkpaal','dijktraject','bit_afstand', 'bik_afstand', 'buk_afstand'))
df = pd.DataFrame(array)
sort = df.sort(['afstand'])

for index, row in sort.iterrows():
    if row['dijktraject'] == dijktraject:
        binnen = afstand_bik_buk = abs(row['buk_afstand']-row['bik_afstand'])
        buiten = afstand_bit_buk = abs(row['buk_afstand']-row['bit_afstand'])
        list_afstand_bik_buk.append(binnen)
        list_afstand_bit_buk.append(buiten)

        locatie.append(row['afstand']) # Hier moet iets aangepast, gaat fout bij plot.
        dijkpaal.append(row['dijkpaal'])
        traject.append(row['dijktraject'])


df_plots_ = pd.DataFrame(
    {'afstand': locatie,
     'dijkpaal': dijkpaal,
     'traject': dijktraject,
     'binnen': list_afstand_bik_buk,
     'buiten': list_afstand_bit_buk})

df_plots = df_plots_.sort(['afstand'])


# opzetten x-as

indexes = df_plots.index.tolist()
t = np.linspace(min(indexes), max(indexes), 70)

for n, i in enumerate(t):
    t[n] = round(i,0)

df = pd.DataFrame(df_plots , index=t)
x_as = df['afstand'].tolist()
dp = df['dijkpaal'].tolist()



# data dijkvakken
array_dv = arcpy.da.FeatureClassToNumPyArray(dijkvakken, ('OBJECTID', 'afstand', 'dijktraject'))
df_dv = pd.DataFrame(array_dv)
sort_dv = df_dv.sort(['afstand'])


# data maatgevende profielen
array_mg = arcpy.da.FeatureClassToNumPyArray(mg_profielen, ('OBJECTID', 'afstand', 'dijktraject'))
df_mg = pd.DataFrame(array_mg)
sort_mg = df_mg.sort(['afstand'])

# data constructies
array_ctr = arcpy.da.FeatureClassToNumPyArray(langsconstructies, ('groep', 'afstand', 'hoogte'))
df_ctr = pd.DataFrame(array_ctr)
sort_ctr = df_ctr.sort(['afstand'])

# data kis
array_kis = arcpy.da.FeatureClassToNumPyArray(traject_kis, ('groep', 'afstand', 'hoogte'))
df_kis = pd.DataFrame(array_kis)
sort_kis = df_kis.sort(['afstand'])



plt.style.use('seaborn-whitegrid')
fig = plt.figure(figsize=(100, 10))

# smooth-lines
smooth_binnen = savgol_filter(list_afstand_bik_buk, window_length=21, polyorder=5, deriv=0)
smooth_buiten = savgol_filter(list_afstand_bit_buk, window_length=21, polyorder=5, deriv=0)

ax1 = fig.add_subplot(111)
# ax1.plot(df_plots['afstand'], df_plots['binnen'], linewidth=0.8, color='blue', label = 'afstand binnenkruin-buitenkruin')
ax1.plot(df_plots['afstand'], smooth_buiten, linewidth=0.8, color='red', label = 'afstand binnenteen-buitenkruin_smooth')
ax1.plot(df_plots['afstand'], smooth_binnen, linewidth=1, color='blue', label = 'afstand binnenkruin-buitenkruin_smooth')



# plot dijkvakken
for index, row in sort_dv.iterrows():
    x_afstand = row['afstand']
    traject = row['dijktraject']
    if traject == dijktraject:
        ax1.axvline(x=x_afstand, color='red', linewidth=1.5, linestyle = '--')

# plot maatgevende profielen
for index, row in sort_mg.iterrows():
    x_afstand = row['afstand']
    traject = row['dijktraject']
    if traject == dijktraject:
        # ax1.axvline(x=x_afstand, ymin=0, ymax=60, color='black', linewidth=2.5, linestyle = '-')
        plt.vlines(x=x_afstand, ymin=0, ymax=60, color='black', linewidth=2.5, linestyle = '-')

# plot langsconstructies
grouped_ctr = sort_ctr.groupby('groep')
for name, group_ctr in grouped_ctr:
    ax1.plot(group_ctr['afstand'], group_ctr['hoogte'], linewidth= 5, color = 'red', label='_nolegend_')
    # ax1.plot(group['afstand'], group['hoogte'], 'o', markersize = 3, color='red', label='_nolegend_')
    # ax.plot(xx, yy, 'o', color='tab:red', markersize=3)
    # smooth_buiten, linewidth = 0.8, color = 'red', label = 'afstand binnenteen-buitenkruin_smooth'


# plot traject KIS
grouped_kis = sort_kis.groupby('groep')
for name, group_kis in grouped_kis:
    ax1.plot(group_kis['afstand'], group_kis['hoogte'], linewidth= 5, color = 'orange', label='_nolegend_')
    # ax1.plot(group['afstand'], group['hoogte'], 'o', markersize = 3, color='red', label='_nolegend_')
    # ax.plot(xx, yy, 'o', color='tab:red', markersize=3)
    # smooth_buiten, linewidth = 0.8, color = 'red', label = 'afstand binnenteen-buitenkruin_smooth'

leg = ax1.legend(frameon=1)
frame = leg.get_frame()
frame.set_facecolor('white')
ax1.set_xlabel(r"afstand [km vanaf links gemeten]")

# ax1.xaxis.set_major_locator(ticker.MultipleLocator(2))
# ax1.xaxis.set_minor_locator(ticker.MultipleLocator(0.5))
# ax1.set_xlim(0, 20)


min = round(min(df_plots['afstand'].tolist()))-500
max = round(max(df_plots['afstand'].tolist()))+500



# ax1.xaxis.set_ticks(np.arange(min, max, 500)) # standaard 0.5
ax1.set_xticks(x_as)
ax1Xs = ax1.get_xticks()

ax1.set_xticklabels([round(i/1000,1) for i in ax1Xs])
ax1.set_xlim(min, max)

# setup tweede x-as
ax2 = ax1.twiny()
ax2.set_xlim(min, max)
ax2Xs = []



ax2.set_xticks(x_as)
ax2.set_xticklabels(dp)


ax2.xaxis.set_ticks_position('bottom')  # set the position of the second x-axis to bottom
ax2.xaxis.set_label_position('bottom')  # set the position of the second x-axis to bottom
ax2.set_xlabel("dijkpaal")
ax2.spines['bottom'].set_position(('outward', 40))  # place downward
ax2.grid(False)
# plt.show()

plt.savefig(outpath, pad_inches=0.02, dpi=300, bbox_inches='tight')


