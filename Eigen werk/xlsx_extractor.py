import os
import xlrd
import xlwt


#define empty lists
kritiek_verval = []
optredend_verval = []
totaal_verschil = []

#find values in .xlsx's
for root, dirs, files in os.walk("C:/Users/vince/Desktop/uitvoer_script/test"):
    xlsfiles=[ _ for _ in files if _.endswith('.xlsx') ]
    for xlsfile in xlsfiles:
        workbook = xlrd.open_workbook(os.path.join(root,xlsfile))
        worksheet = workbook.sheet_by_name("Overzicht scenario's_Pf")

        #c0 = [worksheet.row_values(i)[0] for i in range(worksheet.nrows) if worksheet.row_values(i)[0]]
        kv = worksheet.cell(33,6)
        ov = worksheet.cell(34,6)

        kv1 = kv.value
        ov1 = ov.value
        verschil = kv1 - ov1
        kritiek_verval.append(kv1)
        optredend_verval.append(ov1)
        totaal_verschil.append(verschil)

style = xlwt.easyxf('font: bold 1')         #define style
wb = xlwt.Workbook()                        #open new workbook
ws = wb.add_sheet("overzicht")              #add new sheet

#write headers
row = 0
ws.write(row,0,"locatie", style = style)
ws.write(row,1,"kritiek verval",style = style)
ws.write(row,2,"optredend verval",style = style)
ws.write(row,3,"verschil(kv-ov)",style = style)

#write colums
row = 1
for i in xlsfiles:
    ws.write(row,0,i)
    row +=1

row = 1
for i in kritiek_verval:
    ws.write(row,1,i)
    row +=1

row = 1
for i in optredend_verval:
    ws.write(row,2,i)
    row +=1

row = 1
for i in totaal_verschil:
    ws.write(row,3,i)
    row +=1

#save
wb.save("stph_2075.xls")
