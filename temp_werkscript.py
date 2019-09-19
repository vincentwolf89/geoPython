import os
import xlwt




resultfile = "C:/Users/vince/Desktop/bijlagen_stbi.xls"
dv_nummer = []
bestanden = []


directory = r'C:\Users\vince\Desktop\Laatste versies berekeningen STBI Safe 2-9-2019'

for filename in os.listdir(directory):
    dv_nummer.append(filename[8:10])
    bestanden.append(filename)

print dv_nummer, bestanden

wb = xlwt.Workbook()  # open new workbook
ws = wb.add_sheet("overzicht")  # add new sheet

row = 1
for i in dv_nummer:
    ws.write(row, 0, i)
    row += 1

row = 1
for i in bestanden:
    ws.write(row, 1, i+".zip")
    row += 1
wb.save(resultfile)


