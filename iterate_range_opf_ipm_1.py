import numpy as np
import math
import gurobipy as gp
from gurobipy import GRB
import pandas as pd

P_values = [-10, -5, 0, 5, 10]
# Liste zur Speicherung der Ergebnisse
results = []

for P0 in P_values:
    #### 1. GET GRID-VARIABLES 
    n_buses = 2
    P_load = [P0, -5]  # Update the first value with P0
    Q_load = [-10, -0.06]
    X = [[0, 12.8], [12.8, 0]]
    R = [[0, 0], [0, 0]]

    B = [[1 / element**2 if element != 0 else 0 for element in row] for row in X]
    G = [[0, 0], [0, 0]]

    #### 2. CREATE MODEL
    model = gp.Model("optimal_power_flow")
    model.params.NonConvex = 2
    model.params.Method = 2

    ### 2.1 CREATE VARIABLES
    V = model.addVars(n_buses, lb=0.9, ub=1.1, name="V")
    theta = model.addVars(n_buses, lb=-math.pi, ub=math.pi, name="theta")
    k = model.addVar(lb=1, ub=6, vtype=GRB.INTEGER, name="k")
    
    deltaV_plus = model.addVar(lb=0, ub=GRB.INFINITY, name="deltaV_plus")
    deltaV_minus = model.addVar(lb=0, ub=GRB.INFINITY, name="deltaV_minus")

    # Trigonometric function variables
    cos_theta_diff = model.addVar(lb=-1, ub=1, name="cos_theta_diff")
    sin_theta_diff = model.addVar(lb=-1, ub=1, name="sin_theta_diff")
    theta_diff = model.addVar(lb=-GRB.INFINITY, ub=GRB.INFINITY, name="theta_diff")
    model.addConstr(theta_diff == theta[0] - theta[1])
    model.addGenConstrCos(cos_theta_diff, theta_diff)
    model.addGenConstrSin(sin_theta_diff, theta_diff)

    # Product variable for quadratic expressions
    V_product = model.addVar(lb=0, ub=GRB.INFINITY, name="V_product")
    model.addConstr(V_product == V[0] * V[1])
    quad_intermediate = model.addVar(lb=-GRB.INFINITY, ub=GRB.INFINITY, name="quad_intermediate")
    model.addConstr(quad_intermediate == V_product * (B[1][0] * sin_theta_diff))
    print(B[1][0])
    print(V_product)
    print(sin_theta_diff)
    print(quad_intermediate)
    # Power values
    p1 = P_load[0]
    p2 = P_load[1]
    q1 = Q_load[0]
    q2 = Q_load[1]

    ### 2.1 ADD CONSTRAINTS
    model.addConstr(V[0] == 1, name="slack_bus")
    model.addConstr(theta[0] == 0, name="slack_bus_angle")

    # Power flow constraints
    model.addConstr(p1 - V_product * (B[0][1] * cos_theta_diff) <= 0, name="p1")
    model.addConstr(q1 - V_product * (B[0][1] * sin_theta_diff) <= 0, name="q1")
    model.addConstr(p2 - V_product * (B[1][0] * cos_theta_diff) <= 0, name="p2")
    model.addConstr(k * (q2 - quad_intermediate) <= 0, name="q2")
    test = 1
    # Define the absolute difference between V[1] and 1 using two additional variables
    delta_plus = model.addVar(lb=0, name="delta_plus")
    delta_minus = model.addVar(lb=0, name="delta_minus")
    
    model.addConstr(V[1] - 1 <= delta_plus)
    model.addConstr(1 - V[1] <= delta_minus)
    
    # Objective to minimize the absolute difference
    #model.setObjective(delta_plus + delta_minus, GRB.MINIMIZE)
    model.setObjective(V[1], GRB.MAXIMIZE)

    # Solve and display results
    model.optimize()

    print(f"Results for P[0] = {P0}:")
    if model.Status == GRB.INFEASIBLE:
        print(f"The model is infeasible.")
        model.computeIIS()
        results.append([P0, 0, "Infeasible", None, None]) # "None" für infeasible Modelle
    elif model.Status == GRB.OPTIMAL:
        print(f"Optimal Objective (Delta V): {model.objVal}")
        for v in model.getVars():
            print(f"{v.varName} = {v.x}")
        print("Spannung an Sammelschiene 2 in [p.u.]: %g" % V[1].X)
        results.append([P0, k.x, "Feasible", quad_intermediate.x, V[1].x])

df = pd.DataFrame(results, columns=['P', 'k', 'Status', 'quad_intermediate', 'V[1]'])
print(df)

    