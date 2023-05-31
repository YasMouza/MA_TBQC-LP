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

#### Q von statischen Generatoren anpassen 

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
bus2 = bus_all[1]
V1 = bus1.GetAttribute('m:u')
V2 = bus2.GetAttribute('m:u')

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
print('LOAD DF', load_df)
load_q = np.asarray(load_q)
load_p = np.asarray(load_p)

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
print('SGEN DF', sgen_df)
sgen_p = np.asarray(sgen_p)

# set sgen_p and sgen_q to 20 MW 
# set attribute of sgen to 20 MW
for sgen in sgen_all:
    sgen.P = 20
    sgen.Q = 20
print('SGEN_DF', sgen_df)  


# 2.1 case 1: load_p = 0, load_q = -150
for load in load_all:
    load.plini = 0
    load.qlini = -150

#ac loadflow
ldf_ac.run()
   
# get load_p and load_q
load_p = []
load_q = []
for load in load_all:
    load_p.append(load.GetAttribute('m:P:bus1'))
    load_q.append(load.GetAttribute('m:Q:bus1'))
    load_p = np.asarray(load_p)
    load_q = np.asarray(load_q)

test = 1

# 2.1.2 Berechnung der Blindleistung des statischen Generators
Q_gen_calc_1 = (V1 - V2) * (load_p / V1) + load_q - (sgen_p * (X/Sbase) / V1)
print("Blindleistung des statischen Generators Case 1:", Q_gen_calc_1, "MVAr") 

# 2.2 case 2: load_p = 0, load_q = 150
for load in load_all:
    load.plini = 0
    load.qlini = 150
    
#ac loadflow
ldf_ac.run()

load_p = []
load_q = []
for load in load_all:
    load_p.append(load.GetAttribute('m:P:bus1'))
    load_q.append(load.GetAttribute('m:Q:bus1'))
    load_p = np.asarray(load_p)
    load_q = np.asarray(load_q)
    
# 2.2.2 Berechnung der Blindleistung des statischen Generators
Q_gen_calc_2 = (V1 - V2) * (load_p / V1) + load_q - (sgen_p * (X/Sbase) / V1)
print("Blindleistung des statischen Generators Case 2:", Q_gen_calc_2, "MVAr")
#ac loadflow
ldf_ac.run()

# 2.3 case 3: load_p = 50, load_q = 0
for load in load_all:
    load.plini = 50
    load.qlini = 0
    
#ac loadflow
ldf_ac.run()

load_p = []
load_q = []
for load in load_all:
    load_p.append(load.GetAttribute('m:P:bus1'))
    load_q.append(load.GetAttribute('m:Q:bus1'))
    load_p = np.asarray(load_p)
    load_q = np.asarray(load_q)
    


# 2.3.2 Berechnung der Blindleistung des statischen Generators
Q_gen_calc_3 = (V1 - V2) * (load_p / V1) + load_q - (sgen_p * (X/Sbase) / V1)
print("Blindleistung des statischen Generators Case 3:", Q_gen_calc_3, "MVAr")


# 2.4 case 4: load_p = 50, load_q = -150
for load in load_all:
    load.plini = 50
    load.qlini = -150

#ac loadflow
ldf_ac.run()

load_p = []
load_q = []
for load in load_all:
    load_p.append(load.GetAttribute('m:P:bus1'))
    load_q.append(load.GetAttribute('m:Q:bus1'))
    load_p = np.asarray(load_p)
    load_q = np.asarray(load_q)
    
    
# 2.4.2 Berechnung der Blindleistung des statischen Generators
Q_gen_calc_4 = (V1 - V2) * (load_p / V1) + load_q - (sgen_p * (X/Sbase) / V1)
print("Blindleistung des statischen Generators Case 4:", Q_gen_calc_4, "MVAr")


# 2.5 case 5: load_p = 50, load_q = 150
for load in load_all:
    load.plini = 50
    load.qlini = 150
    
#ac loadflow
ldf_ac.run()

load_p = []
load_q = []
for load in load_all:
    load_p.append(load.GetAttribute('m:P:bus1'))
    load_q.append(load.GetAttribute('m:Q:bus1'))
    load_p = np.asarray(load_p)
    load_q = np.asarray(load_q)
    

# 2.5.2 Berechnung der Blindleistung des statischen Generators
Q_gen_calc_5 = (V1 - V2) * (load_p / V1) + load_q - (sgen_p * (X/Sbase) / V1)
print("Blindleistung des statischen Generators Case 5:", Q_gen_calc_5, "MVAr")

#create Dataframe for results of static generator Q 
sgen_q_calc = [Q_gen_calc_1, Q_gen_calc_2, Q_gen_calc_3, Q_gen_calc_4, Q_gen_calc_5]
sgen_q_calc = pd.DataFrame(sgen_q_calc)
sgen_q_calc.columns = ['Q_gen_calc']
sgen_q_calc.index = ['Case 1', 'Case 2', 'Case 3', 'Case 4', 'Case 5']
print(sgen_q_calc)

# plot a graph for the results of static generator Q 
sgen_q_calc.plot(kind='bar', title='Static Generator Q', xlabel='Case', ylabel='Q [MVAr]') 
#add information of p and q of load to x axis
plt.xticks(np.arange(5), ('Case 1\np=0\nq=-150', 'Case 2\np=0\nq=150', 'Case 3\np=50\nq=0', 'Case 4\np=50\nq=-150', 'Case 5\np=50\nq=150'))
plt.show()

test = 1

