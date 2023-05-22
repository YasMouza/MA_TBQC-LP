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

#1.1 Grid parameters
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

# 2.1. Linear Approximation of cos(theta)
def linear_approximation_cos(theta):
    # Bereiche für die lineare Approximation
    intervals = [0, math.pi/6, math.pi/3, math.pi/2, 2*math.pi/3, 5*math.pi/6, math.pi]

    # Hilfsvariablen für die lineare Approximation
    a_values = [1, 1/2, 0, -1/2, -1, -1/2, 0]
    b_values = [0, math.sqrt(3)/2, 1, math.sqrt(3)/2, 0, -math.sqrt(3)/2, -1]

    # Lineare Approximation in den Bereichen
    for i in range(len(intervals)-1):
        if intervals[i] <= theta <= intervals[i+1]:
            a = a_values[i]
            b = b_values[i]
            break
    
    # Hilfsvariable z berechnen
    z = a * theta + b
    
    return z


#3. Linear Program by Gurobipy 
m = gp.Model('Cold-Start-AC-Load-Flow')
# 3.1.  Define Variables
theta = m.addVar(lb=0, ub=math.pi, name='theta')
z = {}
sections = 7  # Anzahl der Abschnitte
for i in range(sections):
    z[i] = m.addVar(vtype=GRB.CONTINUOUS, lb=-1, ub=1, name=f'z{i+1}')

# Constraints definieren
section_angles = [math.pi/sections * i for i in range(sections)]
for i in range(sections):
    m.addConstr(z[i] >= math.cos(section_angles[i]) * theta, name=f'constraint{i+1}')


# Maximierungsfunktion definieren
m.setObjective(gp.quicksum(z[i] for i in range(sections)), GRB.MAXIMIZE)

num_nodes = len(all_nodes)
num_lines = len(line_all)

v_magnitudes = m.addVars(range(num_nodes), lb=0, ub=1.5, name='v_magnitude')
theta = m.addVars(range(2), lb=-math.pi, ub=math.pi, name='theta')


# 3.3. Define Constraints
# 3.3.1. Voltage Magnitude Constraints
v_magnitudes_dict = {}  # Dictionary zur Speicherung der Variablen pro Knoten
for i, node in enumerate(all_nodes):
    v_magnitudes_dict[node] = m.addVar(lb=0, ub=1.5, name=f'v_magnitude_{node}')
    m.update()

# # 3.3.2. Voltage Angle Constraints
# theta = {}  # Dictionary zur Speicherung der Variablen pro Knoten
# for i, node in enumerate(all_nodes):
#     theta[node] = m.addVar(lb=-math.pi, ub=math.pi, name=f'v_angle_{node}')
#     m.update()

# 3.3.3. Power Balance Constraints
p_i = [50,50] 
q_i = [100,100] 
p_j = [-50,50] 
q_j = [-100,-100] 
all_nodes = 2
b_cap = [125,125]
for i in range(all_nodes):
    for j in range(2):
        m.addConstr(b_cap[i] * (theta[i] - theta[j]) <= p_i[i]/100)
        m.addConstr(-b_cap[i] + b_cap[i] * z[i] <= q_i[i]/100)



# 3.3.4 voltage angle difference constraints
for i in range(2):
    for j in range(2):
        if i != j:
            m.addConstr(theta[i] - theta[j] <= 2*math.pi)
            m.addConstr(theta[i] - theta[j] >= -2*math.pi)
                
# # 3.3.5. Voltage Magnitude Constraints
# for i, line in enumerate(line_all):
#     m.addConstr(v_magnitudes[line.bus1.cterm] - v_magnitudes[line.bus2.cterm] <= 0.1)
#     m.addConstr(v_magnitudes[line.bus1.cterm] - v_magnitudes[line.bus2.cterm] >= -0.1)
#     m.update()

# write model to file
m.write('overview_constraints.lp')

# result of the optimization problem
m.optimize()

# print the optimal solution
for v in m.getVars():
    print('%s %g' % (v.varName, v.x))
    
test = 1
            

# for i in range(len(all_nodes)):
#     p_sum = 0
#     q_sum = 0
#     for j in range(len(all_nodes)):
#         if i != j:
#             p_sum += p_i[j] * gp.cos(v_angles[i] - v_angles[j]) - q_i[j] * gp.sin(v_angles[i] - v_angles[j]) - B_cap[i][j] * (v_magnitudes[i] ** 2 - v_magnitudes[i] * v_magnitudes[j])
#             q_sum += p_i[j] * gp.sin(v_angles[i] - v_angles[j]) + q_i[j] * gp.cos(v_angles[i] - v_angles[j]) + G[i][j] * (v_magnitudes[i] ** 2 - v_magnitudes[i] * v_magnitudes[j])
#     m.addConstr(p_i[i] >= p_sum)
#     m.addConstr(q_i[i] >= q_sum)

# # 3.3.4. Voltage Angle Difference Constraints
# for i in range(len(all_nodes)):
#     for j in range(len(all_nodes)):
#         if i != j:
#             m.addConstr(v_magnitudes[i] ** 2 >= v_magnitudes[i] * v_magnitudes[j])

# # 3.3.5. Voltage Angle Difference Constraints
# for i, j in direct_connections:
#     m.addConstr(v_angles[i] - v_angles[j] == 0)

# # 3.3.6. Voltage Magnitude Constraints
# for i in range(len(all_nodes)):
#     m.addConstr(v_magnitudes[i] >= v_min)
#     m.addConstr(v_magnitudes[i] <= v_max)

# # 3.3.7. Voltage Angle Constraints
# for i in range(len(all_nodes)):
#     m.addConstr(v_angles[i] >= -gp.pi)
#     m.addConstr(v_angles[i] <= gp.pi)


