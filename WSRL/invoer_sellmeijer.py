# import gc
# gc.collect()
from Sellmeijer_basisfuncties import*

arcpy.env.overwriteOutput = True
# werkdatabase
arcpy.env.workspace = r"C:\Users\vince\Desktop\GIS\stph_testomgeving.gdb"

# profielen = "profielen_sm_juli_2019"  #'profielen_sm_juli_2019'
profielen = "profielen_sept_2019"
waterstanden = "gekb_safe"
intredelijn = "voorlanden_aangepast"
intredelijn_buffer = "voorlanden_aangepast"
uittredelijn = "binnenteenlijn_20m"
sloten = 'waterlopen_safe_langs'
sloten_punt = "waterlopen_safe_langs_dummy" #waterlopen_safe_langs_point
dijkvakindeling = "dijkvakindeling_sept_2019"
koppeling_voorlandbuffers = 'voorlanden_aangepast_koppeling'

naam_run = r"C:\Users\vince\Desktop\GIS\stph_sept_2019.gdb\basis_20m"

# standaard parameters
n = 0.25
gamma_p = 16.5
gamma_w = 9.81
theta = 37
sterktefactor = 1
v = 0.000001

velden_voor_profielen(profielen)
koppel_hoogte_zandlaag(profielen)
knoop_gekb_profielen(profielen, waterstanden)
knip_profielen_140m(profielen, intredelijn,dijkvakindeling)
split_profielen_waterlopen(sloten_punt,dijkvakindeling)
uittredepunten_land(uittredelijn,dijkvakindeling)

sellmeijer_aangepast(naam_run, v,gamma_p, gamma_w, theta, sterktefactor, n)

split_berekende_profielen(naam_run)
koppel_losse_delen(dijkvakindeling)
verwijder_lege_velden()
voeg_nieuwe_velden_toe()
join_velden_aan_resultaten(naam_run)
calc_r_exit(naam_run)
bereken_beta(naam_run)




# calc_extensie(naam_run, intredelijn_buffer, koppeling_voorlandbuffers)

# controle_stph(naam_run)
