#### Calculation with R = 0 
from pyomo.environ import *
import cmath
import math

# Netzwerkparameter
P1 = 78.7  # MW
P2 = 80
P3 = 100
P4 = 50
P5 = 30
Q1 = 1446.2  # Mvar
P2 = -100  # MW
Q2 = 30  # Mvar
Q3 = 40
Q4 = 50
Q5 = 30
V1 = 1.03  # p.u.
l = 70  # km
R_prime = 0.018  # Ohm/km
X_prime = 0.123  # Ohm/km
C_prime = 280e-9  # Farad/km
n = 5
R = R_prime * l
X = X_prime * l
C = C_prime * l
omega = 2 * cmath.pi * 50  # Kreisfrequenz für 50 Hz
B = C * omega

#### R = 0 ####

# Netzwerkspezifische Parameter
V1 = 1.03  # p.u.
V2_target = 1.05  # p.u.
P1_pu = 1.0  # p.u.
Q1_pu = 0.5  # p.u.
P2_pu = -1.0  # p.u.
Q2_pu = 0.3  # p.u.
Q_set_shunt_1 = Q_set_shunt_2 = 10/100  # MVar
Q_statgen = 80  # MVar
Q_statgen_pu = Q_statgen/100  # p.u.

# Modell initialisieren
model = ConcreteModel()

# Variablen
model.V2_nach_compensation = Var(bounds=(0.9, 1.1))
model.V = Var(range(n), bounds=(0.9, 1.1))
model.P = Var(range(n))
model.Q = Var(range(n))
model.Q_Comp = Var(bounds=(-100, 100))
model.delta_v = Var(bounds=(0, None))
model.I = Var(bounds=(0, None))
model.k = Var(bounds=(-50, 50))
model.k_int = Var(domain=Integers)
model.theta = Var(range(n), bounds=(-math.pi, math.pi))
model.Q_shunt_1 = Var(bounds=(-500, 500))

## Shunt an Bus 4 ist fix? (also ohne k und ohne bounds)
model.Q_shunt_2 = Var(bounds=(-500, 500))

model.a1 = Var(bounds=(0, 50))
model.a2 = Var(bounds=(0, 50))

## Transfrormer only inductive
# a = ü
# B_trafo1 = X/(model.a1**2)
# B_trafo2 = X/(model.a2**2)
B_trafo1 = X/(5**2)
B_trafo2 = X/(10**2)
## Shunt
#B_shunt1 = (model.k * (Q_set_shunt_1/100))
B_shunt1 = (3* (Q_set_shunt_1/100))

#B_shunt2 = (model.k2 * (Q_set_shunt_2/100))
B_shunt2 = (Q_set_shunt_2/100)

## Kabel 
B_kabel1 = B_kabel2 = -1 / X

B_12 = B_21 = - B_kabel1
B_11 = + B_kabel1 
B_22 = B_kabel1 + B_trafo1
B_23 = B_32 = -B_trafo1
B_13 = B_31 = 0
B_14 = B_41 = 0
B_15 = B_51 = 0
B_24 = B_42 = 0
B_25 = B_52 = 0
B_35 = B_53 = 0
B_33 = B_trafo1 + B_shunt1 + B_kabel2
B_34 = B_43 = -B_kabel2
B_44 = B_kabel2 + B_shunt2 + B_trafo2
B_45 = B_54 = -B_trafo2
B_55 = B_trafo2

B_ij_values = [
    [B_11, B_12, B_13, B_14, B_15],
    [B_21, B_22, B_23, B_24, B_25],
    [B_31, B_32, B_33, B_34, B_35],
    [B_41, B_42, B_43, B_44, B_45],
    [B_51, B_52, B_53, B_54, B_55]
]

# G_ij = [
#     [G_11, G_12, G_13, G_14, G_15],
#     [G_21, G_22, G_23, G_24, G_25],
#     [G_31, G_32, G_33, G_34, G_35],
#     [G_41, G_42, G_43, G_44, G_45],
#     [G_51, G_52, G_53, G_54, G_55]
# ]
model.I = RangeSet(n) 

n = 5  # Die Größe Ihrer Matrix

G_ij = [[0 for _ in range(n)] for _ in range(n)]



model.I = RangeSet(n) 

# B_ij als Pyomo-Parameter definieren
model.B_ij = Param(model.I, model.I, initialize=lambda model, i, j: B_ij_values[i-1][j-1])

