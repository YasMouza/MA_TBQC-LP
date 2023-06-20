import sys 
sys.path.append('C:\\Users\\yasin\\source\\MA_TBQC LP')
from main_powerfactory import PowerFactory
from loadflow import LoadFlow
import math as m
import numpy as np
import pandas as pd

from main_powerfactory import PowerFactory
from loadflow import LoadFlow

# def calculate_shunt_compensation(V1, V2, load_p, load_q, xpu, Zbase, shunt_q_1):
#     if load_p != 0:
#         return  V2**2*xpu + V1*V2*xpu - 1/load_p + load_q - shunt_q_1  
#     else:
#         return V2**2*xpu + V1*V2*xpu + load_q - shunt_q_1
    

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
shunt_all[0].qcapn = 100
shunt2 = shunt_all[1]

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
        shunt2.shtype = 1  # Inductive
    else:
        shunt2.shtype = 2  # Capacitive

    # Set the reactive power
    shunt2.qcapn = float(shunt_q_calc)
    load_all[0].qlini = load_q
    
    # Run the load flow calculation
    ldf_ac.run()

    # Get the voltage at bus 2
    voltage = bus2.GetAttribute('m:u')
    
    # Append the voltage to the results list
    voltage_results.append(voltage)

# Convert the results to a pandas DataFrame
df = pd.DataFrame(voltage_results, columns=['Voltage'])

# Print the DataFrame
print(df)