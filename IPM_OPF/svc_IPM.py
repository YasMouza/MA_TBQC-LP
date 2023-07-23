import sys 
sys.path.append('C:\\Users\\yasin\\source\\MA_TBQC LP')
from main_powerfactory import PowerFactory
from loadflow import LoadFlow
import math 
import numpy as np
import pandas as pd
import gurobipy as gp
from gurobipy import GRB

from main_powerfactory import PowerFactory
from loadflow import LoadFlow

path = r'C:\Program Files\DIgSILENT\PowerFactory 2023 SP3A\Python\3.9'
pf = PowerFactory(path)
project_name = '[MA] Equipment Modelling - SVC'
app = pf.open_app(project_name)
ldf_ac = LoadFlow(app)
#ldf_ac.run()
ldf_ac.iopt_pq = 1

#### 1. GET GRID-VARIABLES 
n_buses = 2
P_load = [0, -1]  # Active power load at each bus
Q_load = [0, -0.5]  # Reactive power load at each bus
X = [[0, 12.8], [12.8, 0]]  # Reactance matrix
R = [[0, 0], [0, 0]] 

B = [[1 / element if element != 0 else 0 for element in row] for row in X]

G = [[0, 0], [0, 0]] 


#### 2. CREATE MODEL
model = gp.Model("ACLoadFlow")

### 2.1 CREATE VARIABLES
V = model.addVars(n_buses, lb=0.9, ub=1.1, name="V")  # Voltage magnitudes
theta = model.addVars(n_buses, lb=-math.pi, ub=math.pi, name="theta")  # Voltage angles
k = model.addVar(lb=1, ub=10, vtype=GRB.INTEGER, name="k")

mu = 0.1 ### Barrier parameter

### 2.1 ADD CONSTRAINTS 
## 2.1.1 Add power flow constraints for each bus
for i in range(n_buses):
    for j in range(n_buses):
        cos_theta = model.addVar(lb=-1, ub=1, name=f"cos_theta_{i}_{j}")
        sin_theta = model.addVar(lb=-1, ub=1, name=f"sin_theta_{i}_{j}")
        theta_diff = model.addVar(lb=-GRB.INFINITY, ub=GRB.INFINITY, name=f"theta_diff_{i}_{j}")
        V_product = model.addVar(lb=0, ub=GRB.INFINITY, name=f"V_product_{i}_{j}")

        # Define the difference theta[i] - theta[j]
        model.addConstr(theta_diff == theta[i] - theta[j])

        # Add the trigonometric constraints
        model.addGenConstrSin(sin_theta, theta_diff)
        model.addGenConstrCos(cos_theta, theta_diff)

        model.addConstr(
            V_product * ((G[i][j] * cos_theta + B[i][j] * sin_theta)) - P_load[i] == 0,
            name=f"P_balance_bus_{i}"
        )
        model.addConstr(
            V_product * ((G[i][j] * sin_theta + B[i][j] * cos_theta))  - Q_load[i] == 0,
            name=f"Q_balance_bus_{i}"
        )
    
## 2.1.2 Add single argument constraints 


### 2.2 SOLVE MODEL 
# Define the objective function (example: maximize voltage at bus 2)
model.setObjective(V[1], GRB.MAXIMIZE)
# minimiere delta V

# Set the optimization method to Interior-Point
model.Params.Method = 2
model.write('SVC_modelling.lp')
# Solve the model
model.optimize()

# Display the results
for v in model.getVars():
    print(f"{v.varName} = {v.x}")

# Display the optimal objective value
print(f"Optimal Objective: {model.objVal}")
