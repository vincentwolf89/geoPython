import matplotlib.pyplot as plt
import numpy as np
import numpy.ma as ma
import pandas as pd
from pandas import ExcelWriter
from pandas import ExcelFile
import matplotlib.pyplot as plt
from os import path
import sys
import matplotlib.ticker as ticker
sys.setrecursionlimit(30000000)


plt.rcParams["figure.figsize"] = [30, 10]

#locaties
import_bestand = ('C:/Users/vince/Desktop/waterstanden/ws_compleet(flip).xlsx')
outpath = "C:/Users/vince/Desktop/waterstanden/plots/test"

#dataframes
df = pd.read_excel(import_bestand, sheet_name='werkblad')

#z = pd.concat([df['z_dag1'], df['z_ahn']],axis=1)
#pd.concat([df['naam_dwp'], df['naam_dwp2']],axis=1)

grouped = df.groupby('naam_dwp')

#masker = np.isfinite(grouped['z_dag1'])
for name, group in grouped:
    fig = plt.figure()
    #plt.style.use('seaborn-dark')
    ax1 = fig.add_subplot(111)
    #Z = group['x-as']
    #Zt = group['naam_lijn']

    #Zt2 = np.ma.masked_where(Zt == "niks", Zt)
    #ax2 = ax1.twiny()

    #lijnen
    group.plot.line(ax=ax1, color='red', x= "x-as", y = "z_ahn", legend=True, label="ahn3", linewidth=1.5)
    group.plot.line(ax=ax1, color='midnightblue', x="x-as", y="z_dag0", legend=True, label="7 januari 2003", linewidth=0.8)
    group.plot(ax=ax1, color='navy', x="x-as", y="z_dag1", legend=True, label="8 januari 2003", linewidth=0.8)
    group.plot(ax=ax1, color='mediumblue', x="x-as", y="z_dag2", legend=True, label="9 januari 2003", linewidth=0.8)
    group.plot(ax=ax1, color='royalblue', x="x-as", y="z_dag3", legend=True, label="10 januari 2003", linewidth=0.8)
    group.plot(ax=ax1, color='cornflowerblue', x="x-as", y="z_dag4", legend=True, label="11 januari 2003", linewidth=0.8)
    group.plot(ax=ax1, color='deepskyblue', x="x-as", y="z_dag5", legend=True, label="12 januari 2003", linewidth=0.8)
    group.plot(ax=ax1, color='skyblue', x="x-as", y="z_dag6", legend=True, label="13 januari 2003", linewidth=0.8)
    group.plot(ax=ax1, color='lightskyblue', x="x-as", y="z_dag7", legend=True, label="14 januari 2003", linewidth=0.8)
    group.plot(ax=ax1, color='black', x="x-as", y="HBN_2015", legend=True, label="waterstand OI2014 (2015)", linewidth=1, dashes=[2, 2])
    group.plot(ax=ax1, color='navy', x="x-as", y="z_rivier", legend=True, label="waterstand Lek", linewidth=2, dashes=[2, 1])

    #scatters van de dagen
    #group.plot.scatter(ax=ax1, color='midnightblue', x= "x-as", y = "z_dag0", legend=False, label="7 januari 2003", marker ="+")
    #group.plot.scatter(ax=ax1, color='navy', x="x-as", y="z_dag1", legend=False, label="8 januari 2003", s = 1.5)
    #group.plot.scatter(ax=ax1, color='mediumblue', x="x-as", y="z_dag2", legend=False, label="9 januari 2003", s = 1.5)
    #group.plot.scatter(ax=ax1, color='royalblue', x="x-as", y="z_dag3", legend=False, label="10 januari 2003", s = 1.5)
    #group.plot.scatter(ax=ax1, color='cornflowerblue', x="x-as", y="z_dag4", legend=False, label="11 januari 2003",s = 1.5)
    #group.plot.scatter(ax=ax1, color='deepskyblue', x="x-as", y="z_dag5", legend=False, label="12 januari 2003", s = 1.5)
    #group.plot.scatter(ax=ax1, color='skyblue', x="x-as", y="z_dag6", legend=False, label="13 januari 2003", s = 1.5)
    #group.plot.scatter(ax=ax1, color='lightskyblue', x="x-as", y="z_dag7", legend=False, label="14 januari 2003", s = 1.5)


    plt.title(str(name), fontsize=15)
    # place new x-axis
    ax1.set_ylabel('hoogte [m +NAP]')
    ax1.set_xlabel('afstand [m]')

#tweede x-as
    #ax2 = ax1.twinx()
    #ax2.xaxis.set_ticks_position('bottom')  # set the position of the second x-axis to bottom
    #ax2.xaxis.set_label_position('bottom')  # set the position of the second x-axis to bottom
    #ax2.spines['bottom'].set_position(('outward', 40))  # place downward
    #ax2.set_xlabel('meetlocatie')
    #ax2.set_xlim(ax1.get_xlim())
    #plt.xticks(Z, Zt, rotation=45)
    #tick_spacing = 10
    #tick_spacing2 = 20
    #ax1.xaxis.set_major_locator(ticker.MultipleLocator(tick_spacing))
    #ax2.xaxis.set_major_locator(ticker.NullLocator())
    #plt.savefig(path.join(outpath, "profiel_{0}.png".format(name)), pad_inches=0.02, dpi=300, bbox_inches='tight')


    #plt.show()

    plt.savefig(path.join(outpath, "profiel_{0}.png".format(name)), pad_inches=0.02, dpi=300, bbox_inches='tight')




