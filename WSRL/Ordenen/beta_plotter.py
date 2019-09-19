import arcpy
import matplotlib.pyplot as plt
import pandas as pd
import sys
from matplotlib.ticker import FuncFormatter, MaxNLocator

import numpy as np
import numpy.ma as ma




import sys
import matplotlib.ticker as ticker
sys.setrecursionlimit(30000000)

arcpy.env.workspace = "C:/Users/vince/Desktop/GIS/stph_testomgeving.gdb"

# features
invoer = 'maxbeta_7_run_25m'

dijktraject = '16-3'
outpath = "C:/Users/vince/Desktop/16-3_versie3.png"


# lijsten
locatie = []
dijkpaal =[]
beta_zondersloot = []
beta_kopsloot = []
beta_langssloot = []

array = arcpy.da.FeatureClassToNumPyArray(invoer, ('afstand','dijkpaal','beta_max','betamax_langs','betamax_kop', 'dijktraject', 'z_max', 'L', 'dpip'))
df = pd.DataFrame(array)
sort = df.sort(['afstand'])






X = sort['afstand']
Y1 = sort['beta_max']
Y2 = sort['betamax_langs']
Y3 = sort['betamax_kop']
DP = sort['dijkpaal']
z_max = sort['z_max']
L = sort['L']
dpip = sort['dpip']
X_rond = []

# for index, row in df.iterrows():
#     print(row['afstand'], row['dijkpaal'])


# def format_fn(tick_val, tick_pos):
#     for index, row in df.iterrows():
#         if int(tick_val) in X:
#             return row['dijkpaal']
#         else:
#             return ''


list_x = []
list_beta = []
list_betalangs =[]
list_betakop = []
list_betamin = []
list_z_max = []
list_L = []
list_dpip = []


for index, row in sort.iterrows():
    if row['dijktraject'] == dijktraject:
        list_x.append((row['afstand'])/1000)
        list_beta.append(row['beta_max'])
        list_betalangs.append(row['betamax_langs'])
        list_betakop.append(row['betamax_kop'])
        list_z_max.append(row['z_max'])
        list_L.append(row['L'])
        list_dpip.append(row['dpip'])

        test1 = (row['beta_max'])
        test2 = (row['betamax_langs'])
        # test3 = (row['betamax_langs'])

        minimum = test1
        if test2 < minimum:
            minimum = test2
        # if test3 < min:
        #     min = test3
        list_betamin.append(minimum)
        # print min

plt.style.use('seaborn-whitegrid')
fig = plt.figure(figsize=(100, 10))

betagrens_boven = 5.1
betagrens_onder = 4.0
list_x_int = []

for item in list_x:
    # print type(item)
    x_int = int(item)
    list_x_int.append(x_int)



xmin = min(list_x_int)
xmax = max(list_x_int)+1


ax1 = fig.add_subplot(311)
ax1.plot(list_x, list_beta, linewidth=0.8, color='blue', label = 'beta zonder sloten')
ax1.plot(list_x, list_betalangs, linewidth=0.8, color='orange', label = 'beta langs-sloten')
# ax1.plot(list_x, list_betakop,linewidth=0.8, color='green', label = 'beta kop-sloten')
ax1.plot(list_x, list_betamin, linewidth=2.0, color='red', label='minimale beta')

ax1.hlines(betagrens_boven, xmin, xmax, linestyles='dashed', color='black', linewidth = 1.2, label='beta-grens 5,1')
ax1.hlines(betagrens_onder, xmin, xmax,linestyles='dashed', color='black', linewidth = 1.2, label='beta-grens 4,0')

# ax1.plot (list_x, betagrens_boven, '--',linewidth=1.2, color='grey', label='beta-grens 5,1')
# ax1.plot(list_x, betagrens_onder, '--', linewidth = 1.2, color ='red', labe ='beta-grens 4.0')


leg = ax1.legend(frameon=1)
frame = leg.get_frame()
frame.set_facecolor('white')
ax1.set_xlabel(r"afstand [km vanaf links gemeten]")
plt.locator_params(axis='x', nbins=60)


ax2 = fig.add_subplot(312)
ax2.set_ylim([0, 10])
# ax2.plot(list_x, list_z_max, linewidth=1.5, color='black', label = 'bovenkant zandlaag [m NAP]')
ax2.plot(list_x, list_dpip, linewidth=1.5, color='grey', label = 'dikte deklaag [m]')
ax2.set_xlabel(r"dikte deklaag")
plt.locator_params(axis='x', nbins=60)

leg = ax2.legend(frameon=1)
frame = leg.get_frame()
frame.set_facecolor('white')

ax3 = fig.add_subplot(313)
ax3.plot(list_x, list_L, linewidth=1.5, color='orange', label = 'lengte kwelweg L [m]')
ax3.set_xlabel(r"lengte kwelweg L [m]")
plt.locator_params(axis='x', nbins=60)

# ax4 = fig.add_subplot(414)
# ax4.plot(list_x, list_dpip, linewidth=1.5, color='grey', label = 'dikte deklaag [m]')
# ax4.set_xlabel(r"dikte deklaag [m]")
# plt.locator_params(axis='x', nbins=60)






plt.subplots_adjust(hspace=0.5)
plt.savefig(outpath, pad_inches=0.02, dpi=300, bbox_inches='tight')





