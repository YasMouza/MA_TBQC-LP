\ Model Blindleistungsoptimierung
\ LP format - for model browsing. Use MPS format to capture full model detail.
Minimize
  0 P2 + delta_V2 + 0 k
Subject To
 Kompensationsblindleistung,_um_auf_1,05_zu_regeln: - delta_Q
   = 65.7982661433313
 Leistungsfluss_Q2: [ Q2 * V2_pu ] = 66.86151195892411
Bounds
 -100 <= Q2 <= 100
 -100 <= P2 <= 100
 1.05 <= V2_pu <= 1.1
 -100 <= delta_Q <= 100
 -250 <= k <= 250
End
