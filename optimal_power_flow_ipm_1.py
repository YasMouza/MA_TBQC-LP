import numpy as np
import math
import gurobipy as gp
from gurobipy import GRB

#### 1. GET GRID-VARIABLES 
n_buses = 2
P_load = [-0.4, -2]  # Active power load at each bus
Q_load = [-6.9, -2.8]  # Reactive power load at each bus
X = [[0, 12.8], [12.8, 0]]  # Reactance matrix
R = [[0, 0], [0, 0]] 

B = [[1 / element**2 if element != 0 else 0 for element in row] for row in X] 
G = [[0, 0], [0, 0]] 

#### 2. CREATE MODEL
model = gp.Model("optimal_power_flow")
model.params.NonConvex = 2
model.params.Method = 2

### 2.1 CREATE VARIABLES
V = model.addVars(n_buses, lb=0.9, ub=1.1, name="V")  # Voltage magnitudes
theta = model.addVars(n_buses, lb=-math.pi, ub=math.pi, name="theta")  # Voltage angles
k = model.addVar(lb=1, ub=6, vtype=GRB.INTEGER, name="k")  # Integer variable

# Define auxiliary variables for the trigonometric functions
cos_theta_diff = model.addVar(lb=-1, ub=1, name="cos_theta_diff")
sin_theta_diff = model.addVar(lb=-1, ub=1, name="sin_theta_diff")
# Define the difference theta[0] - theta[1]
theta_diff = model.addVar(lb=-GRB.INFINITY, ub=GRB.INFINITY, name="theta_diff")
model.addConstr(theta_diff == theta[0] - theta[1])
# Add the trigonometric constraint
model.addGenConstrCos(cos_theta_diff, theta_diff)
model.addGenConstrSin(sin_theta_diff, theta_diff)

# Define an auxiliary variable for the product V[0] * V[1]
V_product = model.addVar(lb=0, ub=GRB.INFINITY, name="V_product")
model.addConstr(V_product == V[0] * V[1])

# Intermediate variable for quadratic product
quad_intermediate = model.addVar(lb=-GRB.INFINITY, ub=GRB.INFINITY, name="quad_intermediate")
model.addConstr(quad_intermediate == V_product * (B[1][0] * sin_theta_diff))

p1 = P_load[0]
p2 = P_load[1]
q1 = Q_load[0]
q2 = Q_load[1]

### 2.1 ADD CONSTRAINTS
model.addConstr(V[0] == 1, name="slack_bus")
model.addConstr(theta[0] == 0, name="slack_bus_angle")

# Add the power flow constraints
model.addConstr(p1 - V_product * (B[0][1] * cos_theta_diff) <= 0, name="p1")
model.addConstr(q1 - V_product * (B[0][1] * sin_theta_diff) <= 0, name="q1")
model.addConstr(p2 - V_product * (B[1][0] * cos_theta_diff) <= 0, name="p2")
model.addConstr(k * (q2 - quad_intermediate) <= 0, name="q2")

# Here, you would typically set the objective and solve the model
# For example:
# Define the absolute difference between V[1] and 1 using two additional variables
delta_plus = model.addVar(lb=0, name="delta_plus")
delta_minus = model.addVar(lb=0, name="delta_minus")

model.addConstr(V[1] - 1 <= delta_plus)
model.addConstr(1 - V[1] <= delta_minus)

model.setObjectiveN(delta_plus + delta_minus, 0, priority=1, weight=1, name="PrimaryObj")
#model.setObjectiveN(delta_plus, 0, priority=1, weight=1, name="PrimaryObj")
#model.setObjectiveN(V[1], 0, priority=1, weight=-1, name="PrimaryObj")
# Secondary objective: Minimize k as much as possible
#model.setObjectiveN(k, 1, priority=2, weight=1, name="SecondaryObj")

model.optimize()

# Display results
if model.Status == GRB.INFEASIBLE:
    model.computeIIS()
    model.write("constraints_overview\\model.lp")
    print("Model is infeasible")
elif model.Status == GRB.OPTIMAL:
    print("Optimal Objective: %g" % model.objVal)
    model.printAttr('X')
    model.printAttr('Obj')
    print("Spannung an Sammelschiene 2 in [p.u.]: %g" % V[1].X)
    print("K:" + str(k.X))
    
    
