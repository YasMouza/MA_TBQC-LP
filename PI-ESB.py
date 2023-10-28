import numpy as np
import math as m 
import gurobipy as gp
from gurobipy import GRB, Model, quicksum
from main_powerfactory import PowerFactory
from loadflow import LoadFlow
import pandas as pd

from gurobipy import Model, GRB
import numpy as np

# Netzwerkparameter
l = 70  # Leitungslänge in km
R_per_km = 0.018  # Ohm/km
X_per_km = 0.123  # Ohm/km
Cb_per_km = 280e-9  # F/km

# Berechnung der Leitungsparameter
R = R_per_km * l
X = X_per_km * l
Cb = Cb_per_km * l

# Frequenz
f = 50  # Frequenz in Hz

# Berechnung der Kreisfrequenz
omega = 2 * np.pi * f

# Berechnung der Suszeptanz der Kapazität
B_C_2 = omega * Cb / 2

# Berechnung der Gesamtsuszeptanz der Leitung
B_L = 1 / X
B_ges = 2 * B_C_2 + B_L

# Erstellen des Optimierungsmodells
m = Model("Lastfluss")

# Entscheidungsvariablen
V = m.addVar(vtype=GRB.CONTINUOUS, name="V")
theta = m.addVar(vtype=GRB.CONTINUOUS, name="theta")

# Parameter
P = 1.0  # Aktive Leistung in p.u.
Q = 0.5  # Reaktive Leistung in p.u.
G = 1 / R  # Leitfähigkeit in S
B = B_ges  # Suszeptanz in S

# Zielfunktion (hier als Beispiel die Minimierung der Spannung)
m.setObjective(V, GRB.MINIMIZE)

# Nebenbedingungen
m.addConstr(V**2 * G + V * V * (G * np.cos(theta) + B * np.sin(theta)) >= P, "P_ungleichung")
m.addConstr(-V**2 * B + V * V * (G * np.sin(theta) - B * np.cos(theta)) >= Q, "Q_ungleichung")

# Optimierung
m.optimize()

# Ergebnisse
if m.status == GRB.OPTIMAL:
    print(f"Optimale Spannung: {V.x}")
    print(f"Optimaler Phasenwinkel: {theta.x}")
else:
    print("Keine optimale Lösung gefunden")
