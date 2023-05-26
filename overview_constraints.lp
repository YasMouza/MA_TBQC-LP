\ Model Cold-Start-AC-Load-Flow
\ LP format - for model browsing. Use MPS format to capture full model detail.
Maximize
  z1 + z2 + z3 + z4 + z5 + z6 + z7 + 0 v_magnitude[0] + 0 v_magnitude[1]
   + 0 v_magnitude_<l3>\yasin.IntUser\TBQC.IntPrj\Netzmodell.IntPrjfolder\Netzdaten.IntPrjfolder\2_Bus.ElmNet\Klemmleiste.ElmTerm</l3>
   + 0 v_magnitude_<l3>\yasin.IntUser\TBQC.IntPrj\Netzmodell.IntPrjfolder\Netzdaten.IntPrjfolder\2_Bus.ElmNet\Klemmleiste(1).ElmTerm</l3>
Subject To
 constraint1: - theta + z1 >= 0
 constraint2: - 0.9009688679024191 theta + z2 >= 0
 constraint3: - 0.6234898018587336 theta + z3 >= 0
 constraint4: - 0.2225209339563144 theta + z4 >= 0
 constraint5: 0.2225209339563143 theta + z5 >= 0
 constraint6: 0.6234898018587335 theta + z6 >= 0
 constraint7: 0.900968867902419 theta + z7 >= 0
 R7: <= 0.5
 R8: 125 z1 <= 126
 R9: 125 theta[0] - 125 theta[1] <= 0.5
 R10: 125 z1 <= 126
 R11: - 125 theta[0] + 125 theta[1] <= 0.5
 R12: 125 z2 <= 126
 R13: <= 0.5
 R14: 125 z2 <= 126
 R15: theta[0] - theta[1] <= 6.283185307179586
 R16: theta[0] - theta[1] >= -6.283185307179586
 R17: - theta[0] + theta[1] <= 6.283185307179586
 R18: - theta[0] + theta[1] >= -6.283185307179586
Bounds
 theta <= 3.141592653589793
 -1 <= z1 <= 1
 -1 <= z2 <= 1
 -1 <= z3 <= 1
 -1 <= z4 <= 1
 -1 <= z5 <= 1
 -1 <= z6 <= 1
 -1 <= z7 <= 1
 v_magnitude[0] <= 1.5
 v_magnitude[1] <= 1.5
 -3.141592653589793 <= theta[0] <= 3.141592653589793
 -3.141592653589793 <= theta[1] <= 3.141592653589793
 v_magnitude_<l3>\yasin.IntUser\TBQC.IntPrj\Netzmodell.IntPrjfolder\Netzdaten.IntPrjfolder\2_Bus.ElmNet\Klemmleiste.ElmTerm</l3> <= 1.5
 v_magnitude_<l3>\yasin.IntUser\TBQC.IntPrj\Netzmodell.IntPrjfolder\Netzdaten.IntPrjfolder\2_Bus.ElmNet\Klemmleiste(1).ElmTerm</l3> <= 1.5
End
