
import numpy as np
import pandas as pd 
import sys
sys.path.append('C:\\Users\\yasin\\source\\MA_TBQC LP')
from main_powerfactory import PowerFactory
from loadflow import LoadFlow
import math as m

def calculate_static_generator_q(V1, V2, load_p, load_q, xpu, Zbase):
    if load_p != 0:
        return  V2**2*xpu + V1*V2*xpu + 1/load_p + load_q
    else:
        return V2**2*xpu + V1*V2*xpu + load_q

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

# 1.6 shunt compensation parameters
shunt_all = app.GetCalcRelevantObjects('*.ElmShnt')
shunt_q = []
for shunt in shunt_all:
    shunt_q.append(shunt.GetAttribute('m:Q:bus1'))
shunt_q = np.array(shunt_q)

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

shunt_q_pf = []
shunt_q_calc = []
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
    
    for shunt in shunt_all:
        shunt_q_pf.append(shunt.GetAttribute('m:Q:bus1'))

    
    Q_gen_calc = calculate_static_generator_q(V1, V2, load_p, load_q, xpu, Zbase)
    shunt_q_calc.append(Q_gen_calc)

# Create DataFrame for results of static generator Q
shunt_q_calc = pd.DataFrame(shunt_q_calc, columns=['Berechnete Werte von Sgen_Q'])
shunt_q_calc.index = ['Case 1', 'Case 2', 'Case 3', 'Case 4', 'Case 5']
print(shunt_q_calc)

shunt_q_pf = pd.DataFrame(shunt_q_pf, columns=['Sgen_Q Werte aus PowerFactory'])
shunt_q_pf.index = ['Case 1', 'Case 2', 'Case 3', 'Case 4', 'Case 5']
print(shunt_q_pf)
