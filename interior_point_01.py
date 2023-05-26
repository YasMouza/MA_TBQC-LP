from main_powerfactory import PowerFactory
from loadflow import LoadFlow
import math
import pandas as pd
import matplotlib.pyplot as plt
import gurobipy as gp
from gurobipy import GRB
import numpy as np
import pyomo
from pyomo.environ import ConcreteModel, Set, Var, Objective, Constraint, SolverFactory


# 1. ACloadflow
path = r'C:\Program Files\DIgSILENT\PowerFactory 2023 SP3A\Python\3.9'
pf = PowerFactory(path)
project_name = 'TBQC'
app = pf.open_app(project_name)
ldf_ac = LoadFlow(app)
ldf_ac.run()

# 1.1 Grid parameters
Sbase = 100
# 1.2 Line parameters
line_all = app.GetCalcRelevantObjects('*.ElmLne')
line_names = []
xpu = []
rpu = []


#write a optimisation function with ipopt to get the optimal power flow from AC power flow
# 1.3 Transformer parameters
trafo_all = app.GetCalcRelevantObjects('*.ElmTr2')
trafo_names = []
xpu_trafo = []
rpu_trafo = []
for trafo in trafo_all:
    trafo_names.append(trafo.loc_name)
    xpu_trafo.append(trafo.xpu)
    rpu_trafo.append(trafo.rpu)
trafo_df = pd.DataFrame({'name': trafo_names, 'xpu': xpu_trafo, 'rpu': rpu_trafo})
trafo_df = trafo_df.set_index('name')
# 1.4 Bus parameters
bus_all = app.GetCalcRelevantObjects('*.ElmTerm')
bus_names = []
bus_voltages = []
bus_angles = []
for bus in bus_all:
    bus_names.append(bus.loc_name)
    bus_voltages.append(bus.GetAttribute('m:u'))
    bus_angles.append(bus.GetAttribute('m:phi'))
bus_df = pd.DataFrame({'name': bus_names, 'voltage': bus_voltages, 'angle': bus_angles})
bus_df = bus_df.set_index('name')
# 1.5 Generator parameters
gen_all = app.GetCalcRelevantObjects('*.ElmGenstat')
gen_names = []
gen_p = []
gen_q = []
for gen in gen_all:
    gen_names.append(gen.loc_name)
    gen_p.append(gen.GetAttribute('m:P'))
    gen_q.append(gen.GetAttribute('m:Q'))
gen_df = pd.DataFrame({'name': gen_names, 'p': gen_p, 'q': gen_q})
gen_df = gen_df.set_index('name')
# 1.6 Load parameters
load_all = app.GetCalcRelevantObjects('*.ElmLod')
load_names = []
load_p = []
load_q = []
for load in load_all:
    load_names.append(load.loc_name)
    load_p.append(load.GetAttribute('m:P'))
    load_q.append(load.GetAttribute('m:Q'))
load_df = pd.DataFrame({'name': load_names, 'p': load_p, 'q': load_q})
load_df = load_df.set_index('name')
# 1.7 Shunt parameters
shunt_all = app.GetCalcRelevantObjects('*.ElmShnt')
shunt_names = []
shunt_p = []
shunt_q = []
for shunt in shunt_all:
    shunt_names.append(shunt.loc_name)
    shunt_p.append(shunt.GetAttribute('m:P'))
    shunt_q.append(shunt.GetAttribute('m:Q'))
shunt_df = pd.DataFrame({'name': shunt_names, 'p': shunt_p, 'q': shunt_q})
shunt_df = shunt_df.set_index('name')

#2. optimizaiton function 

num_nodes = 2
num_branches = 1
G = np.array([[0.1]])
B = np.array([[0.2]])
P_load = np.array([100, 200])
Q_load = np.array([50, 80])

# Modell erstellen
model = ConcreteModel()

# Sets
model.Nodes = Set(initialize=range(num_nodes))
model.Branches = Set(initialize=range(num_branches))

# Variablen
model.P = Var(model.Nodes, within=Reals, initialize=0.0)
model.Q = Var(model.Nodes, within=Reals, initialize=0.0)
model.V = Var(model.Nodes, within=NonNegativeReals, initialize=1.0)

# Zielfunktion
model.obj = Objective(expr=sum(model.P[node] for node in model.Nodes), sense=maximize)

# Leistungsgleichungen
model.PowerBalanceActive = Constraint(model.Nodes, rule=lambda model, node: 
                                      model.P[node] == sum(model.V[node]*model.V[j]*(G[node,j]*np.cos(model.theta[node]-model.theta[j]) + 
                                                                                            B[node,j]*np.sin(model.theta[node]-model.theta[j]))
                                                           for j in model.Nodes))

model.PowerBalanceReactive = Constraint(model.Nodes, rule=lambda model, node: 
                                        model.Q[node] == sum(model.V[node]*model.V[j]*(G[node,j]*np.sin(model.theta[node]-model.theta[j]) - 
                                                                                              B[node,j]*np.cos(model.theta[node]-model.theta[j]))
                                                             for j in model.Nodes))

# Constraints
model.LoadConstraintsActive = Constraint(model.Nodes, rule=lambda model, node: 
                                         model.P[node] == P_load[node])

model.LoadConstraintsReactive = Constraint(model.Nodes, rule=lambda model, node: 
                                           model.Q[node] == Q_load[node])

# Solver instanziieren
solver = SolverFactory('ipopt')

# Modell lösen
results = solver.solve(model, tee=True)

# Ergebnisse abrufen
if results.solver.termination_condition == TerminationCondition.optimal:
    print("Optimierung erfolgreich!")
    print("Optimale Zielfunktionswert:", model.obj())
    print("Optimale P-Werte:", [model.P[node]() for node in model.Nodes])
    print("Optimale Q-Werte:", [model.Q[node]() for node in model.Nodes])
    print("Optimale V-Werte:", [model.V[node]() for node in model.Nodes])
else:
    print("Optimierung nicht erfolgreich.")


