import arcpy
import math
from arcpy.sa import *
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.ticker as plticker
from matplotlib.ticker import MaxNLocator
import matplotlib
import pandas as pd


#fix min max y-as, locatie dijkpalen x2

arcpy.env.workspace = r'C:\Users\vince\Desktop\GIS\temp_kaart.gdb'
resultaten ='all_beta_aug_sept_2019'
dijkpalen = r'C:\Users\vince\Desktop\GIS\data.gdb\dijkpalen_traject'
dijktraject = '16-3'
outpath = "C:/Users/vince/Desktop/16_3_beta"


# arrays maken
array_results = arcpy.da.FeatureClassToNumPyArray(resultaten, ('dv_nummer','dijktrajec','FMEAS', 'TMEAS','breedte','stbi','section','gekb','stph'))
df_results = pd.DataFrame(array_results)
sort_results = df_results.sort_values(['FMEAS'], ascending=[True])

array_dp =arcpy.da.FeatureClassToNumPyArray(dijkpalen, ('RFTIDENT','MEAS','dijktrajec'))
df_dp = pd.DataFrame(array_dp)
sort_dp = df_dp.sort_values(['MEAS'], ascending=[True])


# define plot
# plt.style.use('seaborn-ticks')
fig = plt.figure(figsize=(60, 20))

ax1 = fig.add_subplot(111, label ="1")
ax2 = fig.add_subplot(111, label="2", frame_on=False)



# lege lijsten
dv_nummer = []
start = []
eind = []

resultaat_stph = []
resultaat_stbi = []
resultaat_gekb = []

locaties = []
breedte = []
tick = []
traject = []
dp = []
dp_MEAS = []
TMEAS = []

# opbouwen nieuwe dataframe en plot resultaten
for index, row in sort_results.iterrows():
    if row['dijktrajec'] == dijktraject:

        start.append(row['FMEAS'])
        eind.append(row['TMEAS'])
        dv_nummer.append(row['dv_nummer'])
        resultaat_stph.append(row['stph'])
        resultaat_stbi.append(row['stbi'])
        resultaat_gekb.append(row['gekb'])
        locaties.append(int(row['dv_nummer']))
        traject.append(row['dijktrajec'])
        tick.append(row['FMEAS']+0.5*row['breedte'])
        TMEAS.append(row['TMEAS'])

# sectie stph
df_plots_start_stph = pd.DataFrame(
    {'dv': dv_nummer,
     'tick': tick,
     'start': start,
     'traject': traject,
     'resultaat': resultaat_stph})

df_plots_eind_stph = pd.DataFrame(
    {'dv': dv_nummer,
     'start': eind,
     'tick': tick,
     'traject': traject,
     'resultaat': resultaat_stph})

df_plots_start_stph = df_plots_start_stph.sort_values(['dv', 'start'], ascending=[True, True])
df_plots_eind_stph = df_plots_eind_stph.sort_values(['dv', 'start'], ascending=[True, True])
combined_stph = df_plots_start_stph.append(df_plots_eind_stph)
sorted_stph = combined_stph.sort_values(['dv','start'], ascending=[True, True])



# sectie stbi
df_plots_start_stbi = pd.DataFrame(
    {'dv': dv_nummer,
     'start': start,
     'tick': tick,
     'traject': traject,
     'resultaat': resultaat_stbi})

df_plots_eind_stbi = pd.DataFrame(
    {'dv': dv_nummer,
     'start': eind,
     'tick': tick,
     'traject': traject,
     'resultaat': resultaat_stbi})

df_plots_start_stbi = df_plots_start_stbi.sort_values(['dv', 'start'], ascending=[True, True])
df_plots_eind_stbi = df_plots_eind_stbi.sort_values(['dv', 'start'], ascending=[True, True])
combined_stbi = df_plots_start_stbi.append(df_plots_eind_stbi)
sorted_stbi = combined_stbi.sort_values(['dv','start'], ascending=[True, True])


