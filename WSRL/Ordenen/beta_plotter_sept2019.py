import arcpy
import math
from arcpy.sa import *
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as plticker
from matplotlib.ticker import MaxNLocator
import matplotlib
import pandas as pd


arcpy.env.workspace = r'C:\Users\vince\Desktop\GIS\temp_kaart.gdb'
stph_resultaten ='stph_results'
dijkpalen = r'C:\Users\vince\Desktop\GIS\data.gdb\dijkpalen_traject'
dijktraject = '16-3'
outpath = "C:/Users/vince/Desktop/16_3_beta_stbi"


# arrays maken
array_results = arcpy.da.FeatureClassToNumPyArray(stph_resultaten, ('dv_nummer','stph_jaar0','dijktrajec','FMEAS', 'TMEAS','breedte','stbi_uplift'))
df_results = pd.DataFrame(array_results)
sort_results = df_results.sort_values(['FMEAS'], ascending=[True])

array_dp =arcpy.da.FeatureClassToNumPyArray(dijkpalen, ('RFTIDENT','MEAS','dijktrajec'))
df_dp = pd.DataFrame(array_dp)
sort_dp = df_dp.sort_values(['MEAS'], ascending=[True])


# define plot
plt.style.use('seaborn-whitegrid') #seaborn-ticks
fig = plt.figure(figsize=(60, 10))

ax1 = fig.add_subplot(111, label ="1")
ax2 = fig.add_subplot(111, label="2", frame_on=False)


# lege lijsten
start_bar = []
locaties = []
resultaat = []
breedte = []
tick = []
traject = []
dp = []
dp_MEAS = []
TMEAS = []

# opbouwen nieuwe dataframe en plot resultaten
for index, row in sort_results.iterrows():
    if row['dijktrajec'] == dijktraject:

        start_bar.append(row['FMEAS'])
        locaties.append(int(row['dv_nummer']))
        resultaat.append(row['stbi_uplift'])
        breedte.append(row['breedte'])
        traject.append(row['dijktrajec'])
        tick.append(row['FMEAS']+0.5*row['breedte'])
        TMEAS.append(row['TMEAS'])

df_plots = pd.DataFrame(
    {'start': start_bar,
     'locatie': locaties,
     'traject': traject,
     'resultaat': resultaat,
     'breedte': breedte})

df_plots = df_plots.sort_values(['start'], ascending=[True])

start = df_plots['start'].tolist()
breedte = df_plots['breedte'].tolist()
resultaat = df_plots['resultaat'].tolist()


ax1.bar(start, resultaat, width =breedte,
                 # alpha=0.4,
                 color='w', align='edge', edgecolor='b', linewidth= 6, label = "Dijkvak")

ax1.hlines(5, int(min(start)), int(max(TMEAS)), color='red', zorder=4, linewidth = 5)
ax1.hlines(0, int(min(start)), int(max(TMEAS)), color='black', zorder=4, linewidth = 8)

# opbouwen nieuwe dataframe en plot dijkpalen
for index, row in sort_dp.iterrows():
    if row['dijktrajec'] == dijktraject:

        dp.append(row['RFTIDENT'])
        dp_MEAS.append(row['MEAS'])


df_dp = pd.DataFrame(
    {'dp': dp,
     'MEAS': dp_MEAS})

df_dp = df_dp[::5]

dp_lijst = df_dp['dp'].tolist()
dp_MEAS_lijst = df_dp['MEAS'].tolist()

ax2.vlines(x=dp_MEAS_lijst, ymin=0, ymax=0, color='black', linewidth=2.5, linestyle = '-', label = "Beta 4,8")

# grafiek netjes maken
ax2.axes.get_xaxis().set_visible(False)
ax2.axes.get_yaxis().set_visible(False)

ax3 = ax2.twiny()
ax3.set_xticks(dp_MEAS_lijst)
ax3.set_xticklabels(dp_lijst,rotation=45)

ax1.set_xticks(tick)


ax1.set_xticklabels(locaties, rotation=90)

ax1.tick_params(color = 'red', labelsize=25, axis= 'x')
ax1.tick_params(color = 'red', labelsize=40, axis= 'y')
ax3.tick_params(color = 'blue', labelsize=35)

ax3.set_xlabel("Dijkpaal", fontsize=40)
ax1.set_xlabel(r"Dijkvak", fontsize=40)
ax1.set_ylabel(r"Beta STBI", fontsize=40)
ax1.yaxis.set_label_coords(-0.02,0.5)
ax3.xaxis.set_label_coords(0.5, 1.25)
ax1.xaxis.set_label_coords(0.5, -0.09)


ax1.set_xlim([int(min(start)), int(max(TMEAS))])
ax2.set_xlim([int(min(start)), int(max(TMEAS))])
ax3.set_xlim([int(min(start)), int(max(TMEAS))])

# plt.show()


plt.savefig(outpath, pad_inches=0.02, dpi=300, bbox_inches='tight')
del fig


