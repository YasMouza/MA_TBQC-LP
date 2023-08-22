import gurobipy as gp
from gurobipy import GRB
import math

def setup_phase1_model(P1, Q1, P2, Q2, B):
    model = gp.Model("optimal_power_flow_phase1")
    
    # Model parameters
    model.params.NonConvex = 2
    model.params.Method = 2
    
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
    model.addConstr(V_product == V[0] * V[1])

    model.addConstr(P1 - V_product * (B[0][1] * cos_theta_diff) >= 0, "p1_constraint")
    model.addConstr(Q1 + Q2 - Q_Comp - V_product * (B[0][1] * sin_theta_diff) >= 0, "q_constraint")
    model.addConstr(P2 - V_product * (B[1][0] * cos_theta_diff) <= 0, "p2_constraint")
    model.addConstr(V[0] == 1, "slack_bus")
    model.addConstr(theta[0] == 0, "slack_bus_angle")

    delta_plus = model.addVar(lb=0, name="delta_plus")
    delta_minus = model.addVar(lb=0, name="delta_minus")
    
    model.addConstr(V[1] - 1 <= delta_plus, "delta_plus_constraint")
    model.addConstr(1 - V[1] <= delta_minus, "delta_minus_constraint")

    # Objective function
    model.setObjectiveN(delta_plus + delta_minus, 0, priority=1, weight=1, name="PrimaryObj")
    model.setObjectiveN(Q_Comp, 1, priority=1, weight=-1, name="SecondaryObj") 
    return model

def setup_phase2_model(Q_Comp_value, Q_cap):
    model = gp.Model("optimal_power_flow_phase2")
    k = model.addVar(lb=1, ub=30, vtype=GRB.INTEGER, name="k")
    model.addConstr(k >= Q_Comp_value/Q_cap)
    model.setObjective(k, GRB.MINIMIZE)
    return model

if __name__ == "__main__":
    B = [[0, 0.08], [0.08, 0]]
    Q_values = [-3, -2, -1, -0.1, 0, 6]
    P1 = 1
    P2 = -1
    Q1 = 2
    Q_cap = 0.3

    results = []

    for Q2 in Q_values:
        model_phase1 = setup_phase1_model(P1, Q1, P2, Q2, B)
        model_phase1.optimize()

        V1_value = model_phase1.getVarByName("V[1]").x if model_phase1.Status == GRB.OPTIMAL else None

        if model_phase1.Status == GRB.INFEASIBLE:
            results.append([Q2, "Infeasible", None, None, V1_value])
        elif model_phase1.Status == GRB.OPTIMAL:
            Q_Comp = model_phase1.getVarByName("Q_Comp").x
            model_phase2 = setup_phase2_model(Q_Comp, Q_cap)
            model_phase2.optimize()

            k_value = model_phase2.getVarByName("k").x if model_phase2.Status == GRB.OPTIMAL else None
            results.append([Q2, "Feasible", Q_Comp, k_value, V1_value])

    for result in results:
        print(result)
