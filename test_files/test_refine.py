import src.FemNodes
import src.FemElement
import src.FemSolver
import numpy as np
import math
"""
第一步,先定义结点及其编号。节点编号需从0开始,逐次递增,否则求解时无法通过节点编号检查。
"""
Nd = src.FemNodes.Fem_Nodes()
a = Nd.Add_Fem_Nodes_Auto_Number([ [0,0,0],[6e-2,0,0],[6e-2,4e-2,0],[0,4e-2,0] ])
# 可选，绘制设置好的节点供检查
#Nd.PrintFemNodes2d()
#print(a)
Nd.PrintFemNodes3d([])

"""
第二步: 通过定义的节点编号生成一系列单元
"""
Fem_Elms_class = src.FemElement.Element_Group(Nd)
Material = {'E':2.1e11,'t':1e-2,'v':0.3}
Fem_Elms_class.Add_Elm_Auto_Number('T3_2d', [0,1,2], Material, pv=['2d_stress'])
Fem_Elms_class.Add_Elm_Auto_Number('T3_2d', [0,2,3], Material, pv=['2d_stress'])
Fem_Elms_class.Elm_dict[0].split_mesh_3(Fem_Elms_class)
Fem_Elms_class.Elm_dict[1].split_mesh_3(Fem_Elms_class)

total = 0
for j in Fem_Elms_class.Elm_dict:
    if j > total:
        total = j
for i in range(total+1):
    Fem_Elms_class.Elm_dict[i].split_mesh_3(Fem_Elms_class)

total = 0
for j in Fem_Elms_class.Elm_dict:
    if j > total:
        total = j
for i in range(total+1):
    Fem_Elms_class.Elm_dict[i].split_mesh_3(Fem_Elms_class)

total = 0
for j in Fem_Elms_class.Elm_dict:
    if j > total:
        total = j
for i in range(total+1):
    Fem_Elms_class.Elm_dict[i].split_mesh_3(Fem_Elms_class)

total = 0
for j in Fem_Elms_class.Elm_dict:
    if j > total:
        total = j
for i in range(total+1):
    Fem_Elms_class.Elm_dict[i].split_mesh_3(Fem_Elms_class)

#print(Fem_Elms_class.Elm_dict)
Nd.Find_Nodes_Cord_Range({'x':[0]})

"""
第三步: 定义求解器 并且加载
"""
Fem_Elms = Fem_Elms_class.Elm_list
Sov = src.FemSolver.Solver_Static_2D(Nd,Fem_Elms)

#载荷施加
x0 = Nd.Find_Nodes_Cord_Range({'x':[6e-2], 'y':[0,2e-2]})
print(x0)
F = (5e6*4e-2*1e-2)/(2*len(x0))
for i in x0:
    Sov.Payload(i,[F,0])

x0 = Nd.Find_Nodes_Cord_Range({'x':[6e-2], 'y':[2e-2,4e-2]})
print(x0)
for i in x0:
    Sov.Payload(i,[-F,0])

x0 = Nd.Find_Nodes_Cord_Range({'x':[0]})

for i in x0:
    Sov.Displacement(i,[0,''])
Sov.Displacement(0,[0,0])

# 可选，查看整体刚度矩阵
if 0:
    print('\nE------------------')
    print(Sov.Calc_E.todense())
    print('\nP------------------')
    print(Sov.Groupe_P)

if 1:
    Sov.Draw_Mesh()

"""
第四步: 求解
"""
print('\n========================> Solving Problem <========================')
a = Sov.solve()
#print(a)

#Nd.PrintFemNodes3d([])
"""
第五步: 后处理
"""
#查看2、3节点处的位移
print('\n========================> Node Displacement <========================')
scaler = 1000 #米化为毫米
x0 = Nd.Find_Nodes_Cord_Range({'x':[6e-2]})
for i in x0:
    print('Node%d:'%i,str(Sov.Post_Node_Displacement(a['Displacement'],i,scaler)))

Sov.Post_DeformedShape_UdeformedEdge(a['Displacement'],1000)