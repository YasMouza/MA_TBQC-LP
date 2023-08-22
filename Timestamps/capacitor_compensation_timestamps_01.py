import gurobipy as gp
from gurobipy import GRB
import math
import pandas as pd

P_values = [-10, -5, 0, 5, 10]  # Werte für P1
results = []

X = 12.8  # Reaktanz der Leitung
P_base = 1e9  # Basisleistung in Watt (1 GW)
V_base = 400e3  # Basisspannung in Volt (400 kV)
Q_cap = 30000  # Kapazität eines Kondensators

for P1 in P_values:
    P2 = -0.5 * P_base  # Last an Sammelschiene 2
    Q1 = -0.0005 * P_base  # Blindleistung an Sammelschiene 1
    Q2 = -0.00001 * P_base  # Blindleistung der Last an Sammelschiene 2

    # Phase 1: Ermittlung von Q_Comp
    model_phase1 = gp.Model("optimal_power_flow_phase1")
    model_phase1.params.NonConvex = 2
    model_phase1.params.Method = 2
    V = model_phase1.addVars(2, lb=0.9, ub=1.1, name="V")
    theta = model_phase1.addVars(2, lb=-math.pi, ub=math.pi, name="theta")
    Q_Comp = model_phase1.addVar(lb=0, ub=GRB.INFINITY, name="Q_Comp")  # Kompensations-Blindleistung

    sin_theta_diff = model_phase1.addVar(lb=-1, ub=1, name="sin_theta_diff")
    theta_diff = model_phase1.addVar(lb=-GRB.INFINITY, ub=GRB.INFINITY, name="theta_diff")

    V_product = model_phase1.addVar(lb=0, ub=GRB.INFINITY, name="V_product")
    V_square = model_phase1.addVar(lb=0, ub=GRB.INFINITY, name="V_square")

    # Constraints für Phase 1
    model_phase1.addConstr(theta_diff == theta[0] - theta[1])
    model_phase1.addGenConstrSin(sin_theta_diff, theta_diff)
    model_phase1.addConstr(V_product == V[0] * V[1])
    model_phase1.addConstr(V_square == V[1] * V[1])

    model_phase1.addConstr(V_product * (sin_theta_diff / 12.8) <= (P1 - P2) / P_base)
    model_phase1.addConstr(-V_square * (1 / 12.8) + V_product * (-sin_theta_diff / 12.8) <= (Q1 - Q2 + Q_Comp) / P_base)

    model_phase1.addConstr(V[0] == 1, name="slack_bus")
    model_phase1.addConstr(theta[0] == 0, name="slack_bus_angle")

    delta_plus = model_phase1.addVar(lb=0, name="delta_plus")
    delta_minus = model_phase1.addVar(lb=0, name="delta_minus")

    model_phase1.addConstr(V[1] - 1 <= delta_plus)
    model_phase1.addConstr(1 - V[1] <= delta_minus)
    
    model_phase1.setObjectiveN(delta_plus + delta_minus, 0, priority=1, weight=1, name="PrimaryObj")

    model_phase1.optimize()
    model_phase1.write(f'Timestamps\\test_iteration_01_P{P1}_phase1.lp')
    
    # Ergebnisse sammeln und weiterverarbeiten
    if model_phase1.Status == GRB.INFEASIBLE:
        results.append([P1, "Infeasible", None])
    elif model_phase1.Status == GRB.OPTIMAL:
        results.append([P1, "Feasible", Q_Comp.x, Q_cap, V[1].x])
        
    # Erhalte den Wert von Q_Comp aus der ersten Phase
    Q_Comp_value = Q_Comp.x

    # Phase 2: Berücksichtigung der Kondensatoren
    model_phase2 = gp.Model("optimal_power_flow_phase2")

    k = model_phase2.addVar(lb=1, ub=30, vtype=GRB.INTEGER, name="k")

    # Constraints für Phase 2
    model_phase2.addConstr(k >= Q_Comp_value/Q_cap)

    model_phase2.setObjectiveN(k, 0, priority=0, weight=1, name="PrimaryObj")
    model_phase2.optimize()
    model_phase2.write(f'Timestamps\\test_iteration_01_P{P1}_phase2.lp')
    
    # Ergebnisse sammeln und weiterverarbeiten
    if model_phase2.Status == GRB.INFEASIBLE:
        results.append([P1, "Infeasible", None])
    elif model_phase2.Status == GRB.OPTIMAL:
        results.append([P1, "Feasible", k.x])

for result in results:
    print(result)
