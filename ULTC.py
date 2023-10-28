from gurobipy import Model, GRB

# Parameter
N = 2  # Anzahl der Busse
P = [100, 150]  # Vektor der aktiven Lasten
Q = [50, 75]  # Vektor der reaktiven Lasten
a = [-10, -15]  # Untere Grenzen für s und x
b = [10, 15]  # Obere Grenzen für s und x

# Modell erstellen
m = Model("PowerFlowUnsolvability")

# Variablen
e = m.addVars(N, vtype=GRB.BINARY, name="e")
o = m.addVars(N, vtype=GRB.BINARY, name="o")
s = m.addVars(N, vtype=GRB.CONTINUOUS, name="s")
x = m.addVars(N, vtype=GRB.CONTINUOUS, name="x")

# Zielfunktion
m.setObjective(sum(s), GRB.MINIMIZE)

# Nebenbedingungen
m.addConstrs((P[i] * (1 - e[i]) - P[i] * x[i] == 0 for i in range(N)), name="P_balance")
m.addConstrs((Q[i] * (1 - o[i]) - Q[i] * x[i] == 0 for i in range(N)), name="Q_balance")
m.addConstrs((a[i] <= s[i] + x[i] <= b[i] for i in range(N)), name="bounds")

# Modell lösen
m.optimize()
