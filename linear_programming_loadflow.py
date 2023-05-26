

from main_powerfactory import PowerFactory
from loadflow import LoadFlow
import numpy as np
import math as m
import pandas as pd
import matplotlib.pyplot as plt

# 1. ACloadflow
path = r'C:\Program Files\DIgSILENT\PowerFactory 2023 SP3A\Python\3.9'
pf = PowerFactory(path)
project_name = '2_Bus'
app = pf.open_app(project_name)

ldf_ac = LoadFlow(app)

ldf_ac.run()

line_all = app.GetCalcRelevantObjects('*.ElmLne')
line_names = []
xpu = []
rpu = []
volt_magnitude_j = []
volt_magnitude_i = []
phi_j = []
phi_i = []
active_power = []
reactive_power = []

for line in line_all:
    line_names.append(line.loc_name)
    xpu.append(line.GetAttribute('e:xSbasepu'))
    rpu.append(line.GetAttribute('e:rSbasepu'))
    volt_magnitude_j.append(line.GetAttribute('m:u:bus2')) #in p.u.
    volt_magnitude_i.append(line.GetAttribute('m:u:bus1')) #in p.u.
    phi_j.append(line.GetAttribute('m:phiu1:bus2')) #in deg
    phi_i.append(line.GetAttribute('m:phiu1:bus1')) #in deg
    active_power.append(line.GetAttribute('m:P:bus1'))
    reactive_power.append(line.GetAttribute('m:Q:bus1'))

lines_all_node1 = [line.bus1.cterm for line in line_all]
lines_all_node2 = [line.bus2.cterm for line in line_all]
lines_all_node1_name = [line.bus1.cterm.loc_name for line in line_all]
lines_all_node2_name = [line.bus2.cterm.loc_name for line in line_all]
phi_j_rad = np.deg2rad(phi_j)
phi_i_rad = np.deg2rad(phi_i) 

#Create Overview DataFrame
lines = pd.DataFrame(
    [line_names,lines_all_node1_name, lines_all_node2_name, rpu, xpu, volt_magnitude_j, volt_magnitude_i],
    index = ['Leitung', 'Terminal i', 'Terminal j', 'rpu', 'xpu', 'v_j', 'v_i']
).transpose()
print(lines)

def b_values(rpu, xpu):
    b = -xpu/(rpu**2+xpu**2)
    return b
def g_values(rpu, xpu):
    g = rpu/(rpu**2+xpu**2) 
    return g



Sbase = 100 #MVA

