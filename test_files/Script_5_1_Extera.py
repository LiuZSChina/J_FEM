import src.FemNodes
import src.FemElement
import src.FemSolver
import numpy as np

"""
第一步,先定义结点及其编号。节点编号需从0开始,逐次递增,否则求解时无法通过节点编号检查。
"""
Nd = src.FemNodes.Fem_Nodes()

Size_nodes = 84
#按行生成等间距系列单元
Nd.Add_Fem_Nodes_With_Start_Number_Step([0,0,0],[0.1/(Size_nodes-1),0,0],Size_nodes ,0)
Nd.Add_Fem_Nodes_With_Start_Number_Step([0,1e-2,0],[0.1/(Size_nodes-1),0,0],Size_nodes ,Size_nodes )
Nd.Add_Fem_Nodes_With_Start_Number_Step([0,2e-2,0],[0.1/(Size_nodes-1),0,0],Size_nodes,2*Size_nodes)
# 可选，绘制设置好的节点供检查
#print('Done')
#Nd.PrintFemNodes2d()


"""
第二步: 通过定义的节点编号生成一系列单元
"""
Fem_Elms = []
Material = {'E':2.1e11,'t':1e-2,'v':0.28}

s_type = '2d_stress'
s_type = '2d_strain'
#生成第一行和第二行的单元
for i in range(int(Size_nodes -1)):
    Fem_Elms.append(src.FemElement.Triangle3Node_2d(i*2,[i,1+i,Size_nodes+i],Nd,Material,solve_type=s_type))
    Fem_Elms.append(src.FemElement.Triangle3Node_2d(1+i*2,[i+1,Size_nodes +1+i,Size_nodes +i],Nd,Material,solve_type=s_type))
for i in range(int(Size_nodes),int(2*Size_nodes-1)):
    Fem_Elms.append(src.FemElement.Triangle3Node_2d(i*2,[i,1+i,Size_nodes+i],Nd,Material,solve_type=s_type))
    Fem_Elms.append(src.FemElement.Triangle3Node_2d(1+i*2,[i+1,Size_nodes +1+i,Size_nodes +i],Nd,Material,solve_type=s_type))

# 可选，绘制单元供检查
print('---Element count = %s'%len(Fem_Elms))
#print('Element Defined')
#Fem_Elms[-2].Draw_Elm()
if 0:
    for i in Fem_Elms:
        i.Draw_Elm()


"""
第三步: 定义求解器 并且加载
"""
Sov = src.FemSolver.Solver_Static_2D(Nd,Fem_Elms)

#载荷施加
F = 100

Sov.Payload(Size_nodes-1,[0,-75])
Sov.Payload(2*Size_nodes-1,[0,-150])
Sov.Payload(3*Size_nodes-1,[0,-75])

"""
Sov.Payload(Size_nodes-1,[-1000,0])
Sov.Payload(3*Size_nodes-1,[1000,0])
"""

Sov.Displacement(0,[0,''])
Sov.Displacement(Size_nodes,[0,0])
Sov.Displacement(2*Size_nodes,[0,''])


#Sov.Draw_Mesh()

# 可选，查看整体刚度矩阵
if 0:
    print('\nE------------------')
    print(Sov.Calc_E.todense())
    #print('\ninvE------------------')
    #print(np.linalg.inv(Sov.Calc_E.todense))
    print('\nP------------------')
    print(Sov.Groupe_P)

"""
第四步: 求解
"""
print('\n========================> Solving Problem <========================')
a = Sov.solve()
#print('\nDisplacement------------------')
#print(a['Stress'])


"""
第五步: 后处理
"""
#查看2、3节点处的位移
print('\n========================> Node Displacement <========================')
scaler = 1000 #米化为毫米
print('Node%s:'%(Size_nodes-1),str(Sov.Post_Node_Displacement(a['Displacement'],Size_nodes-1,scaler)))
print('Node%s:'%(2*Size_nodes-1),str(Sov.Post_Node_Displacement(a['Displacement'],2*Size_nodes-1,scaler)))
print('Node%s:'%(3*Size_nodes-1),str(Sov.Post_Node_Displacement(a['Displacement'],3*Size_nodes-1,scaler)))

#Sov.Post_DeformedShape_UdeformedEdge(a['Displacement'],100)