from tokenize import Double3
import src.FemNodes
import src.FemElement
import src.FemSolver
import src.J_Meshing
import src.J_Modling
import numpy as np


"""
第一步,先建模。
"""
Model = src.J_Modling.Model_2D()

sp_cnt = 2
Model.add_line_auto_number([[0,0,0], [1e-1,0,0]], split=3*sp_cnt) 
Model.add_line_auto_number([[1e-1,0,0], [1e-1,2e-2,0]], split=1*sp_cnt)
#Model.add_line_auto_number([[9e-2,1e-2,0], [1e-2,1e-2,0]], split=int(0.4*sp_cnt)) 
#Model.add_line_auto_number([[9.8e-2,0.5e-2,0], [0.6e-2,0.5e-2,0]], split=int(2*sp_cnt)) 
Model.add_line_auto_number([[9.25e-2,1e-2,0], [0.75e-2,1e-2,0]], split=int(2*sp_cnt)) 
#Model.add_line_auto_number([[9.6e-2,1.5e-2,0], [0.4e-2,1.5e-2,0]], split=int(2*sp_cnt)) 
Model.add_line_auto_number([[1e-1,2e-2,0], [0,2e-2,0]], split=3*sp_cnt) 
Model.add_line_auto_number([[0,2e-2,0], [0,0,0]], split=1*sp_cnt) 

if 1:
    Model.draw_model()

"""
第二步,自动网格划分获得一组节点以及三角形元素。
"""
points = np.array(Model.get_init_nd()) #获取种子节点
points, Mesh = src.J_Meshing.Mesher_Tri_2D(points, max_volume=4e-6, max_shape_rate=2, refine=False) #生成网格 2e-5

#绘制以供检查
src.J_Meshing.print_mesh(points,Mesh)

Nd = src.FemNodes.Fem_Nodes()
points = [list(i)+[0] for i in points] #转化为3维的坐标
Nd.Add_Fem_Nodes_Auto_Number(points) #将生成的节点做成有限元使用的类型

#Nd.PrintFemNodes2d() # 可选，绘制设置好的节点供检查

# 生成单元
Fem_Elms_class = src.FemElement.Element_Group(Nd)
Material = {'E':2.1e11,'t':1e-2,'v':0.3}
solve_type = '2d_stress'
print(Nd.Fem_Nodes_count)
for i in Mesh:
    Fem_Elms_class.Add_Elm_Auto_Number('T3_2d', i, Material, pv=[solve_type])
# 可选，绘制单元供检查
#print(len(Fem_Elms))
if 0:
    for i in Fem_Elms_class.Elm_list:
        i.Draw_Elm()


refine_cnt = 3
for t in range(refine_cnt):
    print('---Refining Meshes &%d ---'%t)
    total = 0
    for j in Fem_Elms_class.Elm_dict:
        if j > total:
            total = j
    for i in range(total+1):
        Fem_Elms_class.Elm_dict[i].split_mesh_3(Fem_Elms_class)



"""
第三步: 定义求解器 并且加载
"""
Fem_Elms = Fem_Elms_class.Elm_list
Sov = src.FemSolver.Solver_Static_2D(Nd,Fem_Elms)

#载荷施加
x0 = Nd.Find_Nodes_Cord_Range({'x':[1e-1]})
F = 300.0/float(len(x0))
#print(F)
for i in x0:
    Sov.Payload(i,[0,-F])

"""
Sov.Payload(5,[100,0])
Sov.Payload(11,[100,0])
Sov.Payload(17,[100,0])
"""

"""Sov.Payload(5,[0,-0])
Sov.Payload(11,[0,-300])
Sov.Payload(17,[0,-0])"""
x0 = Nd.Find_Nodes_Cord_Range({'x':[0]})
for i in x0:
    Sov.Displacement(i,[0,''])
Sov.Displacement(6,[0,0])


# 可选，查看整体刚度矩阵
if 0:
    print('\nE------------------')
    print(Sov.Calc_E)
    
    print('\nP------------------')
    print(Sov.Groupe_P)
    print(Sov.Groupe_P)

if 0:
    Sov.Draw_Mesh()


"""
第四步: 求解
"""
print('\n========================> Solving Problem <========================')
a = Sov.solve()
print('\nDisplacement------------------')
#print(a['Stress'])


"""
第五步: 后处理
"""
#查看2、3节点处的位移
print('\n========================> Node Displacement <========================')
scaler = 1000 #米化为毫米
x0 = Nd.Find_Nodes_Cord_Range({'x':[1e-1]})
for i in x0:
    print('Node%d:'%i,str(Sov.Post_Node_Displacement(a['Displacement'],i,scaler)))
# Sov.Draw_Mesh()
#input('Enter to exit')
Sov.Post_DeformedShape_UdeformedEdge(a['Displacement'],100)