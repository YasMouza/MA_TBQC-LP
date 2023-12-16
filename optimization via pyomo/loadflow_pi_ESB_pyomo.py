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

# Hilfsfunktionen zur Extraktion von Real- und Imaginärteilen
def Y_real(Y):
    return Y.real

def Y_imag(Y):
    return Y.imag

# Admittanzwerte
Y_12 = Y_21 = -1 / (R + 1j * X)  # Nicht-Diagonalelemente, negativ
Y_10 = 1j * omega * C / 2  # Shunt-Admittanz am Knoten 1, positiv

# Y_20 als reiner Imaginärteil
Y_20_imag = B / 2 - model.k * X

# Berechnung der Real- und Imaginärteile der Admittanzmatrix
Y_11 = -(Y_12 + Y_10)  # Diagonalelement für Knoten 1, positiv

Y_11_real = Expression(expr=Y_real(Y_11))
Y_11_imag = Expression(expr=Y_imag(Y_11))
Y_12_real = Expression(expr=Y_real(Y_12))
Y_12_imag = Expression(expr=Y_imag(Y_12))
Y_22_real = Expression(expr=-(Y_real(Y_12)))  # Realteil
Y_22_imag = Expression(expr=-(Y_imag(Y_12) + Y_20_imag))  # Imaginärteil

# Real- und Imaginärteil der Admittanzmatrix
G_ij = [[Y_11_real, Y_12_real], [Y_12_real, Y_22_real]]
B_ij = [[Y_11_imag, Y_12_imag], [Y_12_imag, Y_22_imag]]

print(G_ij)
print(B_ij)
# Ausgabe der Werte
# Berechnung der Real- und Imaginärteile
Y_11_real = Y_real(Y_11)
Y_11_imag = Y_imag(Y_11)
Y_12_real = Y_real(Y_12)
Y_12_imag = Y_imag(Y_12)
Y_22_real = Y_real(Y_22_real)
Y_22_imag = Y_imag(Y_22_imag)


# Ausgabe der Werte
print("Y_11_real:", Y_11_real)
print("Y_11_imag:", Y_11_imag)
print("Y_12_real:", Y_12_real)
print("Y_12_imag:", Y_12_imag)
#print("Y_20_real:", Y_20_real)
print("Y_20_imag:", Y_20_imag)
print("Y_22_real:", Y_22_real)
print("Y_22_imag:", Y_22_imag)

model.Spannung_V1 = Constraint(expr=model.V[0] <= V1)
model.Wirkleistung_P1 = Constraint(expr=model.P[0] == P1_pu)
model.Blindleistung_Q1 = Constraint(expr=model.Q[0] <= Q1_pu)
model.Wirkleistung_P2 = Constraint(expr=model.P[1] >= P2_pu)
model.Blindleistung_Q2 = Constraint(expr=model.Q[1] == Q2_pu + model.k * Q_set_shunt)
model.delta_v_1 = Constraint(expr=model.delta_v >= model.V[1] - V2_target)
model.delta_v_2 = Constraint(expr=model.delta_v >= V2_target - model.V[1])
model.k_int_1 = Constraint(expr=model.k_int <= model.k)
model.k_int_2 = Constraint(expr=model.k - model.k_int <= 1)
model.theta_0 = Constraint(expr=model.theta[0] == 0)

# Annahme, dass V, theta, P, Q bereits als Pyomo-Variablen definiert sind
# und G_ij, B_ij sind definierte Parameter oder Ausdrücke

model.Q2 = Constraint(expr=model.Q[1] == V2_target*(G_ij[1][0]*sin(model.theta[1]-model.theta[0])-B_ij[1][0]*cos(model.theta[1]-model.theta[0])) - B_ij[1][1]*cos(0) + G_ij[1][1]*sin(0))
model.Q1 = Constraint(expr=model.Q[0] == V1*(G_ij[1][0]*sin(model.theta[0]-model.theta[0])-B_ij[1][0]*cos(model.theta[1]-model.theta[0])) - B_ij[0][1])

model.P2 = Constraint(expr=model.P[1] == V2_target*(B_ij[1][0]*sin(model.theta[1]-model.theta[0])-G_ij[1][0]*cos(model.theta[1]-model.theta[0])) - G_ij[1][1]*cos(0) + B_ij[1][1]*sin(0))
#model.P1 = Constraint(expr=model.P[0] == V1*(B_ij[1][0]*sin(model.theta[1]-model.theta[0])-G_ij[1][0]*cos(model.theta[1]-model.theta[0])) - G_ij[0][1])


# Zielsetzung
model.objective = Objective(expr=model.delta_v, sense=minimize)

# Modell lösen
solver = SolverFactory('ipopt')
solver.solve(model)

# Lösung des Modells
results = solver.solve(model, tee=True)

# Ergebnisse abrufen
if results.solver.status == SolverStatus.ok and results.solver.termination_condition == TerminationCondition.optimal:
    print("Optimale Lösung gefunden:")
    print("V2_nach_compensation: ", model.V2_nach_compensation.value)
    print("k: ", model.k.value)
    print("k_int: ", model.k_int.value)
    print("Q_Comp: ", model.Q_Comp.value)
elif results.solver.termination_condition == TerminationCondition.infeasible:
    print("Keine optimale Lösung gefunden. Modell ist unzulässig.")
else:
    print("Keine optimale Lösung gefunden.")
