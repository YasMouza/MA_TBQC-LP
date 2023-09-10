\ Model PowerSystemOptimization
\ LP format - for model browsing. Use MPS format to capture full model detail.
Minimize
  0 theta_diff
Subject To
 V1_fixed: V[0] = 1.05
 V_product_definition: V_product + [ - V[0] * V[1] ] = 0
 P_balance: [ - sin_theta_diff * V_product ] <= 100
 Q1_balance: [ - cos_theta_diff * V_product ] >= 80
 Q2_balance: Q_Comp + [ cos_theta_diff * V_product ] <= 90
Bounds
 1.05 <= V[0] <= 1.1
 1.05 <= V[1] <= 1.1
 theta_diff free
 -1 <= sin_theta_diff <= 1
 -1 <= cos_theta_diff <= 1
 Q_Comp free
General Constraints
 sin_constraint: theta_diff = SIN ( sin_theta_diff )
 cos_constraint: theta_diff = COS ( cos_theta_diff )
End
