import numpy as np
import pandas as pd
from main_powerfactory import PowerFactory
from loadflow import LoadFlow
import math as m

# def calculate_static_generator_q(V1, V2, load_p, load_q, sgen_p, X, Zbase):
#     return (V1 - V2) * (load_p / V1) + load_q - (sgen_p * (X / Zbase) / V1)

def calculate_static_generator_q(V1, V2, load_p, sgen_p, load_q, xpu, Zbase):
    if load_p != 0:
        return  V2**2*xpu + V1*V2*xpu +1/load_p + load_q
    else:
        return V2**2*xpu + V1*V2*xpu + load_q

# 1. ACloadflow
path = r'C:\Program Files\DIgSILENT\PowerFactory 2023 SP3A\Python\3.9'
pf = PowerFactory(path)
project_name = 'TBQC'
app = pf.open_app(project_name)
ldf_ac = LoadFlow(app)
ldf_ac.run()

# 1.2 Line parameters
line_all = app.GetCalcRelevantObjects('*.ElmLne')
X = []
xpu = []
for line in line_all:
    X.append(line.GetAttribute('t:xline'))
    xpu.append(line.GetAttribute('e:xSbasepu'))
X = np.around(X, 3)
X = np.array(X)
xpu = np.array(xpu)

# 1.3 Bus parameters
bus_all = app.GetCalcRelevantObjects('*.ElmTerm')
bus1 = bus_all[0]
bus2 = bus_all[1]
V1 = bus1.GetAttribute('m:u')
V2 = bus2.GetAttribute('m:u')

# 1.4 Generator parameters
gen_all = app.GetCalcRelevantObjects('*.ElmGenstat')

# 1.5 Load parameters
load_all = app.GetCalcRelevantObjects('*.ElmLod')
load_p = []
load_q = []
for load in load_all:
    load_p.append(load.GetAttribute('m:P:bus1'))
    load_q.append(load.GetAttribute('m:Q:bus1'))
load_p = np.array(load_p)
load_q = np.array(load_q)

# 1.6 static generator parameters
sgen_all = app.GetCalcRelevantObjects('*.ElmGenstat')
sgen_p = []
for sgen in sgen_all:
    sgen_p.append(sgen.GetAttribute('m:P:bus1'))
sgen_p = np.array(sgen_p)

# Set static generator P and Q
for sgen in sgen_all:
    sgen.P = 20
    #sgen.Q = 20

# Define Zbase
Sbase = 100
Zbase = 400e3**2/Sbase

# Define load conditions from 5 cases
load_conditions = [
    {'p': 0, 'q': -150},
    {'p': 0, 'q': 150},
    {'p': 50, 'q': 0},
    {'p': 50, 'q': -150},
    {'p': 50, 'q': 150}
]

sgen_q_calc = []
sgen_q_pf = [] 
for condition in load_conditions:
    # Set load P and Q
    for load in load_all:
        load.plini = condition['p']
        load.qlini = condition['q']

    # Run load flow
    ldf_ac.run()

    # Get load P and Q after load flow
    load_p = []
    load_q = []
    for load in load_all:
        load_p.append(load.GetAttribute('m:P:bus1'))
        load_q.append(load.GetAttribute('m:Q:bus1'))
    load_p = np.array(load_p)
    load_q = np.array(load_q)
    
    for sgen in sgen_all:
        sgen_q_pf.append(sgen.GetAttribute('m:Q:bus1'))

    # Calculate static generator Q
    # Q_gen_calc = calculate_static_generator_q(V1, V2, load_p, load_q, sgen_p, X, Zbase)
    # sgen_q_calc.append(Q_gen_calc)
    
    Q_gen_calc = calculate_static_generator_q(V1, V2, load_p, sgen_p, load_q, xpu, Zbase)
    sgen_q_calc.append(Q_gen_calc)
    



# Create DataFrame for results of static generator Q
sgen_q_calc = pd.DataFrame(sgen_q_calc, columns=['Berechnete Werte von Sgen_Q'])
sgen_q_calc.index = ['Case 1', 'Case 2', 'Case 3', 'Case 4', 'Case 5']
print(sgen_q_calc)

sgen_q_pf = pd.DataFrame(sgen_q_pf, columns=['Sgen_Q Werte aus PowerFactory'])
sgen_q_pf.index = ['Case 1', 'Case 2', 'Case 3', 'Case 4', 'Case 5']
print(sgen_q_pf)