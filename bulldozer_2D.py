import src.FemNodes
import src.FemElement
import src.FemSolver
import src.J_Meshing
import src.J_Modling
import src.FemSave
import numpy as np
import pygmsh
import numba
import time as ti
start_time = ti.time()


"""
第一步,先建模。
"""
def bulldozer2D(_mesh_size_, prt=0):
    #_mesh_size_ = 2e-2
    model_file = "bulldozer_2d" + str(_mesh_size_)
    with pygmsh.occ.Geometry() as geom:
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
        #disk4 = geom.add_disk([0, 0.585, 0.0], 0.05)
        flat = geom.boolean_difference(
            poly , 
            geom.boolean_union([disk3,  disk1, disk2]), #, disk4
        )
        """field0 = geom.add_boundary_layer(
            nodes_list=[poly.points[0]],
            lcmin=1e-4,
            lcmax=4e-3,
            distmin=1e-3,
            distmax=5e-3,
        )
        field1 = geom.add_boundary_layer(
            nodes_list=[poly.points[0]],
            lcmin=2e-3,
            lcmax=4e-3,
            distmin=5e-3,
            distmax=20e-3,
        )
        geom.set_background_mesh([field0, field1], operator="Min")"""
        mesh = geom.generate_mesh()
        points = mesh.points
        Mesh = mesh.get_cells_type("triangle")

        src.FemSave.FemSave(list(points), {"triangle":list(Mesh)}, model_file+".vtk")
        print("========Model Saved at:",model_file,"========\n")

    if 0:
        exit()


    """
    第二步,转换网格为可以用的形式。
    """
    points = mesh.points
    Mesh = mesh.get_cells_type("triangle")
    #print(points)
    #print(Mesh)
    #绘制以供检查
    #src.J_Meshing.print_mesh(points,Mesh)

    Nd = src.FemNodes.Fem_Nodes()
    points = [list(i) for i in points] #转化为3维的坐标
    Nd.Add_Fem_Nodes_Auto_Number(points) #将生成的节点做成有限元使用的类型

    #Nd.PrintFemNodes2d() # 可选，绘制设置好的节点供检查
    #end_time = ti.time()
    #print("Plot Time:", (end_time - start_time))

    # 生成单元
    Fem_Elms_class = src.FemElement.Element_Group(Nd)
    Material = {'E':2.1e11,'v':0.279,'t':4e-2}
    solve_type = '2d_stress'
    #print(Nd.Fem_Nodes_count)
    for i in Mesh:
        Fem_Elms_class.Add_Elm_Auto_Number('T3_2d', i, Material, pv=[solve_type])
    # 可选，绘制单元供检查
    #print(len(Fem_Elms))
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
    Sov = src.FemSolver.Solver_Static_2D(Nd,Fem_Elms)

    #载荷施加
    print('\n========================> Applying Loads <========================')

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
    #print(a)
    #print('\nDisplacement------------------')
    #print(a['Stress'])

    """
    第五步: 后处理
    """
    #查看2、3节点处的位移
    print('\n========================> Node Displacement <========================')
    scaler = 1000 #米化为毫米
    x0 = Nd.Find_Nodes_Cord_Range({'x':[0.7]})
    avg = 0
    for i in x0:
        print('Node%d:'%i,str(Sov.Post_Node_Displacement(a['Displacement'],i,scaler)))
        avg += Sov.Post_Node_Displacement(a['Displacement'],i,scaler)['x']
    # Sov.Draw_Mesh()
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
        
    avg = avg/len(x0)
    print("Average Displacement at x direction",avg)
    if prt == 1:
        Sov.Post_DeformedShape_UdeformedEdge(a['Displacement'],Scaler=100, value=x)
    return Nd.Fem_Nodes_count,avg
    

if __name__ == "__main__":
    bulldozer2D(2e-2, 1)