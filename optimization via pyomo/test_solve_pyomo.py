from pyomo.environ import *

model = ConcreteModel()

model.x1 = Var(bounds=(0, 12), within=NonNegativeReals)
model.x2 = Var(bounds=(0, 16), within=NonNegativeReals)

model.eq1 = Constraint(expr=model.x1 + model.x2 <= 12)
model.eq2 = Constraint(expr=2*model.x1 + model.x2 <= 16)

model.obj = Objective(expr=40*model.x1 + 30*model.x2, sense=maximize)

opt = SolverFactory('ipopt')
results = opt.solve(model)
print(results)

