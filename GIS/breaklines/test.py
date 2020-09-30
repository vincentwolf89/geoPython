import arcpy
import matplotlib.pyplot as plt
import pandas as pd

arcpy.env.workspace = r'D:\Projecten\HDSR\2020\gisData\testbatchSafe.gdb'

profiel = 'testIsectFocalPoint'
knikpunten = 'testknikpunten542'
outputFigures = r"C:\Users\Vincent\Desktop\cPointFigures"

arrayProfiel = arcpy.da.FeatureClassToNumPyArray(profiel, ('Contour','MEAS'))
dfProfiel = pd.DataFrame(arrayProfiel)
sortProfiel = dfProfiel.sort_values(by=['MEAS'])

arrayKnik = arcpy.da.FeatureClassToNumPyArray(knikpunten, ('Contour','MEAS','cPoint'))
dfKnik = pd.DataFrame(arrayKnik)
sortKnik = dfKnik.sort_values(by=['MEAS'])

plt.style.use('seaborn-whitegrid') #seaborn-ticks
fig = plt.figure(figsize=(60, 10))
ax1 = fig.add_subplot(111, label ="1")

buitenteen = sortKnik.loc[sortKnik['cPoint'] == 'buitenteen']
if not buitenteen.empty:
    print "niet leeg"
else:
    print "leeg"

ax1.plot(sortProfiel['MEAS'],sortProfiel['Contour'])
ax1.plot(sortKnik['MEAS'],sortKnik['Contour'],'bo',markersize=20,color='red')

ax1.plot(buitenteen['MEAS'],buitenteen['Contour'],'bo',markersize=20,color='yellow',label="Buitenteen")

ax1.legend(frameon=False, loc='upper left',prop={'size': 30})


# plt.show()
plt.savefig(outputFigures+"/naam.jpg")
plt.close()