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

model_file = "bulldozer_3d"


"""
第一步,先建模。
"""
_mesh_size_ = 3e-2

    #pygmsh.write("Script_5_1.msh")
with pygmsh.occ.Geometry() as geom:
    #geom.import_shapes(model_file)
    geom.characteristic_length_min = _mesh_size_
    geom.characteristic_length_max = _mesh_size_
    poly = geom.add_polygon([
            [0.0, 0.0],
            [0.435, 0],
            [0.435, 1.065],
            [0.7, 1.565],
            [0, 1.165],
        ])
    disk1 = geom.add_disk([0.435/2.0, 0.435, 0.0], 0.05)
    disk2 = geom.add_disk([0.435/2.0, 0.105, 0.0], 0.05)
    disk3 = geom.add_disk([0.435/2.0, 0.765, 0.0], 0.05)

    flat = geom.boolean_difference(
        poly , 
        geom.boolean_union([disk3,  disk1, disk2]),
    )

    geom.extrude(flat, [0, 0, 4e-2])  # type: ignore

    mesh = geom.generate_mesh()


    points = mesh.points
    Mesh = mesh.get_cells_type("tetra")

    src.FemSave.FemSave(list(points), {"tetra":list(Mesh)}, model_file+".vtk")
    print("========Model Saved at:",model_file,"========\n")

if 0:
    exit()


"""
第二步,转换网格为可以用的形式。
"""
print("======== Transforming Meshes ========")
Nd = src.FemNodes.Fem_Nodes()
points = [list(i) for i in points] #转化为3维的坐标
Nd.Add_Fem_Nodes_Auto_Number(points) #将生成的节点做成有限元使用的类型
print("Node Number = ", Nd.Fem_Nodes_count)
#Nd.PrintFemNodes2d() # 可选，绘制设置好的节点供检查
#end_time = ti.time()
#print("Plot Time:", (end_time - start_time))

# 生成单元
Fem_Elms_class = src.FemElement.Element_Group(Nd)
Material = {'E':2.1e11,'v':0.279}
#print(Nd.Fem_Nodes_count)
for i in Mesh:
    Fem_Elms_class.Add_Elm_Auto_Number('T4_3d', i, Material)
# 可选，绘制单元供检查
#print(len(Fem_Elms))
print("Element Number = ", len(Fem_Elms_class.Elm_list))
print("======== Done ========\n")
if 0:
    for i in Fem_Elms_class.Elm_list:
        i.Draw_Elm()


"""
第三步: 定义求解器 并且加载
"""
print('\n========================> Applying Loads <========================')
Fem_Elms = Fem_Elms_class.Elm_list
Sov = src.FemSolver.Solver_Static_3D(Nd,Fem_Elms)

#载荷施加
x0 = Nd.Find_Nodes_Surface([500, -265, 0, 64.725], cord_range={'x':[0.435,0.71],'y':[1.065,1.6]})
print('.',end='')
#print(x0)
Fx = -416300/ float(len(x0))
Fy = 204300/ float(len(x0))
#print(F)
for i in x0:
    Sov.Payload(i,[Fx,Fy,0])
print('.',end='')


# 固定边界
x0 = Nd.Find_Nodes_Cord_Range({'x':[0], 'y':[0,0.585]})
#x0 = Nd.Find_Nodes_Cord_Range({'x':[0], 'y':[0,1.165]})
#print(x0)
for i in x0:
    Sov.Displacement(i,[0,'',''])
print('.',end='')
x0 = Nd.Find_Nodes_Cord_Range({'x':[0.435], 'y':[0,0.285]})
#x0 = Nd.Find_Nodes_Cord_Range({'x':[0.435], 'y':[0,1.065]})
#print(x0)
for i in x0:
    Sov.Displacement(i,[0,'',''])
print('.',end='')
x0 = Nd.Find_Nodes_Cylinder_Z([0.435/2,0.105], 0.05,dif=1e-4)
#print(x0)
for i in x0:
    Sov.Displacement(i,[0,0,''])
print('.',end='')
#x0 = Nd.Find_Nodes_Cord_Range({'y':[0,0.435],'z':[0]})
sd_time = ti.time()
x0 = Nd.Find_Nodes_Cord_Range({'x':[0],'z':[0]})
#print(x0)
for i in x0:
    Sov.Displacement(i,['','',0])
print('.',end='')
#cent = Nd.Find_Nodes_by_Coord([0,0,0])
#Sov.Displacement(cent,[0,0,0])
ed_time = ti.time()
print('\n========================> Done <========================')

"""
第四步: 求解
"""
print('\n========================> Solving Problem <========================')

a = Sov.solve()
#print(Nd.Fem_Node_Elm)
#print(Nd.Fem_Nodes_count)
#print(a)
#print('\nDisplacement------------------')
#print(a['Stress'])

"""
第五步: 后处理
"""
save_name = model_file + "_deform.vtk"
post = src.FemPostProc.Post_3D(Nd,Fem_Elms_class)
pdf,cdf = post.Get_Deformed_Nodes(a['Displacement'],Scaler=100)
dic_xyz = post.get_points_displacement(a['Displacement'],Scaler=100)
stress = post.get_cell_stress(a['Stress'])
stress_nd = post.get_stress_nd(a['Stress'])
dic_xyz.update(stress_nd)
load_nd = Sov.get_loads()
dic_xyz.update(load_nd)
c_data = stress
src.FemSave.FemSave(list(pdf), {"tetra":list(Mesh)}, save_name, point_data=dic_xyz, cell_data=c_data)

#查看给定位置处的位移
print('\n========================> Node Displacement <========================')
scaler = 1000 #米化为毫米
x0 = Nd.Find_Nodes_Cord_Range({'x':[0.7], 'y':[1.565]})
avg = 0
for i in x0:
    print('Node%d:'%i,str(post.Post_Node_Displacement(a['Displacement'],i,scaler)))
    avg += post.Post_Node_Displacement(a['Displacement'],i,scaler)['x']
avg = avg/len(x0)
print("Average Displacement at x direction",avg)
#Sov.Draw_Mesh()
#input('Enter to exit')
end_time = ti.time()
print("Run Time:", (end_time - start_time))
post.Post_DeformedShape_Undeformed_Edge(a['Displacement'],Scaler=100) #, value=x