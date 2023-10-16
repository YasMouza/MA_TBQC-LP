import gurobipy as gp
from gurobipy import GRB
import sys
sys.path.append("C:\\Users\\yasin\\source\\MA_TBQC LP")
from main_powerfactory import PowerFactory
from loadflow import LoadFlow

# Netzwerkparameter
P1 = 100  # MW
#P2 = -100  # MW

V1_pu = 1.03  # Spannung an Busbar 1 in p.u.
B = 0.08  # Suszeptanz in p.u. (B = 1/X)
V2_min = 1.05  # Mindestspannung an Busbar 2 in p.u.
V2_max = 1.1  # Höchstspannung an Busbar 2 in p.u.
V2_target = 1.05*110

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

V1 = bus1.GetAttribute('m:Ul')
V2 = bus2.GetAttribute('m:Ul')
print('V2 = ', V2)
print('V1 = ', V1)

V1_pu = bus1.GetAttribute('m:u')
V2_pu = bus2.GetAttribute('m:u')

#set bus1 const v 
bus1.av_control = 1
bus1.av_set = 1.03

#set bus2 const q 
bus2.av_control = 2


synch_gen = app.GetCalcRelevantObjects('*.ElmSym')
p_1 = synch_gen[0].GetAttribute('m:P:bus1')
q_1 = synch_gen[0].GetAttribute('m:Q:bus1')

stat_gen = app.GetCalcRelevantObjects('*.ElmGenstat')
p_2 = stat_gen[0].GetAttribute('m:P:bus1')
q_2 = stat_gen[0].GetAttribute('m:Q:bus1')

q2_values_stat_gen = [-50, 50, 75, 100]  # Values of static Generator

for q2 in q2_values_stat_gen:
    #stat_gen.qgini = q2
    stat_gen[0].qgini = q2
    ldf_ac.run()
    ldf_ac.iopt_asht = 1
    
    Q1 = bus1.GetAttribute('m:Qflow') #Q1 ohne Kompensation
    V1 = bus1.GetAttribute('m:Ul')
    V2 = bus2.GetAttribute('m:Ul')
    V1_pu = bus1.GetAttribute('m:u')
    V2_pu = bus2.GetAttribute('m:u')
    
    delta_Q = B*V2*(V2-V2_target)
    Q_shunt = delta_Q/V2_pu**2
    
    Q1 = q2 - Q_shunt
    
    
    # Initialisieren Sie das Modell
    model = gp.Model("Blindleistungsoptimierung")
    model.params.NonConvex = 2
    model.params.Method = 2
    
    # Variablen
    Q2 = model.addVar(lb=-100, ub=100, name="Q2") # Blindleistung an Busbar 2 
    P2 = model.addVar(lb=-100, ub=100, name="P2")  # Wirkleistung an Busbar 2
    V2_pu = model.addVar(lb=V2_min, ub=V2_max, name="V2")
    #k = model.addVar(lb = 0, vtype = GRB.INTEGER, name = "k")
    #Q_comp = model.addVar(lb = -100, ub = 100, name = "Q_comp") # Blindleistung an Busbar 2 (Compensation)

    Q_shunt_set = 30

    # Constraints
    model.addConstr(V1_pu * Q1 + 1/B == Q2 * V2_pu, "Leistungsfluss_Q2")
    #model.addConstr(U1 * P1 - P2 == Q2 * V2, "Leistungsfluss_P2")


    # Zielsetzung
    #model.setObjective(Q2, GRB.MINIMIZE)
    model.setObjective(V2, GRB.MINIMIZE)

    # Optimierung starten
    model.optimize()
    optimal_V2 = V2_pu.x
    optimal_Q2 = Q2.x
    print(Q2.x)

    # Ergebnisse abrufen
    if model.status == GRB.OPTIMAL:
        print("Optimale Lösung gefunden:")
        print(f"Blindleistung Q2 = {Q2.x} MVAr")
        print(f"Spannung V2 = {V2_pu.x} p.u.")
        print(f"Blindleistung Q_statgen = {q2} MVAr")
        if Q_shunt < 0:
            print('Kapazitive Kompensation: ', Q_shunt)
        else:
            print('Induktive Kompensation: ', Q_shunt)
    else:
        print("Das Problem hat keine optimale Lösung gefunden.")

# Modell aufräumen
model.dispose()

