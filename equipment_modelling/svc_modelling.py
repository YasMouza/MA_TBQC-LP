import sys 
sys.path.append('C:\\Users\\yasin\\source\\MA_TBQC LP')
from main_powerfactory import PowerFactory
from loadflow import LoadFlow
import math
import numpy as np
import pandas as pd

from main_powerfactory import PowerFactory
from loadflow import LoadFlow

path = r'C:\Program Files\DIgSILENT\PowerFactory 2023 SP3A\Python\3.9'
pf = PowerFactory(path)
project_name = '[MA] Equipment Modelling - SVC'
app = pf.open_app(project_name)
ldf_ac = LoadFlow(app)
#ldf_ac.run()
ldf_ac.iopt_pq = 1

bus1 = app.GetCalcRelevantObjects('*.ElmTerm')[0]
bus2 = app.GetCalcRelevantObjects('*.ElmTerm')[1]
load = app.GetCalcRelevantObjects('*.ElmLod')[0]
svs = app.GetCalcRelevantObjects('*.ElmSvs')[0]
line = app.GetCalcRelevantObjects('*.ElmLne')[0]

# Werte setzen
q_min = -200  # MVAr
q_max = 200  # MVAr
i_crtl = 1  # Steuerungsmodus: 1 = Voltage control 
usetp = 1 # Spannungsregelung = 1 p.u.
tcrqact = 100  # MVAr Aktivierungsschwelle für TCR
load_q = 500  # MVAr

# TCR Reactive Power
tcr_reactive_power = min(max(load_q, q_min), q_max)
svs.SetAttribute('tcrqact', tcrqact)
svs.SetAttribute('qmin', q_min)
svs.SetAttribute('qmax', q_max)
svs.SetAttribute('i_ctrl', i_crtl)
svs.SetAttribute('usetp', usetp)
load.SetAttribute('qlini', load_q)

ldf_ac.run()

xpu = line.GetAttribute('e:xSbasepu')

# Ergebnisse abrufen
tcr_reactive_power = svs.GetAttribute('c:qtcr')
tsc_reactive_power = svs.GetAttribute('c:qtsc')
nncap = svs.GetAttribute('c:nncap')


# Manuelle Berechnung
nncap_manual = math.ceil(abs(load_q) / q_max)

if load_q > 0:
    tcr_reactive_power_manual = tcrqact 
    tsc_reactive_power_manual = -(load_q + tcr_reactive_power_manual)
else:
    tcr_reactive_power_manual = max(load_q, q_min)
    tsc_reactive_power_manual = load_q - tcr_reactive_power_manual
    

# Ergebnisse ausgeben
print("TCR Reactive Power (Power Factory):", tcr_reactive_power, "MVAr")
print("TCR Reactive Power (Manuell):", tcr_reactive_power_manual, "MVAr")

print("TSC Reactive Power (Power Factory):", tsc_reactive_power, "MVAr")
print("TSC Reactive Power (Manuell):", tsc_reactive_power_manual, "MVAr")

print("nncap of SVS (Power Factory):", nncap)
print("nncap of SVS (Manuell):", nncap_manual)