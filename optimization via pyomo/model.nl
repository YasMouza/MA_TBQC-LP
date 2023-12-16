g3 1 1 0	# problem unknown
 11 12 1 0 5 	# vars, constraints, objectives, ranges, eqns
 3 0 0 0 0 0	# nonlinear constrs, objs; ccons: lin, nonlin, nd, nzlb
 0 0	# network constraints: nonlinear, linear
 3 0 0 	# nonlinear vars in constraints, objectives, both
 0 0 0 1	# linear network variables; functions; arith, flags
 0 1 0 0 0 	# discrete variables: binary, integer, nonlinear (b,c,o)
 25 1 	# nonzeros in Jacobian, obj. gradient
 16 8	# max name lengths: constraints, variables
 0 0 0 0 0	# common exprs: b,c,o,c1,o1
C0	#Q2
o2	#*
n-1
o2	#*
v0	#V[1]
o16	#-
o2	#*
n-0.078125
o46	#cos
o0	#+
v2	#theta[1]
o2	#*
n-1
v1	#theta[0]
C1	#Q1
o2	#*
n-0.08046875
o46	#cos
o0	#+
v2	#theta[1]
o2	#*
n-1
v1	#theta[0]
C2	#P2
o2	#*
n-1
o2	#*
v0	#V[1]
o2	#*
n-0.078125
o41	#sin
o0	#+
v2	#theta[1]
o2	#*
n-1
v1	#theta[0]
C3	#Spannung_V1
n0
C4	#Wirkleistung_P1
n0
C5	#Blindleistung_Q1
n0
C6	#Blindleistung_Q2
n0
C7	#Compensation
n0
C8	#tap_adjustment
n0
C9	#delta_v_1
n0
C10	#delta_v_2
n0
C11	#theta_0
n0
O0 0	#objective
n0
x0	# initial guess
r	#12 ranges (rhs's)
4 0.078125
4 0.078125
4 0.0
1 1.03
4 -1.0
1 0.3
1 1.0
1 0.8
1 0.0
1 1.05
1 -1.05
4 0.0
b	#11 bounds (on variables)
0 0.9 1.1
0 -3.141592653589793 3.141592653589793
0 -3.141592653589793 3.141592653589793
0 0.9 1.1
3
3
3
3
2 0
0 -500 500
0 1 10
k10	#intermediate Jacobian column lengths
4
8
11
12
13
14
16
19
21
23
J0 5
7 1
10 0.001
0 0
1 0
2 0
J1 3
6 1
1 0
2 0
J2 4
5 1
0 0
1 0
2 0
J3 1
3 1
J4 1
4 1
J5 1
6 1
J6 1
7 1
J7 2
7 1
9 1
J8 2
10 -0.1
9 1
J9 2
0 1
8 -1
J10 2
0 -1
8 -1
J11 1
1 1
G0 1
8 1
