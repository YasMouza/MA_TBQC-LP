##### R als Cable Widerstand eingefügt #####
#### Busbar 1, 2, 3, 4, 5:
### Busbar1 -- Trafo1 -- Busbar2 -- Shunt_fix - Cable(pi) - Shunt_var -- Busbar3 -- Trafo2 -- Busbar4 -- Netzstärke --- Busbar 5

from pyomo.environ import *
import cmath
import math
import pandas as pd

# Netzwerkparameter
n = 5 # 5 Alpha Ventus

### Bus 1
P1 = 100  # MW
Q1 = 50  # Mvar
P1_pu = 1  # p.u.
Q1_pu = 0.4  # p.u.
X_tr1 = 20.97/100 # Ohm

### Bus 2
P2 = -100  # MW
Q2 = 30  # Mvar
P2_pu = -1.0  # p.u.
Q2_pu = 0.3  # p.u.
Q_shunt_fix = 2 # p.u
V2_target = 1.05  # p.u.

## Bus 2 ---> Bus 3 
l = 70  # km
C_prime = 280e-9  # Farad/km
C = C_prime * l
X_prime = 0.123  # Ohm/km
X_cab = X_prime*l # Ohm/km
omega = 2 * cmath.pi * 50  # Kreisfrequenz für 50 Hz
B = C * omega

### Bus 3
Q_shunt_var = 0.4 # p.u
Q_set_shunt = 0.3 # p.u
X_tr2 = 0.15*(75/100) # p.u
X_tr2 = 0.6

### Bus 4
Xe = 24.2/100 # Ohm ---> Strong grid equivalent 

### Bus 5
V5 = 1.03  # p.u.
theta_slack = 0
results_list = []  # Liste zum Speichern der Ergebnisse
results_df = pd.DataFrame()

# Modell initialisieren
model = ConcreteModel()

# Variablen
model.V2_nach_compensation = Var(bounds=(0.98, 1.08))
model.V = Var(range(n), bounds=(0.95, 1.1))
model.P = Var(range(n))
model.Q = Var(range(n))
model.delta_v = Var(within=NonNegativeReals)

model.theta = Var(range(n), bounds=(-math.pi, math.pi))
#model.Q_shunt_var = Var(range(1), bounds = (-2, 2))

model.t1 = Var(bounds=(-10, 10))
model.t2 = Var(bounds=(-10, 10))
model.k = Var(bounds=(0, 1))

l = 70  # km
C_prime = 280e-9  # Farad/km
C = C_prime * l
X_prime = 0.123  # Ohm/km
X_cab = X_prime*l # Ohm/km

omega = 2 * cmath.pi * 50  # Kreisfrequenz für 50 Hz
B = C * omega

X_sv = (110000**2)/100e6  # Q_variable_shunt 60 MVAr
X_sv_pu = X_sv/100
#B_sv = 1/(model.k*X_sv_pu)
#q_Lr = 35e6
q_Lr = 0.35 #p.u
B_sv = 1/model.k*q_Lr
B_sf = 0.35 # p.u (fixed shunt on Busbar 2)
B_cable_c = (omega*C)/2 * (110000**2)/100e6 ### Bezugsscheileistung prüfen
B_cable_ind = 1/X_cab
Y_t1 = 1/0.13
Y_t2 = 1/0.15
R = 0.128*l

# Berechnung von G und B aufgrund von R und X_cab
G = R / (R**2 + X_cab**2)
B_cable_x = -X_cab / (R**2 + X_cab**2)
B_cable_total = B_cable_x + B_cable_c
Y_cable = complex(G, B_cable_total)

#### System - KAM
B_11 = 1/X_tr1 + ((1+ model.t1*1.25)/1)*Y_t1
B_12 = B_21 = - ((1+ model.t1*1.25)/1)*Y_t1
model.B_22 = Var()
def B_22_rule(model):
    return model.B_22 == (1/X_tr1)**2*Y_t1 + B_sf + B_cable_total - G + ((1 + model.t1 * 1.25) / 1) * Y_t1
model.B_22_constraint = Constraint(rule=B_22_rule)
G_22 = G
B_23 = B_32 = 0
G_23 = G_32 = -G
B_13 = B_31 = 0
model.B_33 = Var()
def B_33_rule(model):
    return B_cable_total + ((1+ model.t2*1.25)/1)*Y_t2 + 1/X_tr2 +  1/model.k*q_Lr
model.B_33_constraint = Constraint(rule=B_22_rule)   
G_33 = G 
B_14 = B_41 = 0
B_24 = B_42 = 0
B_34 = B_43 = -((1+ model.t2*1.25)/1)*Y_t2
B_44 = (1/X_tr2)**2*Y_t2 + 1/Xe + ((1+ model.t2*1.25)/1)*Y_t2
B_15 = B_51 = 0
B_25 = B_52 = 0
B_35 = B_53 = 0
B_45 = B_54 = -1/Xe
B_55 = 1/Xe

### Admittanzmatritzen
G_11 = G_12 = G_21 = G_13 = G_31 = G_24 = G_42 = G_44 = G_43 = G_34 = G_45 = G_54 = G_55 = 0
G_ij = [0,0,0,0,0],[0,G_22,G_23,0,0],[0,G_32,0,0,0],[0,0,0,0,0],[0,0,0,0,0]
B_ij = [B_11, B_12, B_13, B_14, B_15], [B_21 , model.B_22, B_23, B_24, B_25], [B_31, B_32, model.B_33, B_34, B_35] , [B_41, B_42, B_43, B_44, B_45],  [B_51, B_52, B_53, B_54, B_55]
print(B_ij)


