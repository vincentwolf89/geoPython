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

arrayKnik = arcpy.da.FeatureClassToNumPyArray(knikpunten, ('Contour','MEAS'))
dfKnik = pd.DataFrame(arrayKnik)
sortKnik = dfKnik.sort_values(by=['MEAS'])

plt.rcParams["figure.figsize"] = [50, 10]
plt.plot(sortProfiel['MEAS'],sortProfiel['Contour'])
plt.plot(sortKnik['MEAS'],sortKnik['Contour'],'bo')

# plt.show()
plt.savefig(outputFigures+"/naam.jpg")
plt.close()