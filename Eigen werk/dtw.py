
# import numpy as np
# import matplotlib.pyplot as plt
from scipy.spatial.distance import euclidean
from fastdtw import fastdtw
 
# start=0
# end=2*np.pi
# step=0.1
# k=2
 
# x1=[1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18]
# x2=[1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18]
 
# noise=np.random.uniform(start,end,len(x2))/10
 


# y1=[1,2,3,4,5,6,7,8,8,8,8,7,6,5,4,3,2,1]
 
# y2=[1,2,3,4,5,6,7,8,8,8,7,6,6,6,4,3,2,1]
# sin1=plt.plot(x1,y1)
 
# plt.setp(sin1,color='b',linewidth=2.0)
 
# sin2=plt.plot(x2,y2)
# plt.setp(sin2,color='r',linewidth=2.0)
 
# time_series_A=zip(x1,y1)
# time_series_B=zip(x2,y2)
# distance, path = fastdtw(time_series_A, time_series_B, dist=euclidean)
# print distance
# print path
 
 
 
# index_a,index_b=zip(*path)
# for i in index_a:
#     x1=time_series_A[i][0]
#     y1=time_series_A[i][1]
#     x2=time_series_B[i][0]
#     y2=time_series_B[i][1]
 
#     plt.plot([x1, x2], [y1, y2], color='k', linestyle='-', linewidth=2)
# plt.show()

import arcpy
import pandas as pd
import matplotlib.pyplot as plt

invoerprofielen = r"D:\Projecten\WW\test.gdb\profiel1_z"
array = arcpy.da.FeatureClassToNumPyArray(invoerprofielen, ('afstand','z_ahn'))
data = arcpy.da.FeatureClassToNumPyArray(invoerprofielen, ('afstand','z_ahn'))
df = pd.DataFrame(array)
afstand = df['afstand'].tolist()
hoogte = df['z_ahn'].tolist()

#afstand = pd.DataFrame(afstand)



import numpy as np

from sklearn.preprocessing import normalize



array = np.column_stack((afstand, hoogte))

test = np.array([1,4,4,2])
x =  df['afstand'].tolist()
y = df['z_ahn'].tolist()

# x = array[:,0]
# test_scaled = np.interp(test, (x.min(), x.max()), (-1, +1))


# plt.plot (x, test_scaled)
# plt.show()


# plt.plot(array[:,0],array[:,1])
# plt.show()
# print array.ndim
# print sum(x), x
# norm = [float(i)/sum(x) for i in x]
# print [sum(x) for i in x]

import sklearn


#demo
xd = [1,2,3,4,5,6,7,8,9,10]
yd = [1,2,3,4,3,3,4,4,3,2]

testx = sklearn.preprocessing.minmax_scale(x, feature_range=(0, 1), axis=0, copy=True)
testy = sklearn.preprocessing.minmax_scale(y, feature_range=(0, 1), axis=0, copy=True)

demox = sklearn.preprocessing.minmax_scale(xd, feature_range=(0, 1), axis=0, copy=True)
demoy = sklearn.preprocessing.minmax_scale(yd, feature_range=(0, 1), axis=0, copy=True)

plt.plot(testx,testy)
plt.plot (demox,demoy)

plt.show()

time_series_A=zip(testx,testy)
time_series_B=zip(demox,demoy)
distance, path = fastdtw(time_series_A, time_series_B, dist=euclidean)

print distance
