import numpy as np 
import pandas as pd
import math as m 
from main_powerfactory import PowerFactory
from loadflow import LoadFlow
import matplotlib.pyplot as plt

# 1. ACloadflow
path = r'C:\Program Files\DIgSILENT\PowerFactory 2023 SP3A\Python\3.9'
pf = PowerFactory(path)
project_name = 'TBQC'
app = pf.open_app(project_name)
ldf_ac = LoadFlow(app)
ldf_ac.run()

# 1 Grid parameters
Sbase = 100

# 1.2 Line parameters
line_all = app.GetCalcRelevantObjects('*.ElmLne')
# get reactance X from line 
X = []
for line in line_all:
    X.append(line.GetAttribute('t:xline'))
X = np.array(X)
# 1.3 Bus parameters
bus_all = app.GetCalcRelevantObjects('*.ElmTerm')
bus1 = bus_all[0]
V1 = bus1.GetAttribute('m:u')
# 1.4 Generator parameters
gen_all = app.GetCalcRelevantObjects('*.ElmGenstat')
# 1.5 Load parameters
load_all = app.GetCalcRelevantObjects('*.ElmLod')
load_names = []
load_p = []
load_q = []
for load in load_all:
    load_names.append(load.loc_name)
    load_p.append(load.GetAttribute('m:P:bus1'))
    load_q.append(load.GetAttribute('m:Q:bus1'))
load_df = pd.DataFrame({'name': load_names, 'p': load_p, 'q': load_q})
load_df = load_df.set_index('name')
print(load_df)

# 1.6 static generator parameters
sgen_all = app.GetCalcRelevantObjects('*.ElmGenstat')
sgen_names = []
sgen_p = []
sgen_q = []
for sgen in sgen_all:
    sgen_names.append(sgen.loc_name)
    sgen_p.append(sgen.GetAttribute('m:P:bus1'))
    sgen_q.append(sgen.GetAttribute('m:Q:bus1'))
sgen_df = pd.DataFrame({'name': sgen_names, 'p': sgen_p, 'q': sgen_q})
sgen_df = sgen_df.set_index('name')
print(sgen_df)

# set sgen_p and sgen_q to 20 MW 
# set attribute of sgen to 20 MW
print(sgen_all[0].loc_name)

for sgen in sgen_all:
    sgen.P = 20
    sgen.Q = 20
print(sgen_df)  


# 2. Cases to be solved
# 2.a) Pload = 0 MW, Qload = -150 MVar
# set load_p and load_q to 0
for load in load_all:
    load.P = 0
    load.Q = -150
load_df = pd.DataFrame({'name': load_names, 'p': load_p, 'q': load_q})
load_df = load_df.set_index('name')
print(load_df)

# get P + jQ on busbar 2 (busbar 1 is slack bus)
bus2 = app.GetCalcRelevantObjects('*.ElmTerm')
bus2 = bus2[1]
bus2_p = bus2.GetAttribute('m:Pflow')
bus2_q = bus2.GetAttribute('m:Qflow')
print(bus2_p, bus2_q)

# Carry out loadflow
ldf_ac.run()

# 2.b) Pload = 0 MW, Qload = -150 MVar
for load in load_all:
    load.P = 0
    load.Q = -150
load_df_a = pd.DataFrame({'name': load_names, 'p': load_p, 'q': load_q})
load_df_a = load_df_a.set_index('name')
print(load_df_a)

# Carry out Loadflow calculation
V2 = V1 - (complex(bus2_p/Sbase, bus2_q/Sbase) / V1) * X/Sbase
print(V2)

# convert to polar coordinates 
V2_mag = np.abs(V2)
V2_ang = np.angle(V2)
print(V2_mag, V2_ang)

# Carry out loadflow
ldf_ac.run()

# 2.b) Pload = 0 MW, Qload = 150 MVar
for load in load_all:
    load.P = 0
    load.Q = -150
load_df_b = pd.DataFrame({'name': load_names, 'p': load_p, 'q': load_q})
load_df_b = load_df_b.set_index('name')
print(load_df_b)

# Carry out Loadflow calculation
V2 = V1 - (complex(bus2_p/Sbase, bus2_q/Sbase) / V1) * X/Sbase
print(V2)

# convert to polar coordinates 
V2_mag = np.abs(V2)
V2_ang = np.angle(V2)
print(V2_mag, V2_ang)

# Carry out loadflow
ldf_ac.run()

# 2.c) Pload = 50 MW, Qload = 0 MVar
for load in load_all:
    load.P = 0
    load.Q = -150
load_df_c = pd.DataFrame({'name': load_names, 'p': load_p, 'q': load_q})
load_df_c = load_df_c.set_index('name')
print(load_df_c)

# Carry out Loadflow calculation
V2 = V1 - (complex(bus2_p/Sbase, bus2_q/Sbase) / V1) * X/Sbase
print(V2)

# convert to polar coordinates 
V2_mag = np.abs(V2)
V2_ang = np.angle(V2)
print(V2_mag, V2_ang)

# Carry out loadflow
ldf_ac.run()

# 2.d) Pload = 50 MW, Qload = -150 MVar
for load in load_all:
    load.P = 0
    load.Q = -150
load_df_d = pd.DataFrame({'name': load_names, 'p': load_p, 'q': load_q})
load_df_d = load_df_d.set_index('name')
print(load_df_d)

# Carry out Loadflow calculation
V2 = V1 - (complex(bus2_p/Sbase, bus2_q/Sbase) / V1) * X/Sbase
print(V2)

# convert to polar coordinates 
V2_mag = np.abs(V2)
V2_ang = np.angle(V2)
print(V2_mag, V2_ang)

# 2.e) Pload = 50 MW, Qload = 150 MVar
for load in load_all:
    load.P = 0
    load.Q = -150
load_df_e = pd.DataFrame({'name': load_names, 'p': load_p, 'q': load_q})
load_df_e = load_df_e.set_index('name')
print(load_df_e)

# Carry out loadflow
ldf_ac.run()

# Carry out Loadflow calculation
V2 = V1 - (complex(bus2_p/Sbase, bus2_q/Sbase) / V1) * X/Sbase
print(V2)

# convert to polar coordinates 
V2_mag = np.abs(V2)
V2_ang = np.angle(V2)
print(V2_mag, V2_ang)

#save the results of all cases in a dataframe 
load_df = pd.DataFrame({'name': load_names, 'p': load_p, 'q': load_q})
load_df = load_df.set_index('name')
print(load_df)

# dataframe of sgen of all cases a to e 
sgen_df = pd.DataFrame({'name': sgen_names, 'p': sgen_p, 'q': sgen_q})
sgen_df = sgen_df.set_index('name')
print(sgen_df)




test = 1