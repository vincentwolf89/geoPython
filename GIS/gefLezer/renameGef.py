import os

def gefTxt(files):
    for gef in os.listdir(files):
        if gef.endswith(".gef"):

            pass
        elif gef.endswith(".GEF"):
            ingef = os.path.join(files, gef)
            if not os.path.isfile(ingef): continue
            nieuwenaam = ingef.replace('.GEF', '.gef')
            output = os.rename(ingef, nieuwenaam)

files = r'C:\Users\Vincent\Desktop\totaal_gef\totaal_gef'

gefTxt(files)