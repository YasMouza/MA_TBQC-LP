import gurobipy as gp
from gurobipy import GRB
import math

def setup_power_flow_model(P1, Q1, P2, Q2, B):
    model = gp.Model("Power_Flow_With_Compensation")
    
    # Model parameters
    model.params.Method = 2  # Interior Point Method
    model.params.NonConvex = 2
    
    # Variables
    V = model.addVars(2, lb=1.05, ub=1.1, name="V")
    theta = model.addVars(2, lb=-math.pi, ub=math.pi, name="theta")
    theta_diff = model.addVar(lb=-2*math.pi, ub=2*math.pi, name="theta_diff")
    Q_Comp = model.addVar(lb=-GRB.INFINITY, ub=GRB.INFINITY, name="Q_Comp")
    sin_theta_diff = model.addVar(lb=-1, ub=1, name="sin_theta_diff")
    cos_theta_diff = model.addVar(lb=-1, ub=1, name="cos_theta_diff")
    V_product = model.addVar(lb=1.05*1.05, ub=1.1*1.1, name="V_product")
    
    # Constraints
    model.addConstr(V_product == V[0] * V[1], "V_product_definition")
    model.addConstr(theta_diff == theta[0] - theta[1], "theta_difference")
    model.addGenConstrSin(sin_theta_diff, theta_diff, "sin_constraint")
    model.addGenConstrCos(cos_theta_diff, theta_diff, "cos_constraint")
    
    model.addConstr(P1 >= V_product * B[0][1] * sin_theta_diff, "P1_balance")
    model.addConstr(P2 <= V_product * B[1][0] * (-sin_theta_diff), "P2_balance")
    model.addConstr(Q1 >= V[0] * V[0] * B[0][0] + V_product * B[0][1] * cos_theta_diff, "Q1_balance")
    model.addConstr(Q2 + Q_Comp >= V[1] * V[1] * B[1][1] + V_product * B[1][0] * (-cos_theta_diff), "Q2_balance")
    model.write('Compensation_with_IPM\\constraints_overview.lp')
    # Objective
    model.setObjective(Q_Comp, GRB.MINIMIZE)
    
    return model

# Test the model
if __name__ == "__main__":
    B = [[0, 0.08], [0.08, 0]]
    P1 = 100  # MV
    Q1 = 100  # MVAr
    P2 = -100  # MV
    Q2 = -100  # MVAr

    model = setup_power_flow_model(P1, Q1, P2, Q2, B)
    model.optimize()

    if model.status == GRB.OPTIMAL:
        print(f"Optimal Q_Comp: {model.getVarByName('Q_Comp').x} MVAr")
    else:
        print("No solution found!")
