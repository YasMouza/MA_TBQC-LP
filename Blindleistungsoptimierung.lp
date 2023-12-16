\ Model Blindleistungsoptimierung
\ LP format - for model browsing. Use MPS format to capture full model detail.
Minimize
  0 P2 + k
Subject To
 V2_max: V2 <= 1.1
 V2_min: V2 >= 1.05
 Kompensationsblindleistung,_um_auf_1,05_zu_regeln: - 20 k
   = -55.4650364144138
 Leistungsfluss_Q2: Q2 - 0.0823999977111816 V2 + delta_Q
   = 70.01466613106491
 Shunt_Blindleistung: delta_Q - 20 k = 0
 Spannung_V2: - 0.08 Q2 + V2 = -4.577963078718225
 Leistungsfluss_Q2: [ Q2 * V2 ] = 84.70252226457657
Bounds
 -100 <= Q2 <= 100
 -100 <= P2 <= 100
 1.05 <= V2 <= 1.1
 -100 <= delta_Q <= 100
 -250 <= k <= 250
Generals
 k
End
