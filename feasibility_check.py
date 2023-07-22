import numpy as np
import matplotlib.pyplot as plt
import math
import gurobipy as gp
from gurobipy import GRB

#### 1. GET GRID-VARIABLES 
n_buses = 2
X = [[0, 12.8], [12.8, 0]]  # Reactance matrix
R = [[0, 0], [0, 0]] 
k = 0.01 # integer variable
B = [[1 / element if element != 0 else 0 for element in row] for row in X]
G = [[0, 0], [0, 0]] 

P_load_range = np.linspace(-1, 0.5, 10)  
Q_load_range = np.linspace(-1, 0.5, 10)  

feasible_P = []
feasible_Q = []
unfeasible_P = []
unfeasible_Q = []

for P_load_value in P_load_range:
    for Q_load_value in Q_load_range:
        P_load = [0, P_load_value]  # Active power load at each bus
        Q_load = [0, Q_load_value]  # Reactive power load at each bus

        #### 2. CREATE MODEL
        model = gp.Model("optimal_power_flow")
        model.params.NonConvex = 2
        model.params.Method = 2

        ### 2.1 CREATE VARIABLES
        V = model.addVars(n_buses, lb=0.9, ub=1.1, name="V")  # Voltage magnitudes
        theta = model.addVars(n_buses, lb=-math.pi, ub=math.pi, name="theta")  # Voltage angles

        # Define an auxiliary variable for the product V[0] * V[1]
        V_product = model.addVar(lb=0, ub=GRB.INFINITY, name="V_product")
        model.addConstr(V_product == V[0] * V[1])

        p1 = P_load[0]
        p2 = P_load[1]
        q1 = Q_load[0]
        q2 = Q_load[1]

        # add variables for delta_v 
        delta_v_plus = model.addVar(lb=0, name="delta_v_plus")
        delta_v_minus = model.addVar(lb=0, name="delta_v_minus")

        ### 2.1 ADD CONSTRAINTS
        model.addConstr(V[0] == 1, name="slack_bus")
        model.addConstr(theta[0] == 0, name="slack_bus_angle")

        # Define auxiliary variables for the trigonometric functions
        cos_theta_diff = model.addVar(lb=-1, ub=1, name="cos_theta_diff")
        sin_theta_diff = model.addVar(lb=-1, ub=1, name="sin_theta_diff")
        # Define the difference theta[0] - theta[1]
        theta_diff = model.addVar(lb=-GRB.INFINITY, ub=GRB.INFINITY, name="theta_diff")
        model.addConstr(theta_diff == theta[0] - theta[1])
        # Add the trigonometric constraint
        model.addGenConstrCos(cos_theta_diff, theta_diff)
        model.addGenConstrSin(sin_theta_diff, theta_diff)

        # Add the power flow constraints
        model.addConstr(k*(p1 - V_product * (B[0][1] * cos_theta_diff)) <= 0, name="p1")
        model.addConstr(k*(q1 - V_product * (B[0][1] * sin_theta_diff)) <= 0, name="q1")
        model.addConstr(k*(p2 - V_product * (B[1][0] * cos_theta_diff)) <= 0, name="p2")
        model.addConstr(k*(q2 - V_product * (B[1][0] * sin_theta_diff)) <= 0, name="q2")

        # Add constraints to model the absolute value
        model.addConstr(delta_v_plus - delta_v_minus == V[1] - 1)
        model.addConstr(delta_v_plus >= 0)
        model.addConstr(delta_v_minus >= 0)

        model.write("model.lp")

        ### 2.2 ADD OBJECTIVE
        model.setObjective(delta_v_plus + delta_v_minus, GRB.MINIMIZE)

        ### 2.3 SOLVE MODEL
        model.optimize()

        ### 2.4 PRINT RESULTS
        if model.Status == GRB.OPTIMAL:
            feasible_P.append(P_load_value)
            feasible_Q.append(Q_load_value)
        else:
            unfeasible_P.append(P_load_value)
            unfeasible_Q.append(Q_load_value)

# Plot the feasible region
plt.scatter(feasible_P, feasible_Q, color='blue')
plt.scatter(unfeasible_P, unfeasible_Q, color='red')
plt.xlabel('P_load')
plt.ylabel('Q_load')
plt.title('Feasible region for P_load and Q_load')
plt.show()
