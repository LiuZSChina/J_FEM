import src.FemNodes
import src.FemElement
import src.FemSolver
import numpy as np
import math

"""
第一步,先定义结点及其编号。节点编号需从0开始,逐次递增,否则求解时无法通过节点编号检查。
"""

t = 4e-2
l = 6e-2
Nd = src.FemNodes.Fem_Nodes()
Nd.Add_Fem_Nodes_With_Number([ [0,0,0],[l,0,0],[0,4e-2,t],[0,4e-2,0] ],[ 0,1,2,3 ])
Nd.Add_Fem_Nodes_With_Number([[0,0,t],[l,0,t]],[ 4,5 ])
Nd.Add_Fem_Nodes_With_Number([[l,4e-2,0],[l,4e-2,t]],[ 6,7 ])
l = 2*l

#Nd.Add_Fem_Nodes_With_Number([ [0,0,0],[l,0,0],[0,4e-2,t],[0,4e-2,0] ],[ 8,9,10,11 ])
Nd.Add_Fem_Nodes_With_Number([[l,0,0],[l,0,t]],[ 8,9 ])
Nd.Add_Fem_Nodes_With_Number([[l,4e-2,0],[l,4e-2,t]],[ 10,11 ])
# 可选，绘制设置好的节点供检查
#Nd.PrintFemNodes2d()
Nd.PrintFemNodes3d([])
print(Nd.Fem_Nodes_Dic)
if 0:
    print("Only Nodes Drawing")
    exit()

"""
第二步: 通过定义的节点编号生成一系列单元
"""
Fem_Elms = []
Material = {'E':2.1e11,'t':1e-2,'v':0.3}
Fem_Elms.append(src.FemElement.Tera4Node_3d(1,[0,1,3,4],Nd,Material))
Fem_Elms.append(src.FemElement.Tera4Node_3d(2,[1,3,4,2],Nd,Material))
Fem_Elms.append(src.FemElement.Tera4Node_3d(3,[1,5,4,2],Nd,Material))

Fem_Elms.append(src.FemElement.Tera4Node_3d(4,[1,5,6,3],Nd,Material))
Fem_Elms.append(src.FemElement.Tera4Node_3d(5,[5,7,6,3],Nd,Material))
Fem_Elms.append(src.FemElement.Tera4Node_3d(6,[2,7,3,5],Nd,Material))


Fem_Elms.append(src.FemElement.Tera4Node_3d(7,[1,8,9,10],Nd,Material))
Fem_Elms.append(src.FemElement.Tera4Node_3d(8,[9,10,11,1],Nd,Material))
Fem_Elms.append(src.FemElement.Tera4Node_3d(9,[5,9,11,1],Nd,Material))

Fem_Elms.append(src.FemElement.Tera4Node_3d(10,[1,10,6,5],Nd,Material))
Fem_Elms.append(src.FemElement.Tera4Node_3d(11,[5,7,6,10],Nd,Material))
Fem_Elms.append(src.FemElement.Tera4Node_3d(12,[5,11,7,10],Nd,Material))
# 可选，绘制单元供检查
if 0:
    Fem_Elms[3].Draw_Elm()
    Fem_Elms[4].Draw_Elm()
    Fem_Elms[5].Draw_Elm()

if 0:
    print("Only Elm")
    exit()
"""
第三步: 定义求解器 并且加载
"""
Sov = src.FemSolver.Solver_Static_3D(Nd,Fem_Elms)

#载荷施加
F = (5e6*4e-2*1e-2)/2
F = 1000

"""Sov.Payload(8,[F,0,0])
Sov.Payload(9,[F,0,0])
Sov.Payload(10,[F,0,0])
Sov.Payload(11,[F,0,0])"""

Sov.Payload(8,[0,F,0])
Sov.Payload(9,[0,F,0])
Sov.Payload(10,[0,F,0])
Sov.Payload(11,[0,F,0])

"""Sov.Payload(8,[0,0,F])
Sov.Payload(9,[0,0,F])
Sov.Payload(10,[0,0,-F])
Sov.Payload(11,[0,0,-F])"""

Sov.Displacement(0,[0,0,0])
Sov.Displacement(3,[0,'',0])
Sov.Displacement(4,[0,0,''])
Sov.Displacement(2,[0,'',''])


# 可选，查看整体刚度矩阵
if 0:
    print('\nE------------------')
    print(Sov.Calc_E.todense())
    print('\nP------------------')
    print(Sov.Groupe_P)

if 1:
    Sov.Draw_Mesh([1,0])


"""
第四步: 求解
"""
print('\n========================> Solving Problem <========================')
a = Sov.solve()
if 0:
    print(a)


"""
第五步: 后处理
"""
#查看2、3节点处的位移
print('\n========================> Node Displacement <========================')
scaler = 1000 #米化为毫米
print('Node1:',str(Sov.Post_Node_Displacement(a['Displacement'],1,scaler)))
print('Node5:',str(Sov.Post_Node_Displacement(a['Displacement'],5,scaler)))
print('Node6:',str(Sov.Post_Node_Displacement(a['Displacement'],6,scaler)))
print('Node7:',str(Sov.Post_Node_Displacement(a['Displacement'],7,scaler)))
print('Node4:',str(Sov.Post_Node_Displacement(a['Displacement'],4,scaler)))
Sov.Post_DeformedShape_UdeformedEdge(a['Displacement'],1000)

if 0:
    input("Press Enter to Exit")