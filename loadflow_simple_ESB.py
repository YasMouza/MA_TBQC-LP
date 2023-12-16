import gurobipy as gp
from gurobipy import GRB
import math 

# Netzwerkparameter
n = 2  # Anzahl der Knoten
G = [[0, 0.0], [0.0, 0]]  # Realteil der Admittanzmatrix (Beispielwerte)
B = [[0, -0.08], [-0.08, 0]]  # Imaginärteil der Admittanzmatrix (Beispielwerte)

# Initialisieren Sie das Modell
model = gp.Model("Spannungsoptimierung")
model.params.Method = 2  # Interior-Point-Methode

# Variablen
V = model.addVars(n, lb=0.9, ub=1.1, name="V")  # Spannungen
P = model.addVars(n, name="P")  # Wirkleistungen
Q = model.addVars(n, name="Q")  # Blindleistungen
delta_v = model.addVar(lb=0, ub=GRB.INFINITY, name="delta_v")
k = model.addVar(lb=-50, ub=50, name="k")
k_int = model.addVar(vtype=GRB.INTEGER, name="k_int")
theta = model.addVars(n, lb=-math.pi, ub=math.pi, name="theta")  # Phasenwinkel

# Netzwerkspezifische Parameter
V1 = 1.03  # p.u.
V2_target = 1.05  # p.u.
P1_pu = 1.0  # p.u.
Q1_pu = 1.1  # p.u.
P2_pu = -1.0  # p.u.
Q2_pu = 0.2  # p.u.
Q_set_shunt = 0.02  #p.u


for i in range(n):
    for j in range(n):
        if i != j:
            # Hilfsvariablen für Produkte
            VV = model.addVar(name="VV_" + str(i) + "_" + str(j))
            cos_approx = model.addVar(name="cos_approx_" + str(i) + "_" + str(j))
            sin_approx = model.addVar(name="sin_approx_" + str(i) + "_" + str(j))
            
            # gc = model.addGenConstrSin(x, y)

            # Definition der Hilfsvariablen
            model.addConstr(VV == V[i] * V[j], "VV_def_" + str(i) + "_" + str(j))
            delta_theta = theta[i] - theta[j]
            model.addConstr(cos_approx == 1 - 0.5 * delta_theta * delta_theta, "cos_approx_" + str(i) + "_" + str(j))
            model.addConstr(sin_approx == delta_theta, "sin_approx_" + str(i) + "_" + str(j))

            # Lastflussgleichungen
            model.addConstr(P[i] >= VV * (G[i][j] * cos_approx + B[i][j] * sin_approx), "Wirkleistung_" + str(i) + "_" + str(j))
            model.addConstr(Q[i] >= VV * (G[i][j] * sin_approx - B[i][j] * cos_approx), "Blindleistung_" + str(i) + "_" + str(j))
            
            if n == 1:
                model.addConstr(Q[i] >= Q2_pu + k*Q_set_shunt *  VV * (G[i][j] * sin_approx - B[i][j]* cos_approx))
            

            

# Zusätzliche Constraints
model.addConstr(V[0] <= V1, "Spannung_V1")
model.addConstr(P[0] == P1_pu, "Wirkleistung_P1")
model.addConstr(Q[0] <= Q1_pu, "Blindleistung_Q1")
print(Q1_pu)
print(Q2_pu)
model.addConstr(P[1] >= P2_pu, "Wirkleistung_P2")
model.addConstr(Q[1] == Q2_pu + k * Q_set_shunt, "Blindleistung_Q2")
model.addConstr(delta_v >= V[1] - V2_target, "delta_v_1")
model.addConstr(delta_v >= V2_target - V[1], "delta_v_2")
model.addConstr(k_int <= k, "k_int_1")
model.addConstr(k - k_int <= 1, "k_int_2")

# Zielsetzung
model.setObjective(delta_v, GRB.MINIMIZE)

# Optimierung starten
model.params.NonConvex = 2
model.optimize()


model.write('loadflow_simple_esb_01.lp')
# Ergebnisse abrufen
if model.status == GRB.OPTIMAL:
    print("Optimale Lösung gefunden:")
    print("Spannungen: ", V[0].x, V[1].x)
    print("Wirkleistungen: ", P[0].x, P[1].x)
    print("Blindleistungen: ", Q[0].x, Q[1].x)
    print("Q_1:", Q[0].x)
    print("Q_2:", Q[1].x)
    print("Delta V: ", delta_v.x)
    print("k: ", k.x)
    print("k_int: ", k_int.x)
    print("cosinus approximierung: ", cos_approx.x)
    print("sinusapproximierung: ", sin_approx.x)
else:
    print("Keine optimale Lösung gefunden.")