# sectie gekb
df_plots_start_gekb = pd.DataFrame(
    {'dv': dv_nummer,
     'start': start,
     'tick': tick,
     'traject': traject,
     'resultaat': resultaat_gekb})

df_plots_eind_gekb = pd.DataFrame(
    {'dv': dv_nummer,
     'start': eind,
     'tick': tick,
     'traject': traject,
     'resultaat': resultaat_gekb})

df_plots_start_gekb = df_plots_start_gekb.sort_values(['dv', 'start'], ascending=[True, True])
df_plots_eind_gekb = df_plots_eind_gekb.sort_values(['dv', 'start'], ascending=[True, True])
combined_gekb = df_plots_start_gekb.append(df_plots_eind_gekb)
sorted_gekb = combined_gekb.sort_values(['dv','start'], ascending=[True, True])


# plot punten, lijnen
ax1.scatter(sorted_stph['tick'], sorted_stph['resultaat'], color='b', label = None, s = 400, zorder=10)
ax1.scatter(sorted_stbi['tick'], sorted_stbi['resultaat'], color = 'g', label = None, s= 400, zorder=9)
ax1.scatter(sorted_gekb['tick'], sorted_gekb['resultaat'], color = 'r', label = None, s = 400, zorder =8)

ax1.plot(sorted_stph['start'], sorted_stph['resultaat'], color='b', label = "Stph", linewidth= 7, zorder=6)
ax1.plot(sorted_stbi['start'], sorted_stbi['resultaat'], color = 'g', label = "Stbi", linewidth= 7, zorder= 5)
ax1.plot(sorted_gekb['start'], sorted_gekb['resultaat'], color = 'r', label = "Hoogte", linewidth= 7, zorder =4)

# legenda instellen
leg = ax1.legend(loc=4, frameon=1,prop={'size': 50})
leg.set_zorder(20)
frame = leg.get_frame()
frame.set_facecolor('white')

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


# grafiek afmaken
ax2.axes.get_xaxis().set_visible(False)
ax2.axes.get_yaxis().set_visible(False)
ax3 = ax2.twiny()
ax3.set_xticks(dp_MEAS_lijst)
ax3.set_xticklabels(dp_lijst,rotation=45)

ax1.set_xticks(tick, minor=False)
ax1.set_xticks(start, minor = True)
y_ticks = ax1.get_yticks()
# y_ticks = np.arange(start=0, stop=8, step=2)
ax1.set_yticks(y_ticks, minor = True)

ax1.xaxis.grid(True, which='minor', linestyle='--', linewidth= 4, color = 'grey', zorder =1)
ax1.yaxis.grid(True, which='minor',linewidth= 3, zorder =2)

ax1.set_xticklabels(locaties, rotation=90)
ax1.tick_params(color = 'red', labelsize=32, axis= 'x')
ax1.tick_params(color = 'red', labelsize=40, axis= 'y')
ax3.tick_params(color = 'blue', labelsize=35)

ax3.set_xlabel(r"Dijkpalen", fontsize=40)
ax1.set_xlabel(r"Dijkvakken", fontsize=40)
ax1.set_ylabel(r'Betrouwbaarheidsindex '+u'\u03B2'+' [-/jaar]', fontsize=40)

ax1.yaxis.set_label_coords(-0.02,0.5)
ax3.xaxis.set_label_coords(0.5, 1.14)
ax1.xaxis.set_label_coords(0.5, -0.07)


ax1.set_xlim([int(min(start)), int(max(TMEAS))])
ax2.set_xlim([int(min(start)), int(max(TMEAS))])
ax3.set_xlim([int(min(start)), int(max(TMEAS))])


ax1.set_ylim(0, max(resultaat_stbi+resultaat_stph+resultaat_gekb)+0.5)
ax1.grid(False)
plt.setp(ax1.spines.values(), linewidth=3)

# plt.show()
plt.savefig(outpath, pad_inches=0.02, dpi=300, bbox_inches='tight')
del fig