model.Spannung_V5 = Constraint(expr=model.V[4] == V5)
model.Blindleistung_Q1 = Constraint(expr=model.Q[0] == Q1_pu)
model.Blindleistung_P1 = Constraint(expr=model.P[0] == P1_pu)
model.theta_slack = Constraint(expr=model.theta[4] == theta_slack)   ### theta_slack = 0

model.Q1 = Constraint(expr=model.Q[0] == (model.V[0]*model.V[1]*(G_12*sin(model.theta[0]-model.theta[1]) - B_12*cos(model.theta[0]-model.theta[1])) + model.V[0]*model.V[0]*(G_11*sin(model.theta[0] - model.theta[0]) - B_11*cos(model.theta[0]-model.theta[0]))))
model.Q2 = Constraint(expr=model.Q[1] == (model.V[0]*model.V[1]*(G_12*sin(model.theta[0]-model.theta[1]) - B_12*cos(model.theta[0]-model.theta[1])) + model.V[1]*model.V[2]*(G_23*sin(model.theta[1]-model.theta[2]) - B_23*cos(model.theta[1]+model.theta[2])) + model.V[1]*model.V[1]*(G_22*sin(model.theta[1]-model.theta[1]) - model.B_22*cos(model.theta[1]-model.theta[1]))))
model.Q3 = Constraint(expr=model.Q[2] == (model.V[1]*model.V[2]*(G_23*sin(model.theta[1]-model.theta[2]) - B_23*cos(model.theta[1]-model.theta[2])) + model.V[2]*model.V[3]*(G_34*sin(model.theta[2]-model.theta[3]) - B_34*cos(model.theta[2]+model.theta[3])) + model.V[2]*model.V[2]*(G_33*sin(model.theta[2]-model.theta[2]) - model.B_33*cos(model.theta[2]-model.theta[2]))))
model.Q4 = Constraint(expr=model.Q[3] == -model.V[3]*model.V[2]*B_34*cos(model.theta[2]-model.theta[3]) - model.V[3]*model.V[4]*B_45*cos(model.theta[3]-model.theta[4]) - model.V[3]*model.V[3]*B_44*cos(model.theta[3]-model.theta[3]))
model.Q5 = Constraint(expr=model.Q[4] == -model.V[4]*model.V[3]*B_45*cos(model.theta[3]-model.theta[4]) - model.V[4]*model.V[4]*B_55*cos(model.theta[4]-model.theta[4]))

model.P1 = Constraint(expr=model.P[0] == model.V[0]*model.V[1]*B_12*sin(model.theta[0]-model.theta[1]) + model.V[0]*model.V[0]*B_11*sin(model.theta[0]-model.theta[0]))
model.P2 = Constraint(expr=model.P[1] == model.V[0]*model.V[1]*B_12*sin(model.theta[0]-model.theta[1]) + model.V[1]*model.V[2]*(G_23*cos(model.theta[1]-model.theta[2])+B_23*sin(model.theta[1]-model.theta[2])) + model.V[1]*model.V[1]*(G_22*cos(model.theta[1]-model.theta[1]) + model.B_22*sin(model.theta[1]-model.theta[1]))) 
model.P3 = Constraint(expr=model.P[2] == model.V[1]*model.V[2]*(G_23*cos(model.theta[1]-model.theta[2]) + B_23*sin(model.theta[1]-model.theta[2])) + model.V[2]*model.V[3]*B_34*sin(model.theta[2]-model.theta[3]))
model.P4 = Constraint(expr=model.P[3] == model.V[2]*model.V[3]*B_34*sin(model.theta[2]-model.theta[3]) + model.V[3]*model.V[4]*B_45*sin(model.theta[3]-model.theta[4]))
model.P5 = Constraint(expr=model.P[4] == model.V[3]*model.V[4]*B_45*sin(model.theta[3]-model.theta[4]))

model.delta_v_pos = Constraint(expr=model.delta_v >= model.V[1] - V2_target)
model.delta_v_neg = Constraint(expr=model.delta_v >= V2_target - model.V[1])

# Min. abs(v1-v2)
model.objective = Objective(expr=model.delta_v, sense=minimize)
#model.objective = Objective(expr=model.t1, sense=maximize)
#model.objective = Objective(expr=model.t2, sense=maximize)
#model.objective = Objective(expr=model.k, sense=maximize)

# Solve via Interior Point Optimizer
solver = SolverFactory('ipopt')
solver.solve(model, tee=True)
solver.solve(model)

results = solver.solve(model, tee=True)

#### Display Results
if results.solver.status == SolverStatus.ok and results.solver.termination_condition == TerminationCondition.optimal:
    print("Optimale Lösung gefunden:")
    print("V2 nach Kompensation: ", model.V[1].value)
    print("t1: ", model.t1.value)
    print("t2: ", model.t2.value)
    print("k: ", model.k.value)
    print("Q1:", model.Q[0].value)
    print("Q2:", model.Q[1].value)
    #print("Q_shunt_var: ", model.Q_shunt_var[0].value)
elif results.solver.termination_condition == TerminationCondition.infeasible:
    print("Keine optimale Lösung gefunden. Modell ist unzulässig.")
    
# Erstellen eines leeren DataFrames
df = pd.DataFrame(columns=['Busbar', 'P', 'Q', 'V', 'Theta'])
for i in range(n):  
    df = df.append({
        'Busbar': f'Busbar {i+1}',
        'P': model.P[i].value if hasattr(model.P[i], 'value') else None, 
        'Q': model.Q[i].value if hasattr(model.Q[i], 'value') else None, 
        'V': model.V[i].value if hasattr(model.V[i], 'value') else None, 
        'Theta': (model.theta[i].value * (180 / math.pi)) if hasattr(model.theta[i], 'value') else None  # Umrechnung von Radiant in Grad
        },
    ignore_index = True)                   
print(df)