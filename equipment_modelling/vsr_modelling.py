import sys 
sys.path.append('C:\\Users\\yasin\\source\\MA_TBQC LP')
from main_powerfactory import PowerFactory
from loadflow import LoadFlow
import math
import numpy as np
import pandas as pd

from main_powerfactory import PowerFactory
from loadflow import LoadFlow

path = r'C:\Program Files\DIgSILENT\PowerFactory 2023 SP3A\Python\3.9'
pf = PowerFactory(path)
project_name = '[MA] Equipment Modelling - VSR'
app = pf.open_app(project_name)
ldf_ac = LoadFlow(app)
#ldf_ac.run()
ldf_ac.iopt_pq = 1

bus1 = app.GetCalcRelevantObjects('*.ElmTerm')[1]
bus2 = app.GetCalcRelevantObjects('*.ElmTerm')[0]
load = app.GetCalcRelevantObjects('*.ElmLod')[0]
reactor = app.GetCalcRelevantObjects('*.ElmShnt')[0]
line = app.GetCalcRelevantObjects('*.ElmLne')[0]

#1. Set Load parameters
load.SetAttribute('plini', 0) 
load.SetAttribute('qlini', -600) 
load_q = load.qlini 

#2. Set Shunt parameters
reactor.SetAttribute('qrean', 30) # reactive power in MVAr per step 
reactor.SetAttribute('ncapx', 25) # max. number of steps 

#2.1 Set Shunt Controller
# Run Load Flow and adjust the number of steps
target_voltage = 1.0
tolerance = 0.01
max_steps = reactor.GetAttribute('ncapx')
reactive_power_per_step = reactor.GetAttribute('qrean')

# Initial number of steps
current_steps = 0

while True:
    # Set the number of steps
    reactor.SetAttribute('ncapa', current_steps)

    # Run the load flow calculation
    ldf_ac.run()
    ldf_ac.iopt_asht = 0  # 0 = no automatic switching of shunt elements

    # Reactive power of Load and Shunt
    reactor_q = reactor.GetAttribute('Qact')
    compare_q = abs(load_q) - reactor_q
    print(compare_q)

    # Get the voltage at bus 2
    voltage_at_bus2 = bus2.GetAttribute('m:u')
    print(voltage_at_bus2)

    # Check if the voltage at bus 2 is within the desired range
    if abs(voltage_at_bus2 - target_voltage) <= tolerance:
        print(f"Number of steps required for compensation: {current_steps}")
        print(f"Voltage at Bus 2: {voltage_at_bus2} p.u.")
        break

    # Increment the number of steps
    current_steps += 1

    # Check if the maximum number of steps is reached
    if current_steps > max_steps:
        print("Unable to reach the desired voltage with the available number of steps.")
        break