import src.FemNodes
import src.FemElement
import src.FemSolver
import numpy as np

"""
第一步,先定义结点及其编号。节点编号需从0开始,逐次递增,否则求解时无法通过节点编号检查。
"""
Nd = src.FemNodes.Fem_Nodes()

#按行生成等间距系列单元
Nd.Add_Fem_Nodes_With_Start_Number_Step([0,0,0],[2e-2,0,0],6,0)
Nd.Add_Fem_Nodes_With_Start_Number_Step([0,1e-2,0],[2e-2,0,0],6,6)
Nd.Add_Fem_Nodes_With_Start_Number_Step([0,2e-2,0],[2e-2,0,0],6,12)
# 可选，绘制设置好的节点供检查
Nd.PrintFemNodes2d()


"""
第二步: 通过定义的节点编号生成一系列单元
"""
Fem_Elms = []
Material = {'E':2.1e11,'t':1e-2,'v':0.28}

solve_type = '2d_stress'
#生成第一行和第二行的单元
for i in range(5):
    Fem_Elms.append(src.FemElement.Triangle3Node_2d(i*2,[i,1+i,7+i],Nd,Material,solve_type))
    Fem_Elms.append(src.FemElement.Triangle3Node_2d(1+i*2,[i,7+i,6+i],Nd,Material,solve_type))
for i in range(6,11):
    Fem_Elms.append(src.FemElement.Triangle3Node_2d(i*2-2,[i,1+i,7+i],Nd,Material,solve_type))
    Fem_Elms.append(src.FemElement.Triangle3Node_2d(i*2-1,[i,7+i,6+i],Nd,Material,solve_type))
# 可选，绘制单元供检查
print(len(Fem_Elms))
if 0:
    for i in Fem_Elms:
        i.Draw_Elm()


"""
第三步: 定义求解器 并且加载
"""
Sov = src.FemSolver.Solver_Static_2D(Nd,Fem_Elms)

#载荷施加
F = 100
"""
Sov.Payload(5,[100,0])
Sov.Payload(11,[100,0])
Sov.Payload(17,[100,0])
"""

Sov.Payload(5,[0,-0])
Sov.Payload(11,[0,-300])
Sov.Payload(17,[0,-0])

Sov.Displacement(0,[0,''])
Sov.Displacement(6,[0,0])
Sov.Displacement(12,[0,''])


# 可选，查看整体刚度矩阵
if 0:
    print('\nE------------------')
    print(Sov.Calc_E)
    print('\ninvE------------------')
    print(np.linalg.inv(Sov.Calc_E))
    print('\nP------------------')
    print(Sov.Groupe_P)
    print(Sov.Groupe_P)
Sov.Draw_Mesh()


"""
第四步: 求解
"""
print('\n========================> Solving Problem <========================')
a = Sov.solve()
print('\nDisplacement------------------')
print(a['Stress'])


"""
第五步: 后处理
"""
#查看2、3节点处的位移
print('\n========================> Node Displacement <========================')
scaler = 1000 #米化为毫米
print('Node3:',str(Sov.Post_Node_Displacement(a['Displacement'],3,scaler)))
print('Node2:',str(Sov.Post_Node_Displacement(a['Displacement'],2,scaler)))
print('Node5:',str(Sov.Post_Node_Displacement(a['Displacement'],5,scaler)))
print('Node11:',str(Sov.Post_Node_Displacement(a['Displacement'],11,scaler)))
print('Node17:',str(Sov.Post_Node_Displacement(a['Displacement'],17,scaler)))
# Sov.Draw_Mesh()
#input('Enter to exit')
Sov.Post_DeformedShape_UdeformedEdge(a['Displacement'],100)