\ Model optimal_power_flow_phase1
\ LP format - for model browsing. Use MPS format to capture full model detail.
Minimize multi-objectives
  PrimaryObj: Priority=1 Weight=1 AbsTol=1e-06 RelTol=0
   0 cos_theta_diff + 0 sin_theta_diff + 0 V_product + 0 V_square
   + delta_plus + delta_minus
  SecondaryObj: Priority=1 Weight=-1 AbsTol=1e-06 RelTol=0
   Q_Comp
Subject To
 R0: - theta[0] + theta[1] + theta_diff = 0
 slack_bus: V[0] = 1
 slack_bus_angle: theta[0] = 0
 R3: V[1] - delta_plus <= 1
 R4: - V[1] - delta_minus <= -1
 qc0: V_product + [ - V[0] * V[1] ] = 0
 qc1: V_square + [ - V[1] ^2 ] = 0
 p1: [ - 0.08 cos_theta_diff * V_product ] <= 5
 q: Q_Comp + [ - 0.08 sin_theta_diff * V_product ] <= 10
 p2: [ - 0.08 cos_theta_diff * V_product ] <= 5
Bounds
 0.9 <= V[0] <= 1.1
 0.9 <= V[1] <= 1.1
 -3.141592653589793 <= theta[0] <= 3.141592653589793
 -3.141592653589793 <= theta[1] <= 3.141592653589793
 -1 <= cos_theta_diff <= 1
 -1 <= sin_theta_diff <= 1
 theta_diff free
General Constraints
 GC0: theta_diff = COS ( cos_theta_diff )
 GC1: theta_diff = SIN ( sin_theta_diff )
End
