import numpy as np
from scipy.optimize import minimize
import matplotlib.pyplot as plt

# Nutzenmatrix
U = np.array([[3, 2, 5], [4, 3, 6]])

# Verfügbarkeit der Ressourcen
A = np.array([100, 150])

# Maximale Aufnahme der Projekte
B = np.array([60, 70, 80])

# Zielfunktion
def objective(x):
    return -np.sum(U * x.reshape((2, 3)))

# Nebenbedingungen
def constraint1(x):
    return A - np.sum(x.reshape((2, 3)), axis=1)

def constraint2(x):
    return B - np.sum(x.reshape((2, 3)), axis=0)

def constraint3(x):
    return x

# Anfangswerte
x0 = np.zeros(6)

# Definition der Nebenbedingungen
con1 = {'type': 'ineq', 'fun': constraint1}
con2 = {'type': 'ineq', 'fun': constraint2}
con3 = {'type': 'ineq', 'fun': constraint3}
constraints = [con1, con2, con3]

# Optimierung
sol = minimize(objective, x0, method='SLSQP', constraints=constraints)

# Ausgabe der Lösung
x_opt = sol.x.reshape((2, 3))
print("Optimale Zuweisung der Ressourcen:")
print(x_opt)

# Grafische Darstellung
fig, ax = plt.subplots()
cax = ax.matshow(x_opt, cmap="viridis")
fig.colorbar(cax)
plt.title("Optimale Ressourcenzuweisung")
plt.xlabel("Projekte")
plt.ylabel("Ressourcen")
plt.xticks(range(3), ['P1', 'P2', 'P3'])
plt.yticks(range(2), ['R1', 'R2'])
plt.show()
