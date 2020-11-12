import urllib2
import arcpy

laag = r'C:\Users\Vincent\Desktop\test.gdb\sonderingensafe'


cursor = arcpy.da.UpdateCursor(laag, ["PDF","PDF_test"])

for row in cursor:
    try:
        urllib2.urlopen(row[0])
        row[1] = row[0]
        print row[1]


    except urllib2.HTTPError, e:
        row[1] = "Geen PDF beschikbaar"
        print row[1]

    cursor.updateRow(row)

