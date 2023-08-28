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


def verify_load_flow(P, Q, V_init, theta_init, G, B):
    num_buses = len(V_init)
    
    P_calculated = np.zeros(num_buses)
    Q_calculated = np.zeros(num_buses)
    
    # Lastflussgleichungen
    for i in range(num_buses):
        for j in range(num_buses):
            if i != j:
                P_calculated[i] += V_init[i] * V_init[j] * (G[i][j] * math.cos(theta_init[i] - theta_init[j]) + B[i][j] * math.sin(theta_init[i] - theta_init[j]))
                Q_calculated[i] += V_init[i] * V_init[j] * (G[i][j] * math.sin(theta_init[i] - theta_init[j]) - B[i][j] * math.cos(theta_init[i] - theta_init[j]))

    return V_init, P_calculated, Q_calculated
def calculate_V2(P1, Q1, P2, Q2, Q_Comp, V1, theta1, theta2, B21):
    V2_approx = (Q2 + Q_Comp) / (B21 * V1 * math.sin(theta1 - theta2))
    return V2_approx

def compute_V2(P1, P2, Q1, Q2, theta1, theta2, B):
    numerator = P2 + Q2 * (B[0][1] * math.sin(theta1 - theta2) / B[0][1])
    denominator = 2 * B[0][1] * math.cos(theta1 - theta2)
    
    if numerator / denominator <= 0:
        print("Negativer Wert in der Quadratwurzelfunktion:")
        print("Numerator:", numerator)
        print("Denominator:", denominator)
        print("P1:", P1)
        print("P2:", P2)
        print("Q1:", Q1)
        print("Q2:", Q2)
        print("theta1:", theta1)
        print("theta2:", theta2)
        return 0  # oder einen anderen Standardwert oder Ausnahme werfen

    return math.sqrt(numerator / denominator)



if __name__ == "__main__":
    B = [[0, 0.08], [0.08, 0]]
    G = [[0, 0], [0, 0]]
    Q_values = [-3, -2, -1, -0.1, 0, 6]
    P1 = 1
    P2 = -1
    Q1 = 2
    Q_cap = 0.3
    P = np.array([P1, P2], dtype=np.float64)
    
    output_results = []

    for Q2 in Q_values:
        model_phase1 = setup_phase1_model(P1, Q1, P2, Q2, B)
        model_phase1.optimize()

        V2_value = 0  # Initialisierung von V2_value
        try:
            V2_value = model_phase1.getVarByName("V[1]").x
        except AttributeError:
            pass  # Wir können einfach "pass" verwenden, da V2_value bereits initialisiert ist.

        theta_value = 0  # Initialisierung von theta_value
        try:
            theta_value = model_phase1.getVarByName("theta[1]").x
        except AttributeError:
            pass

        theta_init = np.array([0, theta_value], dtype=np.float64)

        if model_phase1.Status == GRB.OPTIMAL:
            Q_Comp = model_phase1.getVarByName("Q_Comp").x
            model_phase2 = setup_phase2_model(Q_Comp, Q_cap)
            model_phase2.optimize()
            k_value = model_phase2.getVarByName("k").x if model_phase2.Status == GRB.OPTIMAL else None

            Q_updated = np.array([Q1, Q2 + Q_Comp], dtype=np.float64)
            V2_calculated = compute_V2(P1, P2, Q1, Q_updated[1], theta_init[0], theta_init[1], B)
            
            verification_status = "erfolgreich" if math.isclose(V2_value, V2_calculated, rel_tol=1e-5) else "NICHT erfolgreich"
            result = [Q2, "Feasible", Q_Comp, k_value, V2_value, verification_status, V2_calculated]
            output_results.append(result)

        else:
            output_results.append([Q2, "Infeasible", None, None, V2_value])
    
    # Ergebnisse ausgeben
    for result in output_results:
        if "Infeasible" in result:
            print(result)
        else:
            print(result[:5], f"Berechnete V[1]: {result[6]}")
            print(f"Einfache Lastflussrechnung für Q2 = {result[0]} {result[5]} verifiziert!")
            if result[5] == "NICHT erfolgreich":
                print(f"Erwartete Spannung V[1]: {result[4]}")
            print()



            
        





## Nachträgliche Lastflussrechnung mit den Ergebnissen - Über-/Unterkompensation vermeiden
## Range für V2: 1.05 - 1.1
## k-Wert wird so angepasst, dass in nachfolgender LF Rechnung diese Range erreicht wird
## Spannung am Slack != 1 (1x höher, 1x niedriger) 
## Spannung im Netz bricht ein (V1 = 0.9, 0.95)
