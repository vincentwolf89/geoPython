import arcpy
import math
import numpy as np
from arcpy.sa import *
import xlwt
import pandas as pd
from itertools import groupby
# uitzetten melding pandas#
pd.set_option('mode.chained_assignment', None)
from basisfuncties import*
import matplotlib.pyplot as plt

arcpy.env.workspace = r'D:\Projecten\HDSR\data\werk.gdb'
arcpy.env.overwriteOutput = True

invoer = 'punten_profielen_z'
code = 'SUBSECT_ID'
afstanden_punten = 0.5

array = arcpy.da.FeatureClassToNumPyArray(invoer, ('OBJECTID', 'profielnummer',code, 'afstand', 'z_ahn'))
df = pd.DataFrame(array)
df2 = df.dropna()
sorted = df2.sort_values(['profielnummer', 'afstand'], ascending=[True, True])
grouped = sorted.groupby('profielnummer')

for name, group in grouped:
    # print group

    group['verschil'] = abs(group['z_ahn'].diff())
    group['gem_verschil'] = group.iloc[:, 5].rolling(window=3).mean()

    dx_dt = np.gradient(group['afstand'])
    dy_dt = np.gradient(group['z_ahn'])
    velocity = np.array([[dx_dt[i], dy_dt[i]] for i in range(dx_dt.size)])

    ds_dt = np.sqrt(dx_dt * dx_dt + dy_dt * dy_dt)
    tangent = np.array([1 / ds_dt] * 2).transpose() * velocity

    tangent_x = tangent[:, 0]
    tangent_y = tangent[:, 1]

    deriv_tangent_x = np.gradient(tangent_x)
    deriv_tangent_y = np.gradient(tangent_y)

    dT_dt = np.array([[deriv_tangent_x[i], deriv_tangent_y[i]] for i in range(deriv_tangent_x.size)])

    length_dT_dt = np.sqrt(deriv_tangent_x * deriv_tangent_x + deriv_tangent_y * deriv_tangent_y)

    normal = np.array([1 / length_dT_dt] * 2).transpose() * dT_dt

    d2s_dt2 = np.gradient(ds_dt)
    d2x_dt2 = np.gradient(dx_dt)
    d2y_dt2 = np.gradient(dy_dt)

    curvature = np.abs(d2x_dt2 * dy_dt - dx_dt * d2y_dt2) / (dx_dt * dx_dt + dy_dt * dy_dt) ** 1.5
    t_component = np.array([d2s_dt2] * 2).transpose()
    n_component = np.array([curvature * ds_dt * ds_dt] * 2).transpose()

    acceleration = t_component * tangent + n_component * normal

    print acceleration






    plt.plot(group['afstand'], group['z_ahn'])

    print group
    # plt.show()
    break

