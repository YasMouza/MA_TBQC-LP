import gurobipy as gp
from gurobipy import GRB

# Netzwerkparameter
P1 = 100  # MW
#P2 = -100  # MW
Q1 = 14.6  # MVAr
U1 = 1.03  # Spannung an Busbar 1 in p.u.
B = 0.08  # Suszeptanz in p.u. (B = 1/X)
U2_min = 1.05  # Mindestspannung an Busbar 2 in p.u.
U2_max = 1.06  # Höchstspannung an Busbar 2 in p.u.





# Initialisieren Sie das Modell
model = gp.Model("Blindleistungsoptimierung")
model.params.NonConvex = 2
model.params.Method = 2
# Variablen
Q2 = model.addVar(lb=-100, ub=100, name="Q2")
P2 = model.addVar(lb=-100, ub=100, name="P2")  # Wirkleistung an Busbar 2
V2 = model.addVar(lb=U2_min, ub=U2_max, name="V2")
Q_shunt_set = 50

# Constraints
model.addConstr(U1 * Q1 + 1/B == Q2 * V2, "Leistungsfluss_Q2")
#model.addConstr(U1 * P1 - P2 == Q2 * V2, "Leistungsfluss_P2")


# Zielsetzung
model.setObjective(Q2, GRB.MINIMIZE)

# Optimierung starten
model.optimize()
optimal_V2 = V2.x
optimal_Q2 = Q2.x
Q_shunt = Q_shunt_set * optimal_V2**2
Q_statgen = optimal_Q2 + Q_shunt

# Ergebnisse abrufen
if model.status == GRB.OPTIMAL:
    print("Optimale Lösung gefunden:")
    print(f"Blindleistung Q2 = {Q2.x} MVAr")
    print(f"Spannung V2 = {V2.x} p.u.")
    print(f"Blindleistung Q_statgen = {Q_statgen} MVAr")
    print(f"Blindleistung Q_shunt = {Q_shunt} MVAr")
else:
    print("Das Problem hat keine optimale Lösung gefunden.")

# Modell aufräumen
model.dispose()

