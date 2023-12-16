import gurobipy as gp
from gurobipy import GRB
import numpy as np

# Netzwerkparameter
Sbase = 100
P1 = 100  # MW
P1_pu = P1 / Sbase
Q1 = 50  # Mvar
Q1_pu = Q1 / Sbase
P2 = -100  # MW
P2_pu = P2 / Sbase
Q2 = 30  # Mvar
Q2_pu = Q2 / Sbase
V1 = 1.03  # p.u.
V2_target = 1.05  # p.u.
B = 0.08  # p.u.
l = 70  # km
R_prime = 0.018  # Ohm/km
X_prime = 0.123  # Ohm/km
C_prime = 280e-9  # Farad/km

# Impedanz und Admittanz der Leitung
Z = R_prime * l + 1j * X_prime * l
Y = 1 / Z
Y11 = Y
Y12 = -Y

Q_shunt_set = 10

# Initialisieren Sie das Modell
model = gp.Model("Spannungsoptimierung")
model.params.Method = 2  # Interior-Point-Methode

# Variablen
V2_nach_compensation = model.addVar(lb=0.9, ub=1.1, name="V2_nach_compensation")
Q_Comp = model.addVar(lb=-100, ub=100, name="Q_Comp")
delta = model.addVar(lb=0, ub=GRB.INFINITY, name="delta")
k = model.addVar(lb=-50, ub=50, name="k")
k_int = model.addVar(vtype=GRB.INTEGER, name="k_int")

# Constraints
model.addConstr(V1 * Q1_pu + 1/B == Q2_pu * V2_nach_compensation + k*Q_shunt_set + V1 * V2_nach_compensation * Y12.imag, "Leistungsfluss_Q2")
model.addConstr(P2_pu <= V1 * P1_pu * B - V1 * V2_nach_compensation * Y12.real, "Leistungsfluss_P2")
model.addConstr(delta >= V2_nach_compensation - V2_target, "abs1")
model.addConstr(delta >= V2_target - V2_nach_compensation, "abs2")
model.addConstr(k_int <= k, "k_int")
model.addConstr(k - k_int <= 1, "k_int_round_down")

# Zielsetzung
model.setObjective(delta, GRB.MINIMIZE)

# Optimierung starten
model.optimize()

# Ergebnisse abrufen
if model.status == GRB.OPTIMAL:
    print("Optimale Lösung gefunden:")
    print("V2_nach_compensation: ", V2_nach_compensation.x)
    #print("Q_Comp: ", Q_Comp.x)
    print('k_int:', k_int.x)
else:
    print("Keine optimale Lösung gefunden.")
