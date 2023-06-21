import sys 
sys.path.append('C:\\Users\\yasin\\source\\MA_TBQC LP')
from main_powerfactory import PowerFactory
from loadflow import LoadFlow
import math as m
import numpy as np
import pandas as pd

from main_powerfactory import PowerFactory
from loadflow import LoadFlow

    

def calculate_shunt_compensation(load_q, xpu, Sbase, shunt_q_1, load_p):
    if load_p != 0:
        if load_q <= 0:
            return (- load_q - shunt_q_1)
        elif load_q > 0:
            return  -(load_q + shunt_q_1) 
    elif load_p == 0:
        if load_q <= 0:
            return (- load_q - shunt_q_1)
        elif load_q > 0:
            return  -(load_q + shunt_q_1) 
    

    
path = r'C:\Program Files\DIgSILENT\PowerFactory 2023 SP3A\Python\3.9'
pf = PowerFactory(path)
project_name = 'TBQC - Shunt Capacitor compensation'
app = pf.open_app(project_name)
ldf_ac = LoadFlow(app)
#ldf_ac.run()
ldf_ac.iopt_pq = 1


### 1. Get parameters
# 1.1 Line parameters
line_all = app.GetCalcRelevantObjects('*.ElmLne')
X = []
xpu = []
for line in line_all:
    X.append(line.GetAttribute('t:xline'))
    xpu.append(line.GetAttribute('e:xSbasepu'))
X = np.around(X, 3)
X = np.array(X)
xpu = np.array(xpu)

# 1.2 Bus parameters
bus_all = app.GetCalcRelevantObjects('*.ElmTerm')
bus1 = bus_all[0]
bus2 = bus_all[1]


# 1.3 Generator parameters
gen_all = app.GetCalcRelevantObjects('*.ElmGenstat')

# 1.4 Load parameters
load_all = app.GetCalcRelevantObjects('*.ElmLod')

# 1.5 shunt compensation parameters
shunt_all = app.GetCalcRelevantObjects('*.ElmShnt')
shunt2 = shunt_all[0]
shunt1 = shunt_all[1]
print('Shunt 1 = ',shunt1.loc_name)
shunt2.qs = 100.0
shunt2.iopt_save = 1
print(shunt2.qcapn)
print('Shunt2 = ',shunt2.loc_name)
test = 1
shunt_q_1 = -100
Sbase = 100
Zbase = 400e3**2/Sbase

shunt_q_calc_values = []
# Define load conditions from 5 cases
load_conditions = [
    {'p': 0, 'q': -150}, # L erf (1)
    {'p': 0, 'q': 150}, # C erf (2)
    {'p': 50, 'q': 0}, # L erf (1)
    {'p': 50, 'q': -150}, # L erf (1)
    {'p': 50, 'q': 150} # C erf (2)
]

shunt_q_values = [] 
for condition in load_conditions:
    load_p = condition['p']
    load_q = condition['q']
    load_p = np.array(load_p)
    load_q = np.array(load_q)
    
    shunt_q_calc = calculate_shunt_compensation(load_q, xpu, Sbase, shunt_q_1, load_p)    
    shunt_q_calc_values.append(shunt_q_calc)
        

print(shunt_q_calc_values)
# Convert all negative values in shunt_q_calc_values to positive because shunt.qcapn only accepts positive values
shunt_q_calc_values = [abs(value) for value in shunt_q_calc_values]

############ 2. Set parameters and run load flow  ############

# Create a list to store the voltage results
voltage_results = []
# Iterate over the calculated shunt values and load conditions
for i, (shunt_q_calc, condition) in enumerate(zip(shunt_q_calc_values, load_conditions)):
    # Get the load_q from the condition
    load_q = condition['q']
    
    # Set the shunt type based on the load_q
    if load_q <= 0:
        shunt1.shtype = 1  # Inductive
        shunt1.qrean = float(shunt_q_calc)
    else:
        shunt1.shtype = 2  # Capacitive
        shunt1.qcapn = float(shunt_q_calc)

    # Set the reactive power
    
    load_all[0].qlini = load_q
    print(shunt1.qcapn)
    print(shunt1.qrean)
    # Run the load flow calculation
    ldf_ac.run()
    ldf_ac.iopt_pq = 1
    
    # Get the voltage at bus 2
    voltage = bus2.GetAttribute('m:u')
    
    # Append the voltage to the results list
    voltage_results.append(voltage)

# Convert the results to a pandas DataFrame
df = pd.DataFrame(voltage_results, columns=['Voltage'])

# Print the DataFrame
print(df)