import gurobipy as gp
from gurobipy import GRB
import sys
sys.path.append("C:\\Users\\yasin\\source\\MA_TBQC LP")
from main_powerfactory import PowerFactory
from loadflow import LoadFlow
import pandas as pd

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

shunt = app.GetCalcRelevantObjects('*.ElmShnt')
reactor = shunt[1] 
capacitor = shunt[0]
print(reactor.loc_name)
print(capacitor.loc_name)


results_df = pd.DataFrame(columns=['q2', 'Q1','Q_shunt', 'delta_Q', 'k', 'Q2', 'V2_pu'])   # Dataframe für Berechnungen
results_pf = pd.DataFrame(columns=['q2', 'Q1', 'Q_shunt', 'delta_Q', 'Kompensationstyp'])  # Dataframe für Werte aus PF

q2_values_stat_gen = [-50, 50, 75, 100]  # Values of static Generator

Q_shunt_set = 20

for q2 in q2_values_stat_gen:
    stat_gen[0].qgini = q2
    reactor.outserv = 1  # Induktivität abschalten
    capacitor.outserv = 1  # Kapazität abschalten  
    ldf_ac.run()
    ldf_ac.iopt_asht = 1
    
    Q1 = bus1.GetAttribute('m:Qflow') #Q1 ohne Kompensation
    V1 = bus1.GetAttribute('m:Ul')
    V2 = bus2.GetAttribute('m:Ul')
    V1_pu = bus1.GetAttribute('m:u')
    V2_pu = bus2.GetAttribute('m:u')

    # Initialisieren Sie das Modell
    model = gp.Model("Blindleistungsoptimierung")
    model.params.NonConvex = 2
    model.params.Method = 2
    
    # Variablen
    Q2 = model.addVar(lb=-100, ub=100, name="Q2") 
    P2 = model.addVar(lb=-100, ub=100, name="P2") 
    V2_pu = model.addVar(lb=1.05, ub=1.1, name="V2")
    delta_Q = model.addVar(lb=-100, ub=100, name="delta_Q")
    k = model.addVar(vtype=GRB.INTEGER, lb=-250, ub=250, name="k")
    
    #k = Q_shunt/Q_shunt_set
    
    model.addConstr(V2_pu <= V2_max, "V2_max")
    model.addConstr(V2_pu >= V2_min, "V2_min")
    
    # Constraints
    model.addConstr(V1_pu * Q1 + 1/B == Q2 * V2_pu, "Leistungsfluss_Q2")
    model.addConstr(B*V2 * (V2 - V2_target) - k*Q_shunt_set == 0, "Kompensationsblindleistung, um auf 1,05 zu regeln")
    
    
    # Constraints
    model.addConstr(Q2 == Q1 - B * (V1_pu**2 - V1_pu * V2_pu) -delta_Q, "Leistungsfluss_Q2")
    model.addConstr(delta_Q == 20 * k, "Shunt_Blindleistung")
    model.addConstr(V2_pu == V1_pu - B * (Q1 - Q2), "Spannung_V2")

    # Zielfunktion
    model.setObjective(k, GRB.MINIMIZE)

    # Optimierung
    model.optimize()
    model.write("Blindleistungsoptimierung.lp")
    # Überprüfen, ob das Modell erfolgreich gelöst wurde
    if model.status == GRB.OPTIMAL:
        # Ausgabe der Ergebnisse
        print('Optimale kompensierte Blindleistung: %g MVAr' % delta_Q.X)
        print('Optimale Stufe des Shunts: %g' % k.X)
    else:
        print('Optimierung nicht erfolgreich. Statuscode: %d' % model.status)
        
    