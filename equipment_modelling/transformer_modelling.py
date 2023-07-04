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
project_name = '[MA] Equipment Modelling Transformer'
app = pf.open_app(project_name)
ldf_ac = LoadFlow(app)
#ldf_ac.run()
ldf_ac.iopt_pq = 1

hv_voltage = 400  # Hochspannung in kV
lv_voltage = 110  # Niederspannung in kV
load_q = 100  # Reaktive Last in MVAr
target_voltage = 1.0  # Spannungslevel an Sammelschiene 2 in p.u


bus1 = app.GetCalcRelevantObjects('*.ElmTerm')[0]
bus2 = app.GetCalcRelevantObjects('*.ElmTerm')[1]
load = app.GetCalcRelevantObjects('*.ElmLod')[0]
trafo = app.GetCalcRelevantObjects('*.ElmTr2')[0]

load.SetAttribute('plini', 0)  # Aktivleistung auf 0 setzen
load.SetAttribute('qlini', load_q)  # Reaktive Lastleistung einstellen

# HV- und LV-Spannungen einstellen
trafo.SetAttribute('un1', hv_voltage)
trafo.SetAttribute('un2', lv_voltage)

# Tap Position berechnen
hv_lv_ratio = hv_voltage / lv_voltage
tap_voltage = trafo.GetAttribute('un2') * hv_lv_ratio
tap_position = tap_voltage / target_voltage

# Tap Position setzen
trafo.SetAttribute('c:tap_side2', tap_position)

