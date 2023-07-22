\ Model ACLoadFlow
\ LP format - for model browsing. Use MPS format to capture full model detail.
Maximize
  0 V[0] + V[1] + 0 k + 0 cos_theta_0_0 + 0 sin_theta_0_0 + 0 V_product_0_0
   + 0 cos_theta_1_1 + 0 sin_theta_1_1 + 0 V_product_1_1
Subject To
 R0: theta_diff_0_0 = 0
 R1: - theta[0] + theta[1] + theta_diff_0_1 = 0
 R2: theta[0] - theta[1] + theta_diff_1_0 = 0
 R3: theta_diff_1_1 = 0
 P_balance_bus_0: [ ] = 0
 Q_balance_bus_0: [ ] = 0
 P_balance_bus_0: [ 0.078125 sin_theta_0_1 * V_product_0_1 ] = 0
 Q_balance_bus_0: [ 0.078125 cos_theta_0_1 * V_product_0_1 ] = 0
 P_balance_bus_1: [ 0.078125 sin_theta_1_0 * V_product_1_0 ] = -1
 Q_balance_bus_1: [ 0.078125 cos_theta_1_0 * V_product_1_0 ] = -0.5
 P_balance_bus_1: [ ] = -1
 Q_balance_bus_1: [ ] = -0.5
Bounds
 0.9 <= V[0] <= 1.1
 0.9 <= V[1] <= 1.1
 -3.141592653589793 <= theta[0] <= 3.141592653589793
 -3.141592653589793 <= theta[1] <= 3.141592653589793
 1 <= k <= 10
 -1 <= cos_theta_0_0 <= 1
 -1 <= sin_theta_0_0 <= 1
 theta_diff_0_0 free
 -1 <= cos_theta_0_1 <= 1
 -1 <= sin_theta_0_1 <= 1
 theta_diff_0_1 free
 -1 <= cos_theta_1_0 <= 1
 -1 <= sin_theta_1_0 <= 1
 theta_diff_1_0 free
 -1 <= cos_theta_1_1 <= 1
 -1 <= sin_theta_1_1 <= 1
 theta_diff_1_1 free
Generals
 k
General Constraints
 GC0: theta_diff_0_0 = SIN ( sin_theta_0_0 )
 GC1: theta_diff_0_0 = COS ( cos_theta_0_0 )
 GC2: theta_diff_0_1 = SIN ( sin_theta_0_1 )
 GC3: theta_diff_0_1 = COS ( cos_theta_0_1 )
 GC4: theta_diff_1_0 = SIN ( sin_theta_1_0 )
 GC5: theta_diff_1_0 = COS ( cos_theta_1_0 )
 GC6: theta_diff_1_1 = SIN ( sin_theta_1_1 )
 GC7: theta_diff_1_1 = COS ( cos_theta_1_1 )
End
