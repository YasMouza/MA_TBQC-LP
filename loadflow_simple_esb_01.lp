\ Model Spannungsoptimierung
\ LP format - for model browsing. Use MPS format to capture full model detail.
Minimize
  delta_v
Subject To
 sin_approx_0_1: - theta[0] + theta[1] + sin_approx_0_1 = 0
 sin_approx_1_0: theta[0] - theta[1] + sin_approx_1_0 = 0
 Spannung_V1: V[0] <= 1.03
 Wirkleistung_P1: P[0] = 1
 Wirkleistung_P2: P[1] >= -1
 Blindleistung_Q2: Q[1] - 0.02 k = 0.2
 delta_v_1: - V[1] + delta_v >= -1.05
 delta_v_2: V[1] + delta_v >= 1.05
 k_int_1: - k + k_int <= 0
 k_int_2: k - k_int <= 1
 VV_def_0_1: VV_0_1 + [ - V[0] * V[1] ] = 0
 cos_approx_0_1: cos_approx_0_1 + [ 0.5 theta[0] ^2 - theta[0] * theta[1]
   + 0.5 theta[1] ^2 ] = 1
 Wirkleistung_0_1: P[0] + [ 0.08 VV_0_1 * sin_approx_0_1 ] >= 0
 Blindleistung_0_1: Q[0] + [ - 0.08 VV_0_1 * cos_approx_0_1 ] >= 0
 VV_def_1_0: VV_1_0 + [ - V[0] * V[1] ] = 0
 cos_approx_1_0: cos_approx_1_0 + [ 0.5 theta[0] ^2 - theta[0] * theta[1]
   + 0.5 theta[1] ^2 ] = 1
 Wirkleistung_1_0: P[1] + [ 0.08 VV_1_0 * sin_approx_1_0 ] >= 0
 Blindleistung_1_0: Q[1] + [ - 0.08 VV_1_0 * cos_approx_1_0 ] >= 0
Bounds
 0.9 <= V[0] <= 1.1
 0.9 <= V[1] <= 1.1
 -50 <= k <= 50
 -3.141592653589793 <= theta[0] <= 3.141592653589793
 -3.141592653589793 <= theta[1] <= 3.141592653589793
Generals
 k_int
End
