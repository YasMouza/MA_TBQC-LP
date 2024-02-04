import cmath
import math
import pandas as pd
import numpy as np

# Netzwerkparameter
n = 5  # Anzahl der Busbars

### Bus 1
P1_pu = 0.05  # p.u.
Q1_pu = 0  # p.u.

### Bus 2
Q_shunt_fix = 0.35  # p.u
V2_target = 1.05  # p.u.

## Bus 2 ---> Bus 3
l = 70  # km
C_prime = 280e-9  # Farad/km
C = C_prime * l
X_prime = 0.123  # Ohm/km
X_cab = X_prime * l  # Ohm/km
omega = 2 * cmath.pi * 50  # Kreisfrequenz für 50 Hz
B = C * omega

B_sf = 0.0234

### Bus 3
Q_shunt_var = 0  # p.u
Q_set_shunt = 0.3  # p.u
# X_tr1 = 0.15 * (75 / 100)  # p.u
# X_tr2 = 0.6
X_tr1 = 0.0
X_tr2 = 0.0233
B_cable_cap = (omega*C)/2 * (110000**2)/100e6 ### Bezugsscheileistung prüfen
B_cable_ind = 1/X_cab
k = 0
B_sv = 0.1
B_t1 = 0
B_t2 = 1/X_tr2

### Bus 4
Xe = 24.2  # Ohm ---> Strong grid equivalent 


### Bus 5
V5 = 1.03  # p.u.
theta_slack = 0

# Initialisierung der Spannungen (1 p.u.) und Winkel (0 rad)
V = np.ones(n)
theta = np.zeros(n)


# #### System - KAM
# #B_11 = (Y_t1*(1+ model.t1*1.25))*(-1)
# B_11 = 0
# #B_12 = B_21 = (1+ model.t1*1.25)*Y_t1 
# B_12 = B_21 = 0
# #B_22 =  (B_sf + B_cable_cap + 1/X_cab + ((1+ model.t1*1.25)**2)*Y_t1)*(-1)
# B_22 = -(B_sf + B_cable_cap + 1/X_cab)
# B_23 = B_32 = 1/X_cab
# B_13 = B_31 = 0
# #B_33 = (B_cable_cap + 1/X_cab + (1 + model.t2*1.25)*Y_t2 + Y_t2 + B_sv)*(-1)
# B_33 = -(B_cable_cap + 1/X_cab+ Y_t2 + B_sv)
# B_14 = B_41 = 0
# B_24 = B_42 = 0
# #B_34 = B_43 = (((1+ model.t2*1.25)/1)*Y_t2)*(-1)
# B_34 = B_43 = 0
# B_44 = 1/Xe 
# B_15 = B_51 = 0
# B_25 = B_52 = 0
# B_35 = B_53 = 0
# B_45 = B_54 = -1/Xe
# B_55 = 1/Xe

# B-Matrix
B_ij = np.array([
    [0, 0 , 0, 0, 0],
    [0 , -(B_sf + B_cable_cap + B_cable_ind + B_t1), 1 / X_cab, 0, 0],
    [0, 1 / X_cab, -(B_cable_cap + B_cable_ind + B_t2 + B_sv + B_t2), B_t2, 0],
    [0, 0, B_t2, -1 / Xe, 1 / Xe],
    [0, 0, 0, 1 / Xe, -1 / Xe]
])

print(B_ij)


# Leistungswerte
# P_net = np.array([P1_pu, P1_pu, P1_pu, P1_pu, P1_pu])
# Q_net = np.array([0, 0.573, 0.644, 0.592, 0.529])
P_net = np.array([5, 5, 5, 5, 5])
Q_net = np.array([0, 0.0, 0.0, 0.0, 0.0])
V = np.array([1.279, 1.279, 1.277, 1.176, 1.050])

# Berechnete Leistungsflüsse
P_calc = np.zeros(n)
Q_calc = np.zeros(n)

# Lastflussberechnung
for i in range(n):
    P_calc[i] = P_net[i]
    Q_calc[i] = Q_net[i]
    for j in range(n):        
        P_calc[i] -= V[i] * V[j] * B_ij[i, j] * math.sin(theta[i] - theta[j])
        Q_calc[i] -= V[i] * V[j] * B_ij[i, j] * math.cos(theta[i] - theta[j])

# Umrechnung der Winkel von Radiant in Grad
theta_deg = theta * (180 / math.pi)

# Erstellen eines DataFrames zur Ausgabe der Ergebnisse
df = pd.DataFrame({
    'Busbar': [f'Busbar {i+1}' for i in range(n)],
    'P': P_calc,
    'Q': Q_calc,
    'V': V,
    'Theta': theta_deg
})

# Ausgabe des DataFrames
print(df)
