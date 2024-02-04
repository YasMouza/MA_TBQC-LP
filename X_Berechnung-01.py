import numpy as np

# Gegebene Werte
n=5
V = np.array([1.279, 1.279, 1.277, 1.176, 1.050])  # Spannung in p.u.
theta = np.array([1.1, -148.6, 1, 0.6, 0])  # Phasenwinkel in Grad
P = np.array([0.05, 0.05, 0.05, 0.05, 0.05])  # Wirkleistung in MW
Q = np.array([0.0, 0.573, 0.64, 0.592, 0.529])  # Blindleistung in MVar

# Umrechnung der Winkel von Grad in Radiant
theta_rad = np.deg2rad(theta)

# Berechnung der Reaktanzen X_ij
X = np.zeros((n, n))
for i in range(n):
    for j in range(n):
        X[j,i] = X[i, j] = V[i] * V[j] * np.sin(theta_rad[i] - theta_rad[j]) / P[i]
        # Alternativ, wenn Q und der Cosinus-Term verwendet werden:
        #X[j,i] = X[i, j] = V[i] * V[j] * (np.cos(theta_rad[i] - theta_rad[j]) - 1) / Q[i]


# Berechnung der B-Matrix
B = -1 / X
np.set_printoptions(precision=3, suppress=True)

# Ausgabe der B-Matrix
print("B-Matrix:")
print(B)