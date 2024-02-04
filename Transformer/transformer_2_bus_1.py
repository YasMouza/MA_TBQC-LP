#### Calculation with R = 0 

from pyomo.environ import *
import cmath
import math

# Netzwerkparameter
P1 = 78.7  # MW
Q1 = 1446.2  # Mvar
P2 = -100  # MW
Q2 = 30  # Mvar
V1 = 1.03  # p.u.
l = 70  # km
R_prime = 0.018  # Ohm/km
X_prime = 0.123  # Ohm/km
C_prime = 280e-9  # Farad/km
n = 2
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
Q_set_shunt = 10/100  # MVar
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
model.Q_shunt = Var(bounds=(-500, 500))

model.t = Var(bounds=(-10, 10))

## VZS
#t = Übersetzungsverhältnis
# Admittanzwerte (nur Imaginärteile, repräsentieren Suszeptanz)

B_12 = B_21 = - ((1+ model.t*1.25)/1)
B_11 =  1/X
B_22 = (1/X)**2

# B_12 = B_21 = -1 / X  # Suszeptanz zwischen den Knoten
# #B_shunt = ((model.k * 0.1)/1.05**2)  # Kompensations-Suszeptanz am Knoten 2
# B_shunt = (model.k * (Q_set_shunt/100))
# B_10 = (omega*C)/2 * (110000*2)/120e6
# #B_20 = 1/ k * X  # Kompensations-Suszeptanz am Knoten 2
# # Berechnung der Suszeptanzwerte der Admittanzmatrix
# B_11 = -B_12 + B_10 # Suszeptanz für Knoten 1
# B_22 = B_21 + B_shunt + B_10  # Suszeptanz für Knoten 2

# Realteil der Admittanzmatrix (G_ij) ist 0, da kein Widerstand vorhanden ist
G_ij = [[0, 0], [0, 0]]

# Imaginärteil der Admittanzmatrix (B_ij) ist die Suszeptanzmatrix
B_ij = [[B_11, B_12], [B_12, B_22]]
print(B_ij)

# Constraints
model.Spannung_V1 = Constraint(expr=model.V[0] <= V1)
model.Wirkleistung_P1 = Constraint(expr=model.P[0] == P1_pu)
model.Blindleistung_Q1 = Constraint(expr=model.Q[0] <= Q1_pu)
model.Blindleistung_Q2 = Constraint(expr=model.Q[1] <= Q2_pu)
#model.Wirkleistung_P2 = Constraint(expr=model.P[1] >= P2_pu)

#model.Blindleistung_Q2 = Constraint(expr=model.Q[1] <= - Q_statgen_pu + model.k * Q_set_shunt)

model.Compensation = Constraint(expr=model.Q[1] <= Q_statgen_pu - model.Q_shunt)
model.tap_adjustment = Constraint(expr=model.Q_shunt <= model.k * Q_set_shunt)

model.delta_v_1 = Constraint(expr=model.delta_v >= model.V[1] - V2_target)
model.delta_v_2 = Constraint(expr=model.delta_v >= V2_target - model.V[1])

model.theta_0 = Constraint(expr=model.theta[0] == 0)

model.Q2 = Constraint(expr=model.Q[1] == model.V[1]*(G_ij[1][0]*sin(model.theta[1]-model.theta[0])-B_ij[1][0]*cos(model.theta[1]-model.theta[0])) - B_ij[1][1]*cos(0) + G_ij[1][1]*sin(0))
#model.Q1 = Constraint(expr=model.Q[0] == V1*(G_ij[1][0]*sin(model.theta[0]-model.theta[0])-B_ij[1][0]*cos(model.theta[1]-model.theta[0])) - B_ij[0][1])

model.P2 = Constraint(expr=model.P[1] == model.V[1]*(B_ij[1][0]*sin(model.theta[1]-model.theta[0])-G_ij[1][0]*cos(model.theta[1]-model.theta[0])) - G_ij[1][1]*cos(0) + B_ij[1][1]*sin(0))
#model.P1 = Constraint(expr=model.P[0] == V1*(B_ij[1][0]*sin(model.theta[1]-model.theta[0])-G_ij[1][0]*cos(model.theta[1]-model.theta[0])) - G_ij[0][1])
test = 1


# Zielsetzung
model.objective = Objective(expr=model.delta_v, sense=minimize)

#model.write('optimization via pyomo\\model.nl', io_options={'symbolic_solver_labels': True})
# Modell lösen
solver = SolverFactory('ipopt')
solver.solve(model)

# Lösung des Modells
results = solver.solve(model, tee=True)

Q_comp_vgl = (model.k.value * Q_set_shunt*100)
print("Q_comp_vgl: ",Q_comp_vgl)

# Ergebnisse abrufen
if results.solver.status == SolverStatus.ok and results.solver.termination_condition == TerminationCondition.optimal:
    print("Optimale Lösung gefunden:")
    print("V2 nach Kompensation: ", model.V[1].value)
    print("t: ", model.t.value)
elif results.solver.termination_condition == TerminationCondition.infeasible:
    print("Keine optimale Lösung gefunden. Modell ist unzulässig.")
    

