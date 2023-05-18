import numpy as np
from main_powerfactory import PowerFactory
from loadflow import LoadFlow 
import math as m 
import pandas as pd 
import matplotlib.pyplot as plt 
import gurobipy as gp
from gurobipy import *


# 1. ACloadflow
path = r'C:\Program Files\DIgSILENT\PowerFactory 2023 SP3A\Python\3.9'
pf = PowerFactory(path)
project_name = 'TBQC'
app = pf.open_app(project_name)
ldf_ac = LoadFlow(app)

ldf_ac.run()

Sbase = 100

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

all_nodes = []
for line in line_all:
    all_nodes.append(line.bus1.cterm)
    all_nodes.append(line.bus2.cterm)
    
    all_nodes_flat = [node for node in all_nodes if node is not None]

xpu = np.array(xpu) 
rpu = np.array(rpu) 
b_cap = -xpu/(rpu**2+xpu**2)
b_ind = -xpu/(rpu**2+xpu**2) - 1j*rpu/xpu

B_cap = [[-125, 125], [125, -125]]
B_ind = [[-50+50j, 50-50j], [50-50j, -50+50j]]
G = 0 

