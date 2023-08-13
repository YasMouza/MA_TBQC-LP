\ Model optimal_power_flow
\ LP format - for model browsing. Use MPS format to capture full model detail.
Minimize
  0 deltaV_plus + 0 deltaV_minus + delta_plus + delta_minus
Subject To
 R0: - theta[0] + theta[1] + theta_diff = 0
 slack_bus: V[0] = 1
 slack_bus_angle: theta[0] = 0
 R3: V[1] - delta_plus <= 1
 R4: - V[1] - delta_minus <= -1
 qc0: V_product + [ - V[0] * V[1] ] = 0
 qc1: quad_intermediate + [ - 0.078125 sin_theta_diff * V_product ] = 0
 p1: [ - 0.078125 cos_theta_diff * V_product ] <= 0
 q1: [ - 0.078125 sin_theta_diff * V_product ] <= 100
 p2: [ - 0.078125 cos_theta_diff * V_product ] <= 5
 q2: - 0.06 k + [ - k * quad_intermediate ] <= 0
Bounds
 0.9 <= V[0] <= 1.1
 0.9 <= V[1] <= 1.1
 -3.141592653589793 <= theta[0] <= 3.141592653589793
 -3.141592653589793 <= theta[1] <= 3.141592653589793
 1 <= k <= 6
 -1 <= cos_theta_diff <= 1
 -1 <= sin_theta_diff <= 1
 theta_diff free
 quad_intermediate free
Generals
 k
General Constraints
 GC0: theta_diff = COS ( cos_theta_diff )
 GC1: theta_diff = SIN ( sin_theta_diff )
End
