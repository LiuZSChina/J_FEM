import numpy as np
import matplotlib.patches as mpatch
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection, Line3D
from scipy.spatial import Delaunay

class Post_3D():
    def __init__(self, ND_class, ELM_class):
        self.Node, self.Node_cnt = ND_class.GetFemNodesAll()
        self.Element = ELM_class
        self.ElementGroup =  self.Element.Elm_list
        pass
    
    # 获得变形后的节点位置
    def Get_Deformed_Nodes(self, Solved_disp, Scaler=1):
        # 获得有节点的坐标
        Init_a = np.zeros((3*self.Node_cnt, 1))
        for key in self.Node:
            key_i = int(key)
            Init_a[3*key_i][0] = self.Node[key_i][0]
            Init_a[3*key_i + 1][0] = self.Node[key_i][1]
            Init_a[3*key_i + 2][0] = self.Node[key_i][2]

        #叠加上变形结果（包括放大系数）
        Deformed_a = np.zeros_like(Init_a)
        Deformed_a[:] = Init_a
        Deformed_a += Scaler*Solved_disp
        
        Deformed_Node_list = []
        for i in range(self.Node_cnt):
            Deformed_Node_list.append([Deformed_a[3*i] , Deformed_a[3*i + 1] , Deformed_a[3*i + 2]])
        #Meshes = Delaunay(Deformed_Node_list)
        #print(Meshes)
        return Deformed_Node_list, {}

    # 获得节点位移的points data
    def get_points_displacement(self, Solved_disp, Scaler=1) -> dict:
        """获得 x y z 方向上的节点位移"""
        Displacement = np.zeros((3*self.Node_cnt, 1))
        Displacement = Scaler*Solved_disp
        Deformed_Node_dict = {'x':[],'y':[],'z':[]}
        for i in range(self.Node_cnt):
            Deformed_Node_dict['x'].append(Displacement[3*i])
            Deformed_Node_dict['y'].append(Displacement[3*i + 1])
            Deformed_Node_dict['z'].append(Displacement[3*i + 2])
        return Deformed_Node_dict

    #后处理，获得节点位移
    def Post_Node_Displacement(self,Displacement,Node_number,scaler=1):
        Node_number = int(Node_number)
        x_disp = scaler*Displacement[Node_number*3][0]
        y_disp = scaler*Displacement[Node_number*3+1][0]
        z_disp = scaler*Displacement[Node_number*3+2][0]
        return {'x':x_disp,'y':y_disp, 'z':z_disp}

    #后处理 变形后形状与变形前框架
    def Post_DeformedShape_Undeformed_Edge(self,Solved_disp,Scaler=1, Force_display = False):
        #print(self.Node_cnt)
        if self.Node_cnt>1000:
            print('!====> Too many nodes, Stop Displaying <====!')
            print('!====> Set Force_display = True to display!')
            if Force_display == False:
                return
        if self.Node_cnt>200:
            print('!====> Too many nodes, display maybe very slow <====!')
        # 获得有节点的坐标
        Init_a = np.zeros((3*self.Node_cnt, 1))
        for key in self.Node:
            key_i = int(key)
            Init_a[3*key_i][0] = self.Node[key_i][0]
            Init_a[3*key_i + 1][0] = self.Node[key_i][1]
            Init_a[3*key_i + 2][0] = self.Node[key_i][2]

        #叠加上变形结果（包括放大系数）
        Deformed_a = np.zeros_like(Init_a)
        Deformed_a[:] = Init_a
        Deformed_a += Scaler*Solved_disp
        #print (Deformed_a)

        #定义图表
        fig = plt.figure()
        ax = fig.add_subplot(111, projection='3d')

        #绘制变形后结果
        # Set axis aspect to fit the elm.
        print_list = []
        for key in self.Node:
            print_list.append(self.Node[key])
        x_bound = [min([i[0] for i in print_list]),max([i[0] for i in print_list])]
        y_bound = [min([i[1] for i in print_list]),max([i[1] for i in print_list])]
        z_bound = [min([i[2] for i in print_list]),max([i[2] for i in print_list])]   
        max_size = max([x_bound[1]-x_bound[0], y_bound[1]-y_bound[0], y_bound[1]-y_bound[0]])
        ax.set_xlim([(sum(x_bound)/2) - max_size/2 , (sum(x_bound)/2) + max_size/2])  # type: ignore
        ax.set_ylim([(sum(y_bound)/2) - max_size/2 , (sum(y_bound)/2) + max_size/2])  # type: ignore
        ax.set_zlim([(sum(z_bound)/2) - max_size/2 , (sum(z_bound)/2) + max_size/2])  # type: ignore

        for t in self.ElementGroup:
            Elm_Nd_number = t.Nd_number
            #print(Elm_Nd_number)
            Elm_idj = []
            for j in Elm_Nd_number:
                j = int(j)
                Elm_idj.append([Deformed_a[3*j][0] , Deformed_a[3*j+1][0] , Deformed_a[3*j+2][0] ])
            # 画各个面和边线
            #print(Elm_idj)
            pol = []
            for i in range(2):
                ii = (Elm_idj[i][0], Elm_idj[i][1], Elm_idj[i][2])
                for j in range(i+1,3):
                    jj = (Elm_idj[j][0], Elm_idj[j][1], Elm_idj[j][2])
                    for k in range(j+1,4):
                        kk = (Elm_idj[k][0], Elm_idj[k][1], Elm_idj[k][2])
                        pol.append([ii, jj, kk])
            
            tera = Poly3DCollection(pol,edgecolors= 'w', facecolor= [0.3, 0.7, 1], linewidths=0.2, alpha=0.5)
            ax.add_collection3d(tera)  # type: ignore


        #绘制变形前的框架
        # Set axis aspect to fit the elm.
        for t in self.ElementGroup:
            Elm_idj = t.Nd_i_j_m
            #print(Elm_idj)
            # 画各个面和边线
            pol = []
            for i in range(2):
                ii = (Elm_idj[i][0], Elm_idj[i][1], Elm_idj[i][2])
                for j in range(i+1,3):
                    jj = (Elm_idj[j][0], Elm_idj[j][1], Elm_idj[j][2])
                    for k in range(j+1,4):
                        kk = (Elm_idj[k][0], Elm_idj[k][1], Elm_idj[k][2])
                        pol.append([ii, jj, kk])
                        #print([ii, jj, kk])
                        #ax.plot(ii, jj, kk,linestyle='-')
            tera = Poly3DCollection(pol,edgecolors= 'r', facecolor= [0.5, 1, 1], linewidths=1, alpha=0)
            ax.add_collection3d(tera)  # type: ignore

            #print every nodes number
            Elm_num = t.Nd_number
            for j in range(len(Elm_num)):
                ax.text(Elm_idj[j][0], Elm_idj[j][1], Elm_idj[j][2],c = 'm',ha='center',va='bottom',s = str(Elm_num[j]), fontsize=8)    # type: ignore
                ax.plot(Elm_idj[j][0], Elm_idj[j][1], Elm_idj[j][2],c='m', marker='.',ls="",ms=3)
            

        plt.show()
        return