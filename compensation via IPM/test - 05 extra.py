import numpy as np

# Leitungsparameter
R_prime = 0.018  # Ohm/km
X_prime = 0.123  # Ohm/km
l = 70  # km

# Impedanz der Leitung
Z = R_prime * l + 1j * X_prime * l
print(f"Impedanz der Leitung: {Z} Ohm")

# Admittanz der Leitung
Y = 1 / Z
print(f"Admittanz der Leitung: {Y} S")

# Admittanzmatrix
Y_matrix = np.array([[Y, -Y], [-Y, Y]])
print("Admittanzmatrix:")
print(Y_matrix)
