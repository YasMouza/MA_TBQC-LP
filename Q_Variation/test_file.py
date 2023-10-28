import gurobipy as gp
from gurobipy import GRB
import sys
sys.path.append("C:\\Users\\yasin\\source\\MA_TBQC LP")
from main_powerfactory import PowerFactory
from loadflow import LoadFlow
import pandas as pd

# Netzwerkparameter
P1 = 100  # MW
R = 0.05  # Ohm (Widerstand der Leitung)
X = 0.1   # Ohm (Reaktanz der Leitung)
C = 0.00001  # F (Kapazitanz der Leitung)

# Admittanz berechnen
Y = 1 / (R + 1j*X)  # Admittanz der Leitung
G = Y.real  # Leitwert
B = Y.imag  # Suszeptanz


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

for q2 in q2_values_stat_gen:
    #stat_gen.qgini = q2
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
    V2_pu = model.addVar(lb=V2_min, ub=V2_max, name="V2")
    delta_Q = model.addVar(lb=-100, ub=100, name="delta_Q")

    # Constraints
    model.addConstr(V1_pu * Q1 + V1_pu * V2_pu * B - V1_pu**2 * B == Q2 * V2_pu, "Leistungsfluss_Q2")
    model.addConstr(V1_pu * P1 - V1_pu**2 * G + V1_pu * V2_pu * G == P2 * V2_pu, "Leistungsfluss_P1")
    model.addConstr(B*V2 * (V2 - V2_target) - delta_Q == 0, "Kompensationsblindleistung, um auf 1,05 zu regeln")
 
    # Zielsetzung
    model.setObjective(V2, GRB.MINIMIZE)
    

    Q_shunt_set = 20

    # Optimierung starten
    model.optimize()
    print(delta_Q.x)
    delta_Q = delta_Q.x
    V2_pu_squared = V2_pu.x**2
    Q_shunt = delta_Q/V2_pu_squared
    optimal_V2 = V2_pu.x
    optimal_Q2 = Q2.x
    
    k = Q_shunt/Q_shunt_set
    
    #Fallunterscheidung bei k +- 1 

    # Ergebnisse abrufen  
    if model.status == GRB.OPTIMAL:        
        results_df = results_df.append({
            'q2': q2,
            'Q1 vor Komp.': Q1,
            'Q_shunt': Q_shunt,
            'delta_Q': delta_Q,
            'k': k,
            'Q2': optimal_Q2,
            'V2_pu': optimal_V2
        }, ignore_index=True)
    else:
        print("Das Problem hat keine optimale Lösung gefunden.")
    
    
    #ldf_ac.run()
    # Ergebnisse mit PowerFactory vergleichen

    if q2 < 0:
        #capacitor.iopt_net = 1  # Kapazität einschalten 
        capacitor.outserv = 0
        capacitor.iTaps = 0
        if Q_shunt < 0:
            Q_shunt = -Q_shunt
        capacitor.qcapn = Q_shunt
        print(capacitor.qcapn)
    elif q2 > 0:
        reactor.outserv = 0
        #reactor.iopt_net = 1  # Induktivität einschalten
        reactor.iTaps = 0
        if Q_shunt < 0:
            Q_shunt = -Q_shunt
        reactor.qrean = Q_shunt
        print(reactor.qrean)
    
    
    ldf_ac.run()
    ldf_ac.iopt_asht = 1
    
    if q2 < 0:
        value_capacitor = capacitor.GetAttribute('m:Q:bus1')
        #value_reactor = 0
    elif q2 > 0:
        value_reactor = reactor.GetAttribute('m:Q:bus1') 
        #value_capacitor = 0

    if model.status == GRB.OPTIMAL:
        if q2 < 0:
            results_pf = results_pf.append({
                'q2': q2,
                'Q1 nach Komp.': bus1.GetAttribute('m:Qflow'),
                'Q_shunt': Q_shunt,
                'delta_Q': value_capacitor,
                'Kompensationstyp': 'Kapazitiv'
            }, ignore_index=True)
        elif q2 > 0:
            results_pf = results_pf.append({
                'q2': q2,
                'Q1 nach Komp.': bus1.GetAttribute('m:Qflow'),
                'Q_shunt': Q_shunt,
                'delta_Q': value_reactor,
                'Kompensationstyp': 'Induktiv'
            }, ignore_index=True)
    else:
        print("Das Problem hat keine optimale Lösung gefunden.")


        
    
print('Ergebnisse aus dem Modell:')  
print('-------------------------------------')  
print(results_df)
print('Ergebnisse aus PowerFactory:')
print('-------------------------------------')
print(results_pf)
# Modell aufräumen
model.dispose()

