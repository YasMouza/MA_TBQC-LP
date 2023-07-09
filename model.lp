\ Model optimal_power_flow
\ LP format - for model browsing. Use MPS format to capture full model detail.
Minimize
 
Subject To
 slack_bus: V[0] = 1
 slack_bus_angle: theta[0] = 0
 R2: - theta[0] + theta[1] + theta_diff = 0
 R3: - V[1] + delta_v_plus - delta_v_minus = -1
 R4: delta_v_plus >= 0
 R5: delta_v_minus >= 0
 qc0: V_product + [ - V[0] * V[1] ] = 0
 p1: [ - 0.078125 V_product * cos_theta_diff ] <= 0
 q1: q1 + [ - 0.078125 V_product * sin_theta_diff ] <= 0
 p2: p2 + [ - 0.078125 V_product * cos_theta_diff ] <= 0
 q2: q2 + [ - 0.078125 V_product * sin_theta_diff ] <= 0
Bounds
 0.9 <= V[0] <= 1.1
 0.9 <= V[1] <= 1.1
 -3.141592653589793 <= theta[0] <= 3.141592653589793
 -3.141592653589793 <= theta[1] <= 3.141592653589793
 q1 free
 p2 free
 q2 free
 -1 <= cos_theta_diff <= 1
 -1 <= sin_theta_diff <= 1
 theta_diff free
General Constraints
 GC0: theta_diff = COS ( cos_theta_diff )
 GC1: theta_diff = SIN ( sin_theta_diff )
End
