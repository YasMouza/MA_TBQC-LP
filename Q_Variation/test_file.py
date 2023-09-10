import gurobipy as gp
from gurobipy import GRB
import math
import numpy as np


def setup_phase1_model(P1, Q1, P2, Q2, B):
    model = gp.Model("optimal_power_flow_phase1")
    
    # Model parameters
    model.params.NonConvex = 2
    model.params.Method = 2
    model.params.OutputFlag = 0
    
    # Variables
    V = model.addVars(2, lb=0.9, ub=1.1, name="V")
    theta = model.addVars(2, lb=-math.pi, ub=math.pi, name="theta")
    Q_Comp = model.addVar(lb=0, ub=GRB.INFINITY, name="Q_Comp")
    cos_theta_diff = model.addVar(lb=-1, ub=1, name="cos_theta_diff")
    sin_theta_diff = model.addVar(lb=-1, ub=1, name="sin_theta_diff")
    theta_diff = model.addVar(lb=-GRB.INFINITY, ub=GRB.INFINITY, name="theta_diff")
    V_product = model.addVar(lb=0, ub=GRB.INFINITY, name="V_product")
    
    # Constraints
    model.addGenConstrCos(cos_theta_diff, theta_diff)
    model.addGenConstrSin(sin_theta_diff, theta_diff)
    model.addConstr(theta_diff == theta[0] - theta[1])
    #model.addConstr(V_product == V1 * V2 * V2)
    model.addConstr(V_product == V[1] * V[1])


    model.addConstr(P1 - V_product * (B[0][1] * cos_theta_diff) >= 0, "p1_constraint")
    model.addConstr(Q1 + Q2 - Q_Comp - V_product * (B[0][1] * sin_theta_diff) >= 0, "q_constraint")
    model.addConstr(P2 - V_product * (B[1][0] * cos_theta_diff) <= 0, "p2_constraint")
    model.addConstr(V[0] == 1, "slack_bus")
    model.addConstr(theta[0] == 0, "slack_bus_angle")
    model.addConstr(V[1] >= 1.05, "Voltage range bus 2(1)")
    model.addConstr(V[1] <= 1.1, "Voltage range bus 2(2)")

    delta_plus = model.addVar(lb=0, name="delta_plus")
    delta_minus = model.addVar(lb=0, name="delta_minus")
    
    # model.addConstr(V[1] - 1 <= delta_plus, "delta_plus_constraint")
    # model.addConstr(1 - V[1] <= delta_minus, "delta_minus_constraint")

    # Objective function
    #model.setObjectiveN(delta_plus + delta_minus, 0, priority=1, weight=1, name="PrimaryObj")
    #model.setObjective(V[1], GRB.MINIMIZE)
    #model.setObjectiveN(V[1], 0, priority = 0, weight=1, name = "primaryObj")
    model.setObjectiveN(Q_Comp, 1, priority=1, weight=-1, name="SecondaryObj") 
    model.write('Q_Variation\\test-model.lp')
    return model


def setup_phase2_model(Q_Comp_value, Q_cap):
    model = gp.Model("optimal_power_flow_phase2")
    model.params.OutputFlag = 0
    k = model.addVar(lb=1, ub=30, vtype=GRB.INTEGER, name="k")
    model.addConstr(k >= Q_Comp_value/Q_cap)
    model.setObjective(k, GRB.MINIMIZE)
    return model


        
# Newton-Raphson-Code:
def power_mismatch(V, V1, Y, P1, P2):
    P_calculated_1 = V1 * V * Y[0, 1]
    P_calculated_2 = V**2 * Y[1, 1] - V1 * V * Y[0, 1]
    dP1 = P1 - P_calculated_1
    dP2 = P2 - P_calculated_2
    return dP1, dP2

def jacobian(V, V1, Y):
    dP1_dV = V1 * Y[0, 1]
    dP2_dV = 2 * V * Y[1, 1] - V1 * Y[0, 1]
    return np.array([dP1_dV, dP2_dV])

def solve_lastfluss(Y, P1, P2, V1, V0, tol=1e-6, max_iter=100):
    V = V0
    for _ in range(max_iter):
        dP1, dP2 = power_mismatch(V, V1, Y, P1, P2)
        J = jacobian(V, V1, Y)
        dV = (dP1 + dP2) / J.sum()
        V += dV
        if abs(dV) < tol:
            break
    return V

if __name__ == "__main__":
    B = [[0, 0.08], [0.08, 0]]
    G = [[0, 0], [0, 0]]
    #Q_values = [-3, -2, -1, -0.1, 0, 6]

    Q_values = [0, 6]  # Beispielwerte für Q2
    P1 = 1
    P2 = -1
    Q1 = 2
    Q_cap = 0.3

    for Q2 in Q_values:
        model_phase1 = setup_phase1_model(P1, Q1, P2, Q2, B)
        model_phase1.optimize()

        V1_value = model_phase1.getVarByName("V[0]").x  # Extrahieren von V1
        V2_value = model_phase1.getVarByName("V[1]").x  # Extrahieren von V2

        if model_phase1.Status == GRB.OPTIMAL:
            Q_Comp = model_phase1.getVarByName("Q_Comp").x
            model_phase2 = setup_phase2_model(Q_Comp, Q_cap)
            model_phase2.optimize()
            k_value = model_phase2.getVarByName("k").x if model_phase2.Status == GRB.OPTIMAL else None

            print(f"Für Q2 = {Q2}:")
            print(f"Optimale Blindleistungskompensation (Q_Comp) = {Q_Comp}")
            print(f"Minimale Anzahl von Kompensatoren (k) = {k_value}")

            # Newton-Raphson-Berechnung:
            Y = np.array([[1, 1], [1, 1]])  # Hier können Sie die Admittanzmatrix entsprechend Ihrem Netzwerk anpassen
            V2_calculated = solve_lastfluss(Y, P1, P2, V1_value, V0=V2_value)
            print(f"Die Spannung an Sammelschiene 2 nach IPM ist: {V2_value}")
            print(f"Die Spannung an Sammelschiene 2 nach Newton-Raphson ist: {V2_calculated}")
            print("----------")

## Nachträgliche Lastflussrechnung mit den Ergebnissen - Über-/Unterkompensation vermeiden
## Range für V2: 1.05 - 1.1
## k-Wert wird so angepasst, dass in nachfolgender LF Rechnung diese Range erreicht wird
## Spannung am Slack != 1 (1x höher, 1x niedriger) 
## Spannung im Netz bricht ein (V1 = 0.9, 0.95)
