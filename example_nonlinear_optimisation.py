import gurobipy as gp
from gurobipy import GRB

# Create a new model
model = gp.Model("quadratic_minimization")

# Create variables
x1 = model.addVar(lb=0, name="x1")
x2 = model.addVar(lb=0, name="x2")

# Set objective
obj = x1**2 + x2**2
model.setObjective(obj, GRB.MINIMIZE)

# Add constraint: x1 + x2 = 1
model.addConstr(x1 + x2 == 1, "c0")

# Optimize model
model.optimize()

# Print the optimal solution
for v in model.getVars():
    print(f'{v.varName}, {v.x}')

print(f'Obj: {model.objVal}')


import matplotlib.pyplot as plt
import numpy as np

# Create a grid of points
x = np.linspace(0, 1, 400)
y = np.linspace(0, 1, 400)
x, y = np.meshgrid(x, y)

# Compute the value of the objective function on the grid
z = x**2 + y**2

# Create a contour plot of the objective function
plt.figure(figsize=(8, 6))
contour = plt.contour(x, y, z, levels=np.logspace(-2, 0, 5))
plt.clabel(contour, inline=1, fontsize=10)
plt.xlabel('x1')
plt.ylabel('x2')


# Add the constraint line
plt.plot(0.5, 0.5, 'go', label='Optimal solution (0.5, 0.5)')

plt.legend()
plt.grid(True)
plt.show()

