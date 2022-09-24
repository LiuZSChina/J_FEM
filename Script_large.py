import src.FemNodes
import src.FemElement
import src.FemSolver
import numpy as np

"""
第一步,先定义结点及其编号。节点编号需从0开始,逐次递增,否则求解时无法通过节点编号检查。
"""
Nd = src.FemNodes.Fem_Nodes()
Nd.Add_Fem_Nodes_With_Number([ [0,0,0],[6e-2,0,0],[6e-2,2e-2,0],[6e-2,4e-2,0] ],[ 0,1,2,3 ])
Nd.Add_Fem_Nodes_With_Number([ [0,4e-2,0],[0,2e-2,0],[3e-2,2e-2,0] ],[ 4,5,6 ])
# 可选，绘制设置好的节点供检查
Nd.PrintFemNodes2d()


"""
第二步: 通过定义的节点编号生成一系列单元
"""
Fem_Elms = []
Material = {'E':2e11,'t':1e-2,'v':0.3}
Fem_Elms.append(src.FemElement.Triangle3Node([0,6,5],Nd,Material))
Fem_Elms.append(src.FemElement.Triangle3Node([0,1,6],Nd,Material))
Fem_Elms.append(src.FemElement.Triangle3Node([1,2,6],Nd,Material))
Fem_Elms.append(src.FemElement.Triangle3Node([6,2,3],Nd,Material))
Fem_Elms.append(src.FemElement.Triangle3Node([6,3,4],Nd,Material))
Fem_Elms.append(src.FemElement.Triangle3Node([5,6,4],Nd,Material))
# 可选，绘制单元供检查
Fem_Elms[1].Draw_Elm()


"""
第三步: 定义求解器 并且加载
"""
Sov = src.FemSolver.Solver1(Nd,Fem_Elms)

#载荷施加
F = 5e6*4e-2*1e-2/3
Sov.Payload(1,[F,''])
Sov.Payload(2,[F,0])
Sov.Payload(3,[F,0])

Sov.Displacement(0,[0,''])
Sov.Displacement(4,[0,''])
Sov.Displacement(5,[0,0])

# 可选，查看整体刚度矩阵
if True:
    print('\n------------------E')
    print(Sov.Groupe_E)
    print('\n------------------invE')
    print(np.linalg.inv(Sov.Groupe_E))
    print('\n------------------P')
    print(Sov.Groupe_P)

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
print('Node1:',str(Sov.Post_Node_Displacement(a,1,scaler)))
print('Node2:',str(Sov.Post_Node_Displacement(a,2,scaler)))
print('Node3:',str(Sov.Post_Node_Displacement(a,3,scaler)))
print('Node6:',str(Sov.Post_Node_Displacement(a,6,scaler)))