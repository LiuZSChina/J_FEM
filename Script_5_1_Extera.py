
import src.FemNodes
import src.FemElement
import src.FemSolver
import numpy as np

"""
第一步,先定义结点及其编号。节点编号需从0开始,逐次递增,否则求解时无法通过节点编号检查。
"""
Nd = src.FemNodes.Fem_Nodes()

Size_nodes = 70e3

#按行生成等间距系列单元
Nd.Add_Fem_Nodes_With_Start_Number_Step([0,0,0],[2e-5,0,0],Size_nodes ,0)
Nd.Add_Fem_Nodes_With_Start_Number_Step([0,1e-5,0],[2e-5,0,0],Size_nodes ,Size_nodes )
# 可选，绘制设置好的节点供检查
print('Done')
#Nd.PrintFemNodes2d()


"""
第二步: 通过定义的节点编号生成一系列单元
"""
Fem_Elms = []
Material = {'E':2.1e11,'t':1e-2,'v':0.3}

#生成第一行和第二行的单元
for i in range(int(Size_nodes -1)):
    Fem_Elms.append(src.FemElement.Triangle3Node(i*2,[i,1+i,Size_nodes +1+i],Nd,Material))
    Fem_Elms.append(src.FemElement.Triangle3Node(1+i*2,[i,Size_nodes +1+i,Size_nodes +i],Nd,Material))

# 可选，绘制单元供检查
print(len(Fem_Elms))
Fem_Elms[-2].Draw_Elm()
if 0:
    for i in Fem_Elms:
        i.Draw_Elm()


"""
第三步: 定义求解器 并且加载
"""
Sov = src.FemSolver.Solver_Static(Nd,Fem_Elms)

#载荷施加
F = 100
Sov.Payload(5,[0,-37.5])
Sov.Payload(1100,[0,-225])
Sov.Payload(1700,[0,-37.5])

"""Sov.Payload(5,[100,0])
Sov.Payload(11,[0,0])
Sov.Payload(17,[-100,0])
"""
Sov.Displacement(0,[0,0])
Sov.Displacement(6,[0,0])
Sov.Displacement(12,[0,0])


# 可选，查看整体刚度矩阵
if 0:
    print('\nE------------------')
    print(Sov.Calc_E)
    print('\ninvE------------------')
    print(np.linalg.inv(Sov.Calc_E))
    print('\nP------------------')
    print(Sov.Groupe_P)
    print(Sov.Groupe_P)
#Sov.Draw_Mesh()


"""
第四步: 求解
"""
print('\n========================> Solving Problem <========================')
a = Sov.solve()
print('\nDisplacement------------------')
print(a['Displacement'])


"""
第五步: 后处理
"""
#查看2、3节点处的位移
print('\n========================> Node Displacement <========================')
scaler = 1000 #米化为毫米
print('Node3:',str(Sov.Post_Node_Displacement(a['Displacement'],3,scaler)))
print('Node2:',str(Sov.Post_Node_Displacement(a['Displacement'],2,scaler)))
print('Node5:',str(Sov.Post_Node_Displacement(a['Displacement'],5,scaler)))
print('Node1100:',str(Sov.Post_Node_Displacement(a['Displacement'],1100,scaler)))
print('Node1700:',str(Sov.Post_Node_Displacement(a['Displacement'],1700,scaler)))
# Sov.Draw_Mesh()
#input('Enter to exit')
#Sov.Post_DeformedShape_UdeformedEdge(a['Displacement'],100)