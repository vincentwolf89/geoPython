import arcpy
import os
import xlrd
arcpy.env.overwriteOutput = True

arcpy.env.workspace = r'C:/Users/vince/Desktop/GIS/zandlagen_safe.gdb'

#table = 'test_zand'

def create_route_layer():
    # Set local variables
    in_lines = "route"
    rid = "route_id"
    out_routes = "route_safe"

    # Execute CreateRoutes
    arcpy.CreateRoutes_lr(in_lines, rid, out_routes, "LENGTH", "#", "#", "LOWER_LEFT")


def create_route_event_layer():
    # Set local variables
    rt = "route_safe"
    rid = "route_id"
    tbl = table
    props = "routeid LINE x_van x_tot"
    lyr = "temp_lyr"

    # Execute MakeRouteEventLayer
    arcpy.MakeRouteEventLayer_lr(rt, rid, tbl, props, lyr, "#", "ERROR_FIELD")
    arcpy.CopyFeatures_management("temp_lyr", table+"_route")

    print "route for "+table+" created!"






def importallsheets(in_excel, out_gdb):
    workbook = xlrd.open_workbook(in_excel)
    sheets = [sheet.name for sheet in workbook.sheets()]

    print('{} sheets found: {}'.format(len(sheets), ','.join(sheets)))
    for sheet in sheets:
        # The out_table is based on the input excel file name
        # a underscore (_) separator followed by the sheet name
        out_table = os.path.join(
            out_gdb,
            arcpy.ValidateTableName(
                "{0}_{1}".format(os.path.basename(in_excel), sheet),
                out_gdb))

        print('Converting {} to {}'.format(sheet, out_table))

        # Perform the conversion
        arcpy.ExcelToTable_conversion(in_excel, out_table, sheet)






# if __name__ == '__main__':
#     importallsheets('C:/Users/vince/Desktop/zandlaag_totaal.xls',
#                     'C:/Users/vince/Desktop/GIS/zandlagen_safe.gdb')


for table in arcpy.ListTables():
    create_route_event_layer()


