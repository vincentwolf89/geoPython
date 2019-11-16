import numpy as np
import pandas as pd
import arcpy
from xlsxwriter.workbook import Workbook


workbook = Workbook(r'C:\Users\Vincent\Desktop\chart_combined_test.xlsx')
worksheet = workbook.add_worksheet()

arcpy.env.workspace = r'D:\Projecten\HDSR\data\voorbeeld_oplevering_hdsr.gdb'
arcpy.env.overwriteOutput = True

set = 'punten_profielen_z_125B'
code = 'SUBSECT_ID'
array = arcpy.da.FeatureClassToNumPyArray(set, ('OBJECTID', 'profielnummer', code, 'afstand', 'z_ahn', 'x', 'y'))

df = pd.DataFrame(array)
sorted = df.sort_values(['profielnummer', 'afstand'], ascending=[True, True])



bold = workbook.add_format({'bold': True})


# schrijf kolomnamen
worksheet.write(0, 0, "Profielnummer", bold)
worksheet.write(0, 1, "Afstand [m]", bold)
worksheet.write(0, 2, "Hoogte AHN3 [m NAP]", bold)
worksheet.write(0, 3, "x [RD]", bold)
worksheet.write(0, 4, "y [RD]", bold)

# schrijf kolommen vanuit df
worksheet.write_column('A2', sorted['profielnummer'])
worksheet.write_column('B2', sorted['afstand'])
worksheet.write_column('C2', sorted['z_ahn'])
worksheet.write_column('D2', sorted['x'])
worksheet.write_column('E2', sorted['y'])

grouped = sorted.groupby('profielnummer')
startpunt = 2


# line_chart1 = workbook.add_chart({'type': 'line'})
line_chart1 = workbook.add_chart({'type': 'scatter',
                             'subtype': 'straight'})
for name, group in grouped:
    meetpunten = len(group['profielnummer'])
    if name == 1:
        line_chart1.add_series({
            'name': 'profiel ' + str(name),

            'categories': '=Sheet1!B' + str(startpunt) + ':B' + str(meetpunten + 1),
            'values': '=Sheet1!C' + str(startpunt) + ':C' + str(meetpunten + 1),
        })

    else:
        if name is not 1:
            line_chart1.add_series({
                'name': 'profiel '+str(name),

                'categories': '=Sheet1!B'+str(startpunt)+':B' + str(startpunt+meetpunten-1),
                'values':     '=Sheet1!C'+str(startpunt)+':C' + str(startpunt+meetpunten-1),
            })

    startpunt += (meetpunten)
    # if name ==5:
    #     break




# # grafieken
# line_chart1 = workbook.add_chart({'type': 'line'})
#
# # Configure the data series for the secondary chart.
# line_chart1.add_series({
#     'name':       'profiel_1',
#     'categories':        '=Sheet1!$B$2:$B$'+str(meetpunten+1),
#     'values':        '=Sheet1!$C$2:$C$'+str(meetpunten+1),
# })

# line_chart1.add_series({
#     'profiel':       'profiel_1',
#     'hoogte':        [0,2,3,4,5,6],
#     'values':        [0,2,2,4,5,6],
# })

line_chart1.set_title({'name': 'Overzicht profielen'})
line_chart1.set_x_axis({'name': 'Afstand [m]'})
line_chart1.set_y_axis({'name': 'Hoogte [m NAP]'})
line_chart1.set_x_axis({'interval_tick': 0.5})
line_chart1.set_x_axis({'min': -10, 'max': 20})
worksheet.insert_chart('E18', line_chart1)

workbook.close()