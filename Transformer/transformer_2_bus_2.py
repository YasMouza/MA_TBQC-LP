from pyomo.environ import *
import cmath
import math

# Netzwerkparameter
n = 2 # 2 Bus System

P1 = 100  # MW
Q1 = 50  # Mvar
P2 = -100  # MW
Q2 = -30  # Mvar

P1_pu = 1.0  # p.u.
Q1_pu = 0.5  # p.u.
P2_pu = -1.0  # p.u.
Q2_pu = -0.3  # p.u.

Q_shunt_fix = 0.3 # p.u

V1 = 1.03  # p.u.
V2_target = 1.05  # p.u.

X = 96.8 # Ohm

# Modell initialisieren
model = ConcreteModel()

# Variablen
model.V2_nach_compensation = Var(bounds=(0.9, 1.1))
model.V = Var(range(n), bounds=(0.9, 1.1))
model.P = Var(range(n))
model.Q = Var(range(n))
model.delta_v = Var(bounds=(0, None))
model.theta = Var(range(n), bounds=(-math.pi, math.pi))

model.t = Var(bounds=(-10, 10))

#### Trafo - KAM
B_12 = B_21 = - ((1+ model.t*1.25)/1)
B_11 =  1/X
B_22 = (1/X)**2

# Realteil der Admittanzmatrix (G_ij) ist 0, da kein Widerstand vorhanden ist
G_ij = [[0, 0], [0, 0]]

# Imaginärteil der Admittanzmatrix (B_ij) ist die Suszeptanzmatrix
B_ij = [[B_11, B_12], [B_12, B_22]]
print(B_ij)

### Subject To:
# Constraints
model.Spannung_V1 = Constraint(expr=model.V[0] == V1)
model.Wirkleistung_P1 = Constraint(expr=model.P[0] == P1_pu)
model.Blindleistung_Q1 = Constraint(expr=model.Q[0] == Q1_pu)
model.Blindleistung_Q2 = Constraint(expr=model.Q[1] <= Q2_pu)

model.delta_v_1 = Constraint(expr=model.delta_v >= model.V[1] - V2_target)
model.delta_v_2 = Constraint(expr=model.delta_v >= V2_target - model.V[1])

model.theta_0 = Constraint(expr=model.theta[0] == 0)

model.Q2 = Constraint(expr=model.Q[1] == model.V[1]*(G_ij[1][0]*sin(model.theta[1]-model.theta[0])-B_ij[1][0]*cos(model.theta[1]-model.theta[0])) - B_ij[1][1]*cos(0) + G_ij[1][1]*sin(0))
#model.Q1 = Constraint(expr=model.Q[0] == V1*(G_ij[1][0]*sin(model.theta[0]-model.theta[0])-B_ij[1][0]*cos(model.theta[1]-model.theta[0])) - B_ij[0][1])

model.P2 = Constraint(expr=model.P[1] == model.V[1]*(B_ij[1][0]*sin(model.theta[1]-model.theta[0])-G_ij[1][0]*cos(model.theta[1]-model.theta[0])) - G_ij[1][1]*cos(0) + B_ij[1][1]*sin(0))
#model.P1 = Constraint(expr=model.P[0] == V1*(B_ij[1][0]*sin(model.theta[1]-model.theta[0])-G_ij[1][0]*cos(model.theta[1]-model.theta[0])) - G_ij[0][1])

# Min. abs(v1-v2)
model.objective = Objective(expr=model.delta_v, sense=minimize)

# Solve via Interior Point Optimizer
solver = SolverFactory('ipopt')
solver.solve(model)

results = solver.solve(model, tee=True)


#### Display Results
if results.solver.status == SolverStatus.ok and results.solver.termination_condition == TerminationCondition.optimal:
    print("Optimale Lösung gefunden:")
    print("V2 nach Kompensation: ", model.V[1].value)
    print("t: ", model.t.value)
elif results.solver.termination_condition == TerminationCondition.infeasible:
    print("Keine optimale Lösung gefunden. Modell ist unzulässig.")
