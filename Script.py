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
#Fem_Elms.append(src.FemElement.Triangle3Node_2d(2,[0,2,3],Nd,Material,'2d_stress'))
# 可选，绘制单元供检查
if False:
    Fem_Elms[1].Draw_Elm()


"""
第三步: 定义求解器 并且加载
"""
Fem_Elms = Fem_Elms_class.Elm_list
Sov = src.FemSolver.Solver_Static_2D(Nd,Fem_Elms)

#载荷施加
F = (5e6*4e-2*1e-2)/2
Sov.Payload(1,[F,0])
Sov.Payload(2,[F,0])

Sov.Displacement(0,[0,0])
Sov.Displacement(3,[0,''])


# 可选，查看整体刚度矩阵
if 0:
    print('\nE------------------')
    print(Sov.Calc_E.todense())
    print('\nP------------------')
    print(Sov.Groupe_P)

if 0:
    Sov.Draw_Mesh()


"""
第四步: 求解
"""
print('\n========================> Solving Problem <========================')
a = Sov.solve()
print(a)


"""
第五步: 后处理
"""
#查看2、3节点处的位移
print('\n========================> Node Displacement <========================')
scaler = 1000 #米化为毫米
print('Node1:',str(Sov.Post_Node_Displacement(a['Displacement'],1,scaler)))
print('Node2:',str(Sov.Post_Node_Displacement(a['Displacement'],2,scaler)))
Sov.Post_DeformedShape_UdeformedEdge(a['Displacement'],1000)