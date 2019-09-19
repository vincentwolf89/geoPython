import os
import xlrd
from openpyxl import load_workbook
import os
import win32com.client as win32

#workbook with new names:
name_workbook = ("C:/Users/vince/Desktop/test.xlsx")

#location with existing excel files:
excel_files = ('C:/Users/vince/Desktop/dwp_origineel/')




def filename_changer():
    # define results for input .xlsx
    workbook = xlrd.open_workbook(name_workbook)
    worksheet = workbook.sheet_by_name("Sheet1")

    voegnaam = worksheet.col_values(4, 1)
    nieuwe_filename = worksheet.col_values(6,1)

    d_test = dict(zip(voegnaam, nieuwe_filename))
    #d_traject_tot = dict(zip(voegnaam, traject_tot))
    #d_dwp_naam = dict(zip(voegnaam, dwp_naam))
    #d_dwp_nummer = dict(zip(voegnaam, dwp_nummer))

    for root, dirs, files in os.walk(excel_files):
        xlsfiles = [_ for _ in files if _.endswith('.xlsx')]
        for file in xlsfiles:
            for key, value in d_test.items():
                if key == file:
                    os.rename(os.path.join(excel_files, file), os.path.join(excel_files, value))





filename_changer()


