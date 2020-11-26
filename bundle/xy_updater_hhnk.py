import csv
import xlwt

openfile = 'C:/Users/vince/Desktop/raaien_xy_tx_interpolated.txt'
resultfile = "C:/Users/vince/Desktop/xy_raaien.xls"
with open (openfile, 'r') as f:
    raai = [row[0] for row in csv.reader(f,delimiter='\t')]

with open (openfile, 'r') as f:
    x = [row[1] for row in csv.reader(f,delimiter='\t')]

with open (openfile, 'r') as f:
    y = [row[2] for row in csv.reader(f,delimiter='\t')]


def writer():

    #define styles
        style = xlwt.easyxf('font: bold 1')  # define style
        wb = xlwt.Workbook()  # open new workbook
        ws = wb.add_sheet("overzicht")  # add new sheet

        # write headers
        row = 0
        #ws.write(row, 0, "naam_raai", style=style)
        #ws.write(row, 1, "x", style=style)
        #ws.write(row, 2, "y", style=style)

        # write colums
        row = 0
        for i in raai:
            ws.write(row, 0, i)
            row += 1

        row = 0
        for i in x:
            ws.write(row, 1, i)
            row += 1

        row = 0
        for i in y:
            ws.write(row, 2, i)
            row += 1


        # save
        wb.save(resultfile)


writer()