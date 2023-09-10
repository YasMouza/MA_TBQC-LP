\ Model Power_Flow_With_Compensation
\ LP format - for model browsing. Use MPS format to capture full model detail.
Minimize
 
Subject To
 theta_difference: - theta[0] + theta[1] + theta_diff = 0
 V_product_definition: V_product + [ - V[0] * V[1] ] = 0
 P1_balance: [ 0.08 sin_theta_diff * V_product ] <= 100
 P2_balance: [ - 0.08 sin_theta_diff * V_product ] >= -100
 Q1_balance: [ 0.08 cos_theta_diff * V_product ] <= 100
 Q2_balance: Q_Comp + [ 0.08 cos_theta_diff * V_product ] >= 100
Bounds
 1.05 <= V[0] <= 1.1
 1.05 <= V[1] <= 1.1
 -3.141592653589793 <= theta[0] <= 3.141592653589793
 -3.141592653589793 <= theta[1] <= 3.141592653589793
 -6.283185307179586 <= theta_diff <= 6.283185307179586
 Q_Comp free
 -1 <= sin_theta_diff <= 1
 -1 <= cos_theta_diff <= 1
 1.1025 <= V_product <= 1.21
General Constraints
 sin_constraint: theta_diff = SIN ( sin_theta_diff )
 cos_constraint: theta_diff = COS ( cos_theta_diff )
End
