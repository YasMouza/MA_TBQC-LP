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
    model.addConstr(V[0] == 1.05, "slack_bus")
    model.addConstr(theta[0] == 0, "slack_bus_angle")
    model.addConstr(V[1] >= 1.05, "Voltage range bus 2(1)")
    model.addConstr(V[1] <= 1.1, "Voltage range bus 2(2)")

    delta_plus = model.addVar(lb=0, name="delta_plus")
    delta_minus = model.addVar(lb=0, name="delta_minus")

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

def setup_linear_load_flow_model(P1, P2, Q1, Q2_plus_Q_Comp, B):
    model = gp.Model("linear_load_flow")
    
    # Variablen
    V = model.addVars(2, lb=0.9, ub=1.1, name="V")
    theta = model.addVars(2, lb=-math.pi, ub=math.pi, name="theta")
    theta_diff = model.addVar(lb=-math.pi, ub=math.pi, name="theta_diff")
    cos_theta_diff = model.addVar(lb=-1, ub=1, name="cos_theta_diff")
    sin_theta_diff = model.addVar(lb=-1, ub=1, name="sin_theta_diff")
    V_prod = model.addVar(lb=0.9*0.9, ub=1.1*1.1, name="V_prod")  # Hilfsvariable Spannungsprodukt
    
    # Constraints
    # Für Sammelschiene 1 (Slack-Bus): 
    model.addConstr(theta[0] == 0, "slack_bus_angle")
    model.addConstr(V[0] == 1, "slack_bus_voltage")
    model.addConstr(theta_diff == theta[1] - theta[0], "theta_difference")

    # Für Sammelschiene 2:
    model.addConstr(V[1] >= 1.05, "Voltage range bus 2(1)")
    model.addConstr(V[1] <= 1.1, "Voltage range bus 2(2)")
 
    # Constraints für den Phasenwinkelunterschied
    model.addConstr(theta_diff == theta[1] - theta[0], "theta_difference")

    # General constraints für sin und cos des Phasenwinkelunterschieds
    model.addGenConstrSin(sin_theta_diff, theta_diff)
    model.addGenConstrCos(cos_theta_diff, theta_diff)
    model.addConstr(V_prod == V[0] * V[1])

    # Active Power
    model.addConstr(P1 >= V_prod * B[0][1] * cos_theta_diff, "P1_balance")
    model.addConstr(P2 >= V_prod * B[1][0] * cos_theta_diff, "P2_balance")
    
    # Reactive Power
    model.addConstr(Q1 >= V_prod * B[0][1] * sin_theta_diff, "Q1_balance")
    model.addConstr(Q2_plus_Q_Comp >= V_prod * B[1][0] * sin_theta_diff, "Q2_balance")
    
    # Zielsetzung (optional, da wir nur eine machbare Lösung suchen)
    model.setObjective(V[1], GRB.MAXIMIZE)    
    return model

def get_V2_from_linear_model(P1, P2, Q1, Q2_plus_Q_Comp, B):
    # Erstelle das lineare Lastfluss-Modell
    model = setup_linear_load_flow_model(P1, P2, Q1, Q2_plus_Q_Comp, B)
    
    # Optimiere das Modell
    model.optimize()

    # Schreibe das Modell in eine .lp Datei
    filename = f'Q_Variation\\Verification_Lastfluss{Q2_plus_Q_Comp}.lp'
    model.write(filename)

    # Prüfe, ob eine optimale Lösung gefunden wurde
    if model.status == GRB.OPTIMAL:
        V2 = model.getVarByName("V[1]").x
        return V2
    else:
        return None  # Keine Lösung gefunden


if __name__ == "__main__":
    B = [[0, 0.08], [0.08, 0]]
    G = [[0, 0], [0, 0]]
    Q_values = [-3, -2, -1, -0.1, 0, 6]
    P1 = 1
    P2 = 1
    Q1 = 2
    #Q_cap = 0.3
    Q_cap = 0.001 
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

            V2_linear = get_V2_from_linear_model(P1, P2, Q1, Q2 + Q_Comp, B)

            result = {
                'Q2': Q2,
                'V2_phase1': V2_value,
                'Q_Comp': Q_Comp,
                'k_value': k_value,
                'V2_linear': V2_linear
            }
            output_results.append(result)
        else:
            result = {
                'Q2': Q2,
                'V2_phase1': V2_value,
                'Q_Comp': None,
                'k_value': None,
                'V2_linear': None
            }
            output_results.append(result)
    
    # Ergebnisse ausgeben
    for result in output_results:
        print(f"Für Q2 = {result['Q2']}:")
        print(f"V2 aus Phase 1: {result['V2_phase1']}")
        if result['Q_Comp'] is not None:
            print(f"Q_Comp aus Phase 1: {result['Q_Comp']}")
            print(f"k-Wert aus Phase 2: {result['k_value']}")
            print(f"V2 aus linearem Lastfluss: {result['V2_linear']}")
        else:
            print("Keine optimale Lösung in Phase 1 gefunden.")
        print("----------------------------")


### Werte aus Model phase 1 in Powerfactory
### Fokus auf diskrete Schaltungen
### Stimmiges Ergebnis bis in 3 Wochen
### Induktivität und Kapazität 