# G_ij als Pyomo-Parameter definieren
model.G_ij = Param(model.I, model.I, initialize=lambda model, i, j: 0)

# Constraints
model.Spannung_V1 = Constraint(expr=model.V[0] <= V1)
model.Wirkleistung_P1 = Constraint(expr=model.P[0] == P1_pu)
model.Blindleistung_Q1 = Constraint(expr=model.Q[0] <= Q1_pu)
model.Blindleistung_Q2 = Constraint(expr=model.Q[1] <= Q2_pu)
#model.Wirkleistung_P2 = Constraint(expr=model.P[1] >= P2_pu)

#model.Blindleistung_Q2 = Constraint(expr=model.Q[1] <= - Q_statgen_pu + model.k * Q_set_shunt)

model.Compensation = Constraint(expr=model.Q[1] <= Q_statgen_pu - model.Q_shunt_1)
model.tap_adjustment = Constraint(expr=model.Q_shunt_1 <= model.k * Q_set_shunt_1)

model.Compensation = Constraint(expr=model.Q[1] <= Q_statgen_pu - model.Q_shunt_2)
model.tap_adjustment = Constraint(expr=model.Q_shunt_2 <= model.k * Q_set_shunt_2)

model.delta_v_1 = Constraint(expr=model.delta_v >= model.V[1] - V2_target)
model.delta_v_2 = Constraint(expr=model.delta_v >= V2_target - model.V[1])
# model.k_int_1 = Constraint(expr=model.k_int <= model.k)
# model.k_int_2 = Constraint(expr=model.k - model.k_int <= 1)
model.theta_0 = Constraint(expr=model.theta[0] == 0)

# Definieren Sie die Entscheidungsvariablen (falls noch nicht definiert)
model.P = Var(model.I, within=Reals)
model.Q = Var(model.I, within=Reals)
model.theta = Var(model.I, within=Reals, bounds=(-math.pi, math.pi))
model.V = Var(model.I, within=NonNegativeReals)

# model.I = RangeSet(n)

# # Definieren Sie die Constraint-Regeln
# def Q_constraint_rule(model, i):
#     return model.Q[i] == sum(model.V[j] * (model.G_ij[i,j] * sin(model.theta[i] - model.theta[j]) - model.B_ij[i,j] * cos(model.theta[i] - model.theta[j])) for j in model.I)

# def P_constraint_rule(model, i):
#     return model.P[i] == sum(model.V[j] * (model.G_ij[i,j] * cos(model.theta[i] - model.theta[j]) + model.B_ij[i,j] * sin(model.theta[i] - model.theta[j])) for j in model.I)

n = 5  # Die Größe Ihrer Matrix
# ...

# Definieren Sie die Constraint-Listen
model.Q_constraints = ConstraintList()
model.P_constraints = ConstraintList()

# Definieren Sie die Constraint-Regeln
def Q_constraint_rule(model, i):
    return model.Q[i] == sum(model.V[j] * (0 * sin(model.theta[i] - model.theta[j]) - model.B_ij[i,j] * cos(model.theta[i] - model.theta[j])) for j in range(1, n+1))

def P_constraint_rule(model, i):
    return model.P[i] == sum(model.V[j] * (0 * cos(model.theta[i] - model.theta[j]) + model.B_ij[i,j] * sin(model.theta[i] - model.theta[j])) for j in range(1, n+1))

# Fügen Sie die Constraints zum Modell hinzu
for i in range(1, n+1):
    model.Q_constraints.add(Q_constraint_rule(model, i))
    model.P_constraints.add(P_constraint_rule(model, i))




# Fügen Sie die Constraints zum Modell hinzu
model.Q_constraints = Constraint(model.I, rule=Q_constraint_rule)
model.P_constraints = Constraint(model.I, rule=P_constraint_rule)

# Zielsetzung
model.objective = Objective(expr=model.delta_v, sense=minimize)

#model.write('model.nl')
# Modell lösen
solver = SolverFactory('ipopt')
solver.solve(model)

# Lösung des Modells
results = solver.solve(model, tee=True)
# Ergebnisse abrufen
if results.solver.status == SolverStatus.ok and results.solver.termination_condition == TerminationCondition.optimal:
    print("Optimale Lösung gefunden:")
    print("V2 nach Kompensation: ", model.V[1].value)
    print("k: ", model.k.value)
    #print("k_int: ", model.k_int.value)
elif results.solver.termination_condition == TerminationCondition.infeasible:
    print("Keine optimale Lösung gefunden. Modell ist unzulässig.")
    