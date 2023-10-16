\ Model Blindleistungsberechnung
\ LP format - for model browsing. Use MPS format to capture full model detail.
Minimize
  0 Q_Comp + 0 cos_theta_diff + Q2
Subject To
 R0: - theta1 + theta2 + theta_diff = 0
 slack_bus: V1 = 1
 slack_bus_angle: theta1 = 0
 Voltage_range_bus_2(1): V2 >= 1.05
 Voltage_range_bus_2(2): V2 <= 1.1
 qc0: V_product + [ - V1 * V2 ] = 0
 q_constraint: [ 0.08 sin_theta_diff * V_product ] <= 42.2
 q_constraint: Q2 + [ 0.08 sin_theta_diff * V_product ] <= 0
Bounds
 0.9 <= V1 <= 1.1
 0.9 <= V2 <= 1.1
 -3.141592653589793 <= theta1 <= 3.141592653589793
 -3.141592653589793 <= theta2 <= 3.141592653589793
 -1 <= cos_theta_diff <= 1
 -1 <= sin_theta_diff <= 1
 theta_diff free
 -100 <= Q2 <= 100
General Constraints
 GC0: theta_diff = COS ( cos_theta_diff )
 GC1: theta_diff = SIN ( sin_theta_diff )
End
