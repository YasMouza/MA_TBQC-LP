import numpy as np
from main_powerfactory import PowerFactory
from loadflow import LoadFlow 
import math 
import pandas as pd 
import matplotlib.pyplot as plt 
import gurobipy as gp
from gurobipy import GRB 
from gurobipy import *


# 1. ACloadflow
path = r'C:\Program Files\DIgSILENT\PowerFactory 2023 SP3A\Python\3.9'
pf = PowerFactory(path)
project_name = 'TBQC'
app = pf.open_app(project_name)
ldf_ac = LoadFlow(app)
ldf_ac.run()

#2. Grid parameters
Sbase = 100

line_all = app.GetCalcRelevantObjects('*.ElmLne')
line_names = []
xpu = []
rpu = []
volt_magnitude_j = []
volt_magnitude_i = []
phi_j = []
phi_i = []
active_power_i = []
reactive_power_i = []
active_power_j = []
reactive_power_j = []
for line in line_all:
    line_names.append(line.loc_name)
    xpu.append(line.GetAttribute('e:xSbasepu'))
    rpu.append(line.GetAttribute('e:rSbasepu'))
    volt_magnitude_j.append(line.GetAttribute('m:u:bus2')) #in p.u.
    volt_magnitude_i.append(line.GetAttribute('m:u:bus1')) #in p.u.
    phi_j.append(line.GetAttribute('m:phiu1:bus2')) #in deg
    phi_i.append(line.GetAttribute('m:phiu1:bus1')) #in deg
    active_power_i.append(line.GetAttribute('m:P:bus1'))
    reactive_power_i.append(line.GetAttribute('m:Q:bus1'))
    active_power_j.append(line.GetAttribute('m:P:bus2'))
    reactive_power_j.append(line.GetAttribute('m:Q:bus2'))

lines_all_node1 = [line.bus1.cterm for line in line_all]
lines_all_node2 = [line.bus2.cterm for line in line_all]

all_nodes = []
for line in line_all:
    all_nodes.append(line.bus1.cterm)
    all_nodes.append(line.bus2.cterm)
    

xpu = np.array(xpu) 
rpu = np.array(rpu) 
b_cap = -xpu/(rpu**2+xpu**2)
b_ind = -xpu/(rpu**2+xpu**2) - 1j*rpu/xpu

B_cap = [[-125, 125], [125, -125]]
B_ind = [[-50+50j, 50-50j], [50-50j, -50+50j]]
G = 0 

P = np.concatenate([active_power_i, active_power_j])
P = P/Sbase
R = np.concatenate([reactive_power_i, reactive_power_j]) 
R = R/Sbase


#3. Linear Program by Gurobipy 
m = gp.Model('Cold-Start-AC-Load-Flow')

# 3.1.  Define Variables
num_nodes = len(all_nodes)
num_lines = len(line_all)

v_magnitudes = m.addVars(range(num_nodes), lb=0, ub=1.5, name='v_magnitude')
v_angles = m.addVars(range(num_nodes), lb=-math.pi, ub=math.pi, name='v_angle')
cos_values = m.addVars(range(num_lines), name='cos')

# 3.2. Define Maximization Objective
m.setObjective(gp.quicksum(cos_values), GRB.MAXIMIZE)

# 3.3. Define Constraints
# 3.3.1. Voltage Magnitude Constraints
v_magnitudes_dict = {}  # Dictionary zur Speicherung der Variablen pro Knoten
for i, node in enumerate(all_nodes):
    v_magnitudes_dict[node] = m.addVar(lb=0, ub=1.5, name=f'v_magnitude_{node}')
    m.update()

# 3.3.2. Voltage Angle Constraints
v_angles_dict = {}  # Dictionary zur Speicherung der Variablen pro Knoten
for i, node in enumerate(all_nodes):
    v_angles_dict[node] = m.addVar(lb=-math.pi, ub=math.pi, name=f'v_angle_{node}')
    m.update()

# 3.3.3. Power Balance Constraints
p_i = active_power_i 
q_i = reactive_power_i 
for i in range(len(all_nodes)):
    for j in range(len(all_nodes)):
        if i != j and i < len(all_nodes) and j < len(all_nodes):
            pi[i] <= active_power_i[i] - active_power_i[j] - b_cap[i][j] * (v_angles[i] - v_angles[j])
            delta_q_ij = reactive_power_i[i] - reactive_power_i[j] + G * (v_angles[i] - v_angles[j])
            m.addConstr(p_i[i] - p_i[j] == delta_p_ij, name=f'delta_p_{i}_{j}')
            m.addConstr(q_i[i] - q_i[j] == delta_q_ij, name=f'delta_q_{i}_{j}')

