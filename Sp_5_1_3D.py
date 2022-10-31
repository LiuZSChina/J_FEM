import random
import src.FemNodes
import src.FemElement
import src.FemSolver
import src.FemSave
import src.FemPostProc
import numpy as np
import pygmsh
import time as ti
start_time = ti.time()

model_file = "Script_5_1_3D.vtk"

"""
第一步,先建模。
"""
import pygmsh

with pygmsh.geo.Geometry() as geom:
    poly = geom.add_polygon(
        [
            [0.0, 0.0],
            [1.0e-1, 0],
            [1.0e-1, 1e-2],
            [0, 1e-2],
        ],
        mesh_size=2e-3,
    )
    geom.extrude(poly, [0.0, 0.0, 2e-2], num_layers=12)   # type: ignore
    mesh = geom.generate_mesh()
    #pygmsh.write("Script_5_1.msh")

    points = mesh.points
    Mesh = mesh.get_cells_type("tetra")
    p_data = []
    for i in range(len(points)):
        p_data.append(10*random.random())
    src.FemSave.FemSave(list(points), {"tetra":list(Mesh)}, model_file,point_data={'ss':p_data})
    print("========Model Saved at:",model_file,"========\n")

if 0:
    exit()

"""
第二步,转换网格为可以用的形式。
"""

Nd = src.FemNodes.Fem_Nodes()
points = [list(i) for i in points] #转化为3维的坐标
Nd.Add_Fem_Nodes_Auto_Number(points) #将生成的节点做成有限元使用的类型

#Nd.PrintFemNodes2d() # 可选，绘制设置好的节点供检查
#end_time = ti.time()
#print("Plot Time:", (end_time - start_time))

# 生成单元
Fem_Elms_class = src.FemElement.Element_Group(Nd)
Material = {'E':2.1e11,'t':1e-2,'v':0.3}
solve_type = '2d_stress'
#print(Nd.Fem_Nodes_count)
for i in Mesh:
    Fem_Elms_class.Add_Elm_Auto_Number('T4_3d', i, Material, pv=[solve_type])
# 可选，绘制单元供检查
#print(len(Fem_Elms))
#Fem_Elms_class.Elm_list[0].Draw_Elm()
if 0:
    for i in Fem_Elms_class.Elm_list:
        i.Draw_Elm()


refine_cnt = 0
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
Sov = src.FemSolver.Solver_Static_3D(Nd,Fem_Elms)

#载荷施加
x0 = Nd.Find_Nodes_Cord_Range({'x':[1e-1]})
#print(x0)
F = 300.0/float(len(x0))
#print(F)
for i in x0:
    Sov.Payload(i,[0,0,-F])



x0 = Nd.Find_Nodes_Cord_Range({'x':[0]})
#print(x0)
for i in x0:
    Sov.Displacement(i,[0,'',''])

x0 = Nd.Find_Nodes_Cord_Range({'x':[0], 'y':[0]})
#print(x0)
for i in x0:
    Sov.Displacement(i,[0,0,''])

x0 = Nd.Find_Nodes_Cord_Range({'x':[0], 'z':[0]})
#print(x0)
for i in x0:
    Sov.Displacement(i,[0,'',0])

cent = Nd.Find_Nodes_by_Coord([0,0,0])
Sov.Displacement(cent,[0,0,0])


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
#print(a)
#print('\nDisplacement------------------')
#print(a['Stress'])

"""
第五步: 后处理
"""
save_name = "sp_5_1_deform.vtk"
post = src.FemPostProc.Post_3D(Nd,Fem_Elms_class)
pdf,cdf = post.Get_Deformed_Nodes(a['Displacement'],Scaler=100)
dic_xyz = post.get_points_displacement(a['Displacement'],Scaler=100)

src.FemSave.FemSave(list(pdf), {"tetra":list(Mesh)}, save_name, cell_data=dic_xyz)

#查看2、3节点处的位移
print('\n========================> Node Displacement <========================')
scaler = 1000 #米化为毫米
x0 = Nd.Find_Nodes_Cord_Range({'x':[1e-1]})
avg = 0
for i in x0:
    print('Node%d:'%i,str(post.Post_Node_Displacement(a['Displacement'],i,scaler)))
    avg += post.Post_Node_Displacement(a['Displacement'],i,scaler)['z']
avg = avg/len(x0)
print("Average Displacement at z direction",avg)
#Sov.Draw_Mesh()
#input('Enter to exit')
x = {}
for key in a['Strain']:
    x[key] = abs(a['Strain'][key][0][0])

for key in a['Strain']:
    node = Fem_Elms_class.Elm_dict[key].Nd_number[0]
    #print(a['Displacement'][int(node)])
    x[key] = a['Displacement'][int(2*node)]
end_time = ti.time()
print("Run Time:", (end_time - start_time))
post.Post_DeformedShape_UdeformedEdge(a['Displacement'],Scaler=100) #, value=x
