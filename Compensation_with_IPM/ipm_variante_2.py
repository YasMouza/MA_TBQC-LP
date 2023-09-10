import gurobipy as gp
from gurobipy import GRB

class PowerSystemOptimization:
    def __init__(self, B):
        self.B = B
        self.model = gp.Model("PowerSystemOptimization")
        self.configure_solver()

    def configure_solver(self):
        # Setzen Sie den Optimierer auf das Interior Point Verfahren
        self.model.Params.Method = 2
        self.model.Params.OutputFlag = 0

    def setup_optimization(self):
        # Variablen
        V = self.model.addVars(2, lb=1.05, ub=1.1, name="V")
        theta_diff = self.model.addVar(lb=-GRB.INFINITY, ub=GRB.INFINITY, name="theta_diff")
        sin_theta_diff = self.model.addVar(lb=-1, ub=1, name="sin_theta_diff")
        cos_theta_diff = self.model.addVar(lb=-1, ub=1, name="cos_theta_diff")
        Q_Comp = self.model.addVar(lb=-GRB.INFINITY, ub=GRB.INFINITY, name="Q_Comp")
        V_product = self.model.addVar(lb=0, ub=GRB.INFINITY, name="V_product")

        # Define General Constraints for sin and cos
        self.model.addGenConstrSin(sin_theta_diff, theta_diff, "sin_constraint")
        self.model.addGenConstrCos(cos_theta_diff, theta_diff, "cos_constraint")

        # Einschränkungen
        self.model.addConstr(V[0] == 1.05, "V1_fixed")
        self.model.addConstr(V_product == V[0] * V[1], "V_product_definition")
        self.model.addConstr(100 >= V_product * self.B[0][1] * sin_theta_diff, "P_balance")
        self.model.addConstr(80 <= V[0] * V[0] * self.B[0][0] + V_product * self.B[0][1] * cos_theta_diff, "Q1_balance")
        self.model.addConstr(-90 + Q_Comp <= V[1] * V[1] * self.B[1][1] + V_product * self.B[1][0] * cos_theta_diff, "Q2_balance")
        self.model.write('Compensation_with_IPM\\constraints_variante2.lp')
        # Zielsetzung
        self.model.setObjective(Q_Comp, GRB.MINIMIZE)

    def optimize(self):
        self.model.optimize()
        if self.model.Status == GRB.OPTIMAL:
            return self.model.getVarByName("Q_Comp").x
        else:
            return None

if __name__ == "__main__":
    B = [[0, -1], [-1, 0]]  # Beispielwerte für B-Matrix
    optimizer = PowerSystemOptimization(B)
    optimizer.setup_optimization()
    Q_Comp = optimizer.optimize()

    if Q_Comp:
        print(f"Die notwendige Kompensation beträgt: {Q_Comp} MVar")
    else:
        print("Keine optimale Lösung gefunden.")
