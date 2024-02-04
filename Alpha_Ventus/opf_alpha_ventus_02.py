from pyomo.environ import *
import cmath
import math

# Netzwerkparameter
P = [50, -100, 100, 50, 30]  # MV
#Mvar über cos phi = 0.95
### PV Knoten (Q nicht vorgeben)
Q = [5, 30, 40, 50, 30]   # Mvar
### An Bus 1 sind die Werte vorgegeben, sonst nicht
V1 = 1.03  # p.u.
l = 70     # km
R_prime = 0.018  # Ohm/km
X_prime = 0.123  # Ohm/km
C_prime = 280e-9  # Farad/km
n = 5
R = R_prime * l
X = X_prime * l
C = C_prime * l
omega = 2 * cmath.pi * 50  # Kreisfrequenz für 50 Hz
B = C * omega

# Modell initialisieren
model = ConcreteModel()
model.I = RangeSet(1, n)  # 1-basierte Indizierung

# Variablen
model.V = Var(model.I, bounds=(0.9, 1.1))
model.P = Var(model.I, initialize=lambda model, i: P[i-1])
model.Q = Var(model.I, initialize=lambda model, i: Q[i-1])
model.theta = Var(model.I, bounds=(-math.pi, math.pi))

# Parameter (Beispielwerte, bitte anpassen)
B_ij_values = [
    [0, -1/X, 0, 0, 0],
    [-1/X, 2/X, -1/X, 0, 0],
    [0, -1/X, 2/X, -1/X, 0],
    [0, 0, -1/X, 2/X, -1/X],
    [0, 0, 0, -1/X, 1/X]
]

model.B_ij = Param(model.I, model.I, initialize=lambda model, i, j: B_ij_values[i-1][j-1])
model.G_ij = Param(model.I, model.I, initialize=lambda model, i, j: 0)

# Constraints
def Q_constraint_rule(model, i):
    return model.Q[i] == sum(model.V[j] * (model.G_ij[i,j] * sin(model.theta[i] - model.theta[j]) - model.B_ij[i,j] * cos(model.theta[i] - model.theta[j])) for j in model.I)

def P_constraint_rule(model, i):
    return model.P[i] == sum(model.V[j] * (model.G_ij[i,j] * cos(model.theta[i] - model.theta[j]) + model.B_ij[i,j] * sin(model.theta[i] - model.theta[j])) for j in model.I)

model.Q_constraints = Constraint(model.I, rule=Q_constraint_rule)
model.P_constraints = Constraint(model.I, rule=P_constraint_rule)

# Zielsetzung
model.objective = Objective(expr=sum(model.V[i] for i in model.I), sense=minimize)
### bei PQ Knoten: 0.95 < v2 < 1.1
# Solver
solver = SolverFactory('ipopt')
if not solver.available():
    print("Solver is not available")
    exit(1)

# Modell lösen
results = solver.solve(model, tee=True)

# Ergebnisse ausgeben
if results.solver.status == SolverStatus.ok and results.solver.termination_condition == TerminationCondition.optimal:
    print("Optimale Lösung gefunden:")
    for i in model.I:
        print(f"V{i}: {model.V[i].value}, Theta{i}: {model.theta[i].value}")
else:
    print("Keine optimale Lösung gefunden. Modell ist unzulässig.")
