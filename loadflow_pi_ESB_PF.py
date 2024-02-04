import gurobipy as gp
from gurobipy import GRB
import math
import numpy as np
import cmath
from main_powerfactory import PowerFactory
from loadflow import LoadFlow
import pandas as pd

# 1. ACloadflow
path = r'C:\Program Files\DIgSILENT\PowerFactory 2023 SP3A\Python\3.9'
pf = PowerFactory(path)
project_name = '[MA] Equipment Modelling - SVC'
app = pf.open_app(project_name)
ldf_ac = LoadFlow(app)
ldf_ac.run()

#1.1 Grid parameters
Sbase = 100

# Get Values from Powerfactory
bus_all = app.GetCalcRelevantObjects('*.ElmTerm')
bus1 = bus_all[0]
bus2 = bus_all[1]

# Netzwerkparameter
P1 = 100  # MW
Q1 = 50  # Mvar
P2 = -100  # MW
Q2 = 30  # Mvar
V1 = 1.03  # p.u.
V2_target = 1.05  # p.u.
B = 0.08  # p.u.
l = 70  # km
R_prime = 0.018  # Ohm/km
X_prime = 0.123  # Ohm/km
C_prime = 280e-9  # Farad/km
n = 2
R = R_prime * l
X = X_prime * l
C = C_prime * l
omega = 2 * cmath.pi * 50  # Kreisfrequenz für 50 Hz

# Initialisieren Sie das Modell
model = gp.Model("Spannungsoptimierung")
model.params.Method = 2  # Interior-Point-Methode

# Netzwerkspezifische Parameter
V1 = 1.03  # p.u.
V2_target = 1.05  # p.u.
P1_pu = 1.0  # p.u.
Q1_pu = 0.5  # p.u.
P2_pu = -1.0  # p.u.
Q2_pu = 0.5  # p.u.
Q_set_shunt = 10/100  # MVar

# Variablen
V2_nach_compensation = model.addVar(lb=0.9, ub=1.1, name="V2_nach_compensation")
V = model.addVars(n, lb=0.9, ub=1.1, name="V")  # Spannungen
P = model.addVars(n, name="P")  # Wirkleistungen
Q = model.addVars(n, name="Q")  # Blindleistungen
Q_Comp = model.addVar(lb=-100, ub=100, name="Q_Comp")
delta_v = model.addVar(lb=0, ub=GRB.INFINITY, name="delta")
I = model.addVar(lb=0, ub=GRB.INFINITY, name="I")
k = model.addVar(lb=-50, ub=50, name="k")
k_int = model.addVar(vtype=GRB.INTEGER, name="k_int")
theta = model.addVars(n, lb=-math.pi, ub=math.pi, name="theta")  # Phasenwinkel

#### C nur bei Diagonalelementen dabei:
    ## anpassen

Y = 1 / complex(R, X) + complex(0, omega * C)

# Wirk- und Blindleistungsflüsse
G_ij = Y.real
B_ij = Y.imag

print('B: ', B_ij)
print('G: ', G_ij)

# Constraints
for i in range(n):
    for j in range(n):
        if i != j:
            # Hilfsvariablen für Produkte
            VV = model.addVar(name="VV_" + str(i) + "_" + str(j))
            cos_approx = model.addVar(name="cos_approx_" + str(i) + "_" + str(j))
            sin_approx = model.addVar(name="sin_approx_" + str(i) + "_" + str(j))

            # Definition der Hilfsvariablen
            model.addConstr(VV == V[i] * V[j], "VV_def_" + str(i) + "_" + str(j))
            delta_theta = theta[i] - theta[j]
            model.addConstr(cos_approx == 1 - 0.5 * delta_theta * delta_theta, "cos_approx_" + str(i) + "_" + str(j))
            model.addConstr(sin_approx == delta_theta, "sin_approx_" + str(i) + "_" + str(j))

            # Lastflussgleichungen
            model.addConstr(P[i] >= VV * (G_ij * cos_approx + B_ij * sin_approx), "Wirkleistung_" + str(i) + "_" + str(j))
            model.addConstr(Q[i] >= VV * (G_ij * sin_approx - B_ij * cos_approx), "Blindleistung_" + str(i) + "_" + str(j))

#model.addConstr(V1 * Q1 + 1/B == Q2 * V2_nach_compensation + k*Q_set_shunt, "Leistungsfluss_Q2")
#model.addConstr(P2 == V1 * P1 * B - I**2 * R_prime * l, "Leistungsfluss_P2")
model.addConstr(delta_v >= V2_nach_compensation - V2_target, "abs1")
model.addConstr(delta_v >= V2_target - V2_nach_compensation, "abs2")
model.addConstr(k_int <= k, "k_int")
model.addConstr(k - k_int <= 1, "k_int_round_down")

model.addConstr(V[0] <= V1, "Spannung_V1")
model.addConstr(P[0] == P1_pu, "Wirkleistung_P1")
model.addConstr(Q[0] <= Q1_pu, "Blindleistung_Q1")
model.addConstr(P[1] >= P2_pu, "Wirkleistung_P2")
model.addConstr(Q[1] == Q2_pu + k * Q_set_shunt, "Blindleistung_Q2")
0,
model.addConstr(k_int <= k, "k_int_1")
model.addConstr(k - k_int <= 1, "k_int_2")

# Zielsetzung
model.setObjective(delta_v, GRB.MINIMIZE)
model.write('Loadflow-Pi-ESB.lp')
# Optimierung starten
model.params.NonConvex = 2
model.optimize()

# Ergebnisse abrufen

if model.status == GRB.OPTIMAL:
    print("Optimale Lösung gefunden:")
    print("V2_nach_compensation: ", V2_nach_compensation.x)
    print("k: ", k.x)
    print("k_int: ", k_int.x)
    print("Q_Compenstation: ", Q_Comp.x)
else:
    print("Keine optimale Lösung gefunden.")

shunt = app.GetCalcRelevantObjects('*.ElmShnt')
reactor = shunt[1] 
capacitor = shunt[0]
print(reactor.loc_name)
print(capacitor.loc_name)

stat_gen = app.GetCalcRelevantObjects('*.ElmGenstat')
p_2 = stat_gen[0].GetAttribute('m:P:bus1')
q_2 = stat_gen[0].GetAttribute('m:Q:bus1')
print(stat_gen[0].loc_name)

#stat_gen[0].qgini = q2
reactor.outserv = 0  # Induktivität abschalten
capacitor.outserv = 0  # Kapazität abschalten  
ldf_ac.run()
ldf_ac.iopt_asht = 1

Q1 = bus1.GetAttribute('m:Qflow') #Q1 ohne Kompensation
V1 = bus1.GetAttribute('m:Ul')
V2 = bus2.GetAttribute('m:Ul')
V1_pu = bus1.GetAttribute('m:u')
V2_pu = bus2.GetAttribute('m:u')

# Read results from loadflow py powerfactory
Q2_pf = bus2.GetAttribute('m:Qflow') 
reactor_comp = reactor.GetAttribute('m:Q:bus1')
capacitor_comp = capacitor.GetAttribute('m:Q:bus1') 
print('Q2_pf: ', Q2_pf)
print('reactor_comp: ', reactor_comp)
print('capacitor_comp: ', capacitor_comp)
test = 1