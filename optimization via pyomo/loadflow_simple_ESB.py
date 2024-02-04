from pyomo.environ import *
import cmath
import math

# Netzwerkparameter
P1 = -100  # MW
Q1 = 30  # Mvar
P2 = -100  # MW
Q2 = 100  # Mvar
V1 = 1.03  # p.u.
l = 1  # km

# Netzwerkparameter - Kabel 
X_prime = 12.8  # Ohm/km
n = 2
X = X_prime * l

# Netzwerkspezifische Loads/Generators
V1 = 1.03  # p.u.
V2_target = 1.05  # p.u.
P1_pu = P1/100  # p.u.
Q1_pu = Q1/100  # p.u.
P2_pu = P2/100  # p.u.
Q2_pu = Q2/100  # p.u.
Q_set_shunt = 10/100  # MVar
Q_statgen = 80  # MVar
Q_statgen_pu = Q_statgen/100  # p.u.
# Modell initialisieren
model = ConcreteModel()

# Variablen
#model.V2_nach_compensation = Var(bounds=(0.9, 1.1))
model.V = Var(range(n), bounds=(0.9, 1.1))
model.P = Var(range(n))
model.Q = Var(range(n))
model.Q_Comp = Var(bounds=(-100, 100))
model.delta_v = Var(bounds=(0, None))
model.I = Var(bounds=(0, None))
#model.k = Var(bounds=(1e-5, 10))  # Nur einmal definieren
model.k = Var(domain=Integers, bounds=(1, 10))
model.k_int = Var(domain=Integers)
model.theta = Var(range(n), bounds=(-math.pi, math.pi))
model.Q_shunt = Var(bounds=(-500, 500))

## VZS
# Admittanzwerte (nur Imaginärteile, repräsentieren Suszeptanz)
B_12 = B_21 = -1 / X  # Suszeptanz zwischen den Knoten
#B_shunt = ((model.k * 0.1)/1.05**2)  # Kompensations-Suszeptanz am Knoten 2
B_shunt = (model.k * (Q_set_shunt/100))
#B_20 = 1/ k * X  # Kompensations-Suszeptanz am Knoten 2
# Berechnung der Suszeptanzwerte der Admittanzmatrix
B_11 = -B_12  # Suszeptanz für Knoten 1
B_22 = B_21 + B_shunt  # Suszeptanz für Knoten 2

# Realteil der Admittanzmatrix (G_ij) ist 0, da kein Widerstand vorhanden ist
G_ij = [[0, 0], [0, 0]]

# Imaginärteil der Admittanzmatrix (B_ij) ist die Suszeptanzmatrix
B_ij = [[B_11, B_12], [B_12, B_22]]


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
# model.k_int_1 = Constraint(expr=model.k_int <= model.k)
# model.k_int_2 = Constraint(expr=model.k - model.k_int <= 1)
model.theta_0 = Constraint(expr=model.theta[0] == 0)

model.Q2 = Constraint(expr=model.Q[1] == model.V[1]*(G_ij[1][0]*sin(model.theta[1]-model.theta[0])-model.V[0]*B_ij[1][0]*cos(model.theta[1]-model.theta[0])) - B_ij[1][1]*cos(0) + G_ij[1][1]*sin(0))
model.Q1 = Constraint(expr=model.Q[0] == V1*(G_ij[1][0]*sin(model.theta[1]-model.theta[0])-B_ij[1][0]*cos(model.theta[1]-model.theta[0])) - B_ij[0][1])

model.P2 = Constraint(expr=model.P[1] == model.V[1]*(B_ij[1][0]*sin(model.theta[1]-model.theta[0])-G_ij[1][0]*cos(model.theta[1]-model.theta[0])) - G_ij[1][1]*cos(0) + B_ij[1][1]*sin(0))
#model.P1 = Constraint(expr=model.P[0] == V1*(B_ij[1][0]*sin(model.theta[1]-model.theta[0])-G_ij[1][0]*cos(model.theta[1]-model.theta[0])) - G_ij[0][1])
test = 1


# Zielsetzung
model.objective = Objective(expr=model.delta_v, sense=minimize)

model.write('optimization via pyomo\\model.nl', io_options={'symbolic_solver_labels': True})
# Modell lösen
solver = SolverFactory('ipopt')
solver.solve(model)

# Lösung des Modells
results = solver.solve(model, tee=True)

print(model.k.value)
print("B 22",B_22)
print("B 20",B_shunt)
Q_comp = ((model.V[1].value)**2 * B_22)*100
print("Q_comp: ",Q_comp)

Q_comp_vgl = (model.k.value * Q_set_shunt*100)
print("Q_comp_vgl: ",Q_comp_vgl)

# Ergebnisse abrufen
if results.solver.status == SolverStatus.ok and results.solver.termination_condition == TerminationCondition.optimal:
    print("Optimale Lösung gefunden:")
    print("V2 nach Kompensation: ", model.V[1].value)
    print("k: ", model.k.value)
    #print("k_int: ", model.k_int.value)
elif results.solver.termination_condition == TerminationCondition.infeasible:
    print("Keine optimale Lösung gefunden. Modell ist unzulässig.")
    
