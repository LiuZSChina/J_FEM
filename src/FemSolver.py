import math
from random import random
import numpy as np
import matplotlib.patches as mpatch
import matplotlib.pyplot as plt
from scipy.sparse import csr_matrix,lil_matrix
from scipy.sparse import linalg as sci_linalg
from mpl_toolkits.mplot3d.art3d import Poly3DCollection, Line3D
from src.doolittle import Doolittle_solver


try:
    import FemNodes
    import FemElement
except ModuleNotFoundError:
    import src.FemNodes
    import src.FemElement


def get_color_with_max_value(value, max_I):
    rgb_r = max(0,(value-(max_I/2))/(max_I/2))
    rgb_b = max(0,((max_I-value)-max_I/2)/(max_I/2) )
    rgb_g = (value/max_I)*(1-value/max_I)
    cl = [rgb_r, rgb_g, rgb_b]
    max_hue = max(cl)
    multi = 1/max_hue
    for value in range(len(cl)):
        cl[value] *= multi
    return cl


class Solver_Static_2D():
    def __init__(self, Nd, EleList) -> None:

        self.Node, self.Node_cnt = Nd.GetFemNodesAll()
        self.ElementGroup = EleList
        self.Total_Dof = 0
        #判断节点可用
        print('======>     Node&Element Number Checking     <======')
        nNc,word = self.Node_Elment_Number_Check()
        if not nNc:
            print(word)
            exit()
        print(word)
        self.color_map = self.Get_colors()
        #print(self.color_map)
        # 载荷矩阵
        self.Groupe_P = np.zeros((2*self.Node_cnt,1))
        print('---Got Mat P')

        # 总体刚度矩阵
        self.Calc_E = self.Calc_Grouped_E()
        print('---Got Mat E')


    #求解
    def solve(self):
        #打印总共自由度数量
        print('\nTotal Dofs ================== %s\n'%self.Total_Dof)
        #计算整体的节点位移
        if self.Total_Dof <5000:
            print('Solving Method ........... Doolittle')
            print('Solving Displacement.........\t',end='')
            Solv_E = np.array(self.Calc_E.todense())
            Node_displacement = Doolittle_solver(Solv_E,self.Groupe_P)
        else:
            print('Solving Method ............... Scipy')
            print('Matrix(E) size=', self.Calc_E.get_shape(),'; Nonzero = ',self.Calc_E.count_nonzero(), '(', round(100*self.Calc_E.count_nonzero()/(self.Calc_E.get_shape()[0]**2),2),'%)')
            print('Solving Displacement.........\t',end='')
            
            Solv_E = self.Calc_E.tocsr()
            Node_displacement = np.array([sci_linalg.spsolve(Solv_E,self.Groupe_P)]).T
        print('Done')

        #计算计算各个单元内应变
        print('Calculating Stress&Strain......\t',end='')
        eps = {}
        sigma = {}
        for i in self.ElementGroup:
            ae = np.zeros((6,1))
            nd = 0
            for j in i.Nd_number:
                j = int(j)
                ae[2*nd] = Node_displacement[2*j]
                ae[2*nd+1] = Node_displacement[2*j+1]
                nd += 1
            #ae = np.dot(i.Generate_Elm_G(self.Node_cnt),Node_displacement)
            eps_e = np.dot(i.Generate_Elm_B(),ae)
            D = np.array([
                [1, i.MaterialProp['v'], 0],
                [i.MaterialProp['v'], 1, 0],
                [0, 0, (1-i.MaterialProp['v'])/2]])
            D = (i.MaterialProp['E']/(1-math.pow(i.MaterialProp['v'],2)))*D
            sig_e = np.dot(D,eps_e)
            eps[i.number] = eps_e
            sigma[i.number] = sig_e
            #print(ae)

        print('Done\n')
        #计算各个单元应力

        return {'Displacement':Node_displacement,'Strain':eps,'Stress':sigma}

    # 显示所有的网格
    def Draw_Mesh(self,Size = [10,10]):
        fig,ax =plt.subplots()
        for i in self.ElementGroup:
            pot = [j[0:2] for j in i.Nd_i_j_m]
            tri = mpatch.Polygon(pot)
            #ax.set_xlim(-1,5)
            #ax.set_ylim(-1,5)
            ax.add_patch(tri)
            x = []
            y = []
            if True:
                for j in range(len(i.Nd_i_j_m)):
                    Pos = i.Nd_i_j_m[j]
                    Numb = i.Nd_number[j]
                    plt.plot(Pos[0], Pos[1],c='red', marker='.',ls="",ms=Size[0])
                    plt.text(Pos[0],Pos[1],Numb,ha='center',va='bottom' ,c = 'k',fontsize=Size[1])
                    x.append(Pos[0])
                    y.append(Pos[1])
                    
            ax.plot(x,y,c='m')
        plt.title('Fem Meshes to Solve\nx-y axis not equal!')
        plt.axis('equal')
        plt.show()

    #获得绘图所需要的颜色
    def Get_colors(self, dim = 16):
        c = []
        for i in range(dim):
            c.append(get_color_with_max_value(i,dim))
        return c

    #后处理，获得节点位移
    def Post_Node_Displacement(self,Displacement,Node_number:int,scaler=1):
        Node_number = int(Node_number)
        x_disp = scaler*Displacement[Node_number*2][0]
        y_disp = scaler*Displacement[Node_number*2+1][0]
        return {'x':x_disp,'y':y_disp}

    #后处理 变形后形状与变形前框架
    def Post_DeformedShape_UdeformedEdge(self,Solved_disp, Scaler=1, value ={}, Force_display=False):
        if self.Node_cnt>10000:
            print('!====> Too many nodes, Stop Displaying <====!')
            print('!====> Set Force_display = True to display!')
            if Force_display == False:
                return
        if self.Node_cnt>5000:
            print('!====> Too many nodes, display maybe very slow <====!')
        # 获得有节点的坐标
        Init_a = np.zeros((2*self.Node_cnt, 1))
        for key in self.Node:
            key_i = int(key)
            Init_a[2*key_i][0] = self.Node[key_i][0]
            Init_a[2*key_i +1][0] = self.Node[key_i][1]

        #叠加上变形结果（包括放大系数）
        Deformed_a = np.zeros_like(Init_a)
        Deformed_a[:] = Init_a
        Deformed_a += Scaler*Solved_disp
        #print (Deformed_a)

        #定义图表
        fig,ax =plt.subplots()

        #绘制变形后结果
        max_value = 1
        min_value = 0
        if value != {}:
            value_l = []
            for key in value:
                value_l.append(value[key])
            max_value = max(value_l)
            min_value = min(value_l)
        for i in self.ElementGroup:
            points = []
            nd_num = i.Nd_number
            for nd_f in nd_num:
                nd = int(nd_f)
                x = Deformed_a[2*nd][0]
                y = Deformed_a[2*nd+1][0]
                points.append([x,y])

            portion = 8
            if value != {}:
                elm_num = i.number
                portion = int((value[elm_num] - min_value)*15/(max_value- min_value))
            cl = self.color_map[portion]
            Deformed_Shape = mpatch.Polygon(points, color = cl)
            ax.add_patch(Deformed_Shape)      
        de_nd = []
        for i_f in range(self.Node_cnt):
            i = int(i_f)
            x = Deformed_a[2*i]
            y = Deformed_a[2*i + 1]
            de_nd.append([x,y])

        """for i in de_nd:
            #plt.scatter(i[0],i[1], c='m', s=10, label='Nodes')
            plt.plot(i[0], i[1],c='m', marker='.',ls="",ms=10)"""

        #绘制变形前的框架
        for i in self.ElementGroup:
            x = []
            y = []
            for j in range(3):
                Pos = i.Nd_i_j_m[j]
                x.append(Pos[0])
                y.append(Pos[1])                   
            ax.plot(x,y,c='y',linestyle = 'dashed', lw = 0.4)
        plt.title('Deformed Shape with Undeformed Edge \nDisplacement scal=%s'%Scaler)
        plt.axis('equal')
        plt.show()
        return

    # 定义载荷边界条件
    def Payload(self,Node_Number,value):
        if value[0] != '':
            self.Groupe_P[2*int(Node_Number)][0] = value[0]
        if value[1] != '':
            self.Groupe_P[2*int(Node_Number) +1][0] = value[1]
        return

    # 定义位移边界条件
    def Displacement(self,Node_Number,value):
        Node_Number = int(Node_Number)
        if value[0] == 0:
            self.Total_Dof -= 1
            self.Groupe_P[2*Node_Number] = 0
            
            # 改1法
            for col in range(2*self.Node_cnt):
                if col != 2*Node_Number:
                    self.Calc_E[2*Node_Number,col] = 0
                else:
                    self.Calc_E[2*Node_Number,col] = 1
            for row in range(2*self.Node_cnt):
                if row != 2*Node_Number:
                    self.Calc_E[row,2*Node_Number] = 0
                else:
                    self.Calc_E[row,2*Node_Number] = 1

        elif value[0] != '':
            self.Total_Dof -= 1
            self.Calc_E[2*Node_Number,2*Node_Number] = 10e20*self.Calc_E[2*Node_Number,2*Node_Number]  # type: ignore
            self.Groupe_P[2*Node_Number] = value[0]

        if value[1] == 0:
            self.Total_Dof -= 1
            self.Groupe_P[2*Node_Number+1] = 0
            
            # 改1法
            for col in range(2*self.Node_cnt):
                if col != 2*Node_Number+1:
                    self.Calc_E[2*Node_Number+1, col] = 0
                else:
                    self.Calc_E[2*Node_Number+1, col] = 1
            for row in range(2*self.Node_cnt):
                if row != 2*Node_Number+1:
                    self.Calc_E[row, 2*Node_Number+1] = 0
                else:
                    self.Calc_E[row, 2*Node_Number+1] = 1

        elif value[1] != '':
            self.Total_Dof -= 1
            self.Calc_E[2*Node_Number+1, 2*Node_Number+1] = 10e20*self.Calc_E[2*Node_Number+1, 2*Node_Number+1]  # type: ignore
            self.Groupe_P[2*Node_Number+1] = value[1]

        return
    
    #判断节点编号连续性 单元编号唯一性 计算自由度数量
    def Node_Elment_Number_Check(self):
        #判断节点编号连续性
        number = []
        for k in self.Node:
            number.append(k)
        number.sort()
        for i in range(len(number)):
            if i != number[i]:
                return False,'Node Number is Not Consecutive, Maker Sure it is Like [0,1,2...]'

        number = []
        for i in self.ElementGroup:
            self.Total_Dof += i.Dof
            if i.Error == True:
                return False, 'Element Warning on No.%s' %i.number
            if i.number in number:
                return False, 'More Than One Elements Have Same Number:%s'%i.number

        return True,'======> Node&Element Number Check Passed! <======'

    # 整体刚度矩阵
    def Calc_Grouped_E(self):
        Gr_E = lil_matrix((self.Node_cnt*2, self.Node_cnt*2))
        print('---',end='')
        for i in self.ElementGroup:
            if i.number%100000 == 10001 and i.number>10005:
                print('\n---',end='')
            if i.number%10000 == 1 and i.number!=1:
                print('ElmE at %s; '%i.number, end='')
            Pose = i.Nd_number
            Ee = i.Element_E
            for row in range(3):
                for col in range(3):
                    G_x = int(Pose[row])
                    G_y = int(Pose[col])
                    Gr_E[2*G_x,2*G_y] += Ee[2*row][2*col]
                    Gr_E[2*G_x+1,2*G_y+1] += Ee[2*row+1][2*col+1]
                    Gr_E[2*G_x+1,2*G_y] += Ee[2*row+1][2*col]
                    Gr_E[2*G_x,2*G_y+1] += Ee[2*row][2*col+1]
        print('')
        return Gr_E


class Solver_Static_3D():
    def __init__(self, Nd, EleList) -> None:
        self.Solver_Type = "3D"
        self.Node, self.Node_cnt = Nd.GetFemNodesAll()
        self.ElementGroup = EleList # 所有元素class 组成的list
        self.Total_Dof = 0
        #判断节点可用
        nNc,word = self.Node_Elment_Number_Check()
        if not nNc:
            print(word)
            exit()
        print(word)
        
        # 载荷矩阵
        self.Groupe_P = np.zeros((3*self.Node_cnt,1))
        self.Fix_Node = np.zeros((3*self.Node_cnt,1))
        self.Disp_Node = np.zeros((3*self.Node_cnt,1))
        self.Fix_Node_dict = {'x':[],'y':[],'z':[]}
        print('---Got Mat P')

        # 总体刚度矩阵
        self.Calc_E = self.Calc_Grouped_E()
        #print(self.Calc_E)
        print('---Got Mat E')

    #求解
    def solve(self):
        #打印总共自由度
        print('\nTotal Dofs ================== %s\n'%self.Total_Dof)

        self.Apply_fix()

        #计算整体的节点位移
        if self.Total_Dof <1000:
            print('Solving Method ........... Doolittle')
            print('Solving Displacement.........\t',end='')
            Solv_E = np.array(self.Calc_E.todense())
            Node_displacement = Doolittle_solver(Solv_E,self.Groupe_P)
        else:
            print('Solving Method ......... Scipy')
            print('Solving Displacement.........\t',end='')
            Solv_E = self.Calc_E.tocsr()
            Node_displacement = np.array([sci_linalg.spsolve(Solv_E,self.Groupe_P)]).T
        print('Done')

        #计算计算各个单元内应变
        print('Calculating Stress&Strain......\t',end='')
        eps = {}
        sigma = {}
        for i in self.ElementGroup:
            #print(i)
            ae = np.zeros((12,1))
            nd = 0
            for j in i.Nd_number:
                j = int(j)
                ae[3*nd] = Node_displacement[3*j]
                ae[3*nd+1] = Node_displacement[3*j+1]
                ae[3*nd+2] = Node_displacement[3*j+2]
                nd += 1
            #ae = np.dot(i.Generate_Elm_G(self.Node_cnt),Node_displacement)
            eps_e = i.Generate_Elm_B()@ae

            v0 = i.MaterialProp['v']
            E0 = i.MaterialProp['E']
            D0 = E0*(1-v0)/((1+v0)*(1-2*v0))
            matrix_D = np.eye(6)
            temp = v0/(1-v0)
            matrix_D[0][1] = temp
            matrix_D[0][2] = temp
            matrix_D[1][2] = temp
            matrix_D[1][0] = temp
            matrix_D[2][0] = temp
            matrix_D[2][1] = temp
            temp = (1-2*v0)/(2*(1-v0))
            matrix_D[3][3] = temp
            matrix_D[4][4] = temp
            matrix_D[5][5] = temp
            D = D0*matrix_D
            
            sig_e = np.dot(D,eps_e)
            eps[i.number] = eps_e
            sigma[i.number] = sig_e
            #print(ae)

        print('Done\n')
        #计算各个单元应力

        return {'Displacement':Node_displacement,'Strain':eps,'Stress':sigma}

    #获得加载情况
    def get_loads(self):
        nd_load = {'Fix_x':[0]*(self.Node_cnt), 
                     'Fix_y':[0]*(self.Node_cnt), 
                     'Fix_z':[0]*(self.Node_cnt),
                     'P_x':[0]*(self.Node_cnt),
                     'P_y':[0]*(self.Node_cnt),
                     'P_z':[0]*(self.Node_cnt)}

        for i in range(self.Node_cnt):
            nd_load['Fix_x'][i] = self.Fix_Node[3*i]
            nd_load['P_x'][i] = self.Groupe_P[3*i]
            nd_load['Fix_y'][i] = self.Fix_Node[3*i+1]
            nd_load['P_y'][i] = self.Groupe_P[3*i+1]
            nd_load['Fix_z'][i] = self.Fix_Node[3*i+2]
            nd_load['P_z'][i] = self.Groupe_P[3*i+2]

        return nd_load

    # 显示所有的网格
    def Draw_Mesh(self,Size = [0.1,0.95]):
        fig = plt.figure()
        ax = fig.add_subplot(111, projection='3d')
        #print(self.Node)

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
            Elm_idj = t.Nd_i_j_m
            
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
            Elm_num = t.Nd_number
            for j in range(len(Elm_num)):
                ax.text(Elm_idj[j][0], Elm_idj[j][1], Elm_idj[j][2],c = 'k',ha='center',va='bottom',s = str(Elm_num[j]), fontsize=7)    # type: ignore
                ax.plot(Elm_idj[j][0], Elm_idj[j][1], Elm_idj[j][2],c='m', marker='.',ls="",ms=5)
            
            tera = Poly3DCollection(pol,edgecolors= 'r', facecolor= [0.5, 1, 1], linewidths=Size[0], alpha=Size[1])
            ax.add_collection3d(tera)  # type: ignore

                    
            #ax.plot(x,y,c='w')
        plt.title('Fem Meshes to Solve')
        plt.show()

    # 定义载荷边界条件
    def Payload(self,Node_Number,value):
        if value[0] != '':
            self.Groupe_P[3*int(Node_Number)][0] = value[0]
        if value[1] != '':
            self.Groupe_P[3*int(Node_Number) + 1][0] = value[1]
        if value[2] != '':
            self.Groupe_P[3*int(Node_Number) + 2][0] = value[2]
        return

    def Apply_fix(self):
        for col in range(3*self.Node_cnt):
            for Node_Number in self.Fix_Node_dict['x']:
                if self.Calc_E[3*Node_Number,col] != 0:
                    self.Calc_E[3*Node_Number,col] = 0.0
                if self.Calc_E[col,3*Node_Number] != 0:
                    self.Calc_E[col,3*Node_Number] = 0.0

            for Node_Number in self.Fix_Node_dict['y']:
                if self.Calc_E[3*Node_Number+1,col] == 0 and self.Calc_E[col,3*Node_Number+1] == 0:
                    continue
                self.Calc_E[3*Node_Number+1,col] = 0
                self.Calc_E[col,3*Node_Number+1] = 0

            for Node_Number in self.Fix_Node_dict['z']:
                if self.Calc_E[3*Node_Number+2,col] == 0 and self.Calc_E[col,3*Node_Number+2] == 0:
                    continue
                self.Calc_E[3*Node_Number+2,col] = 0
                self.Calc_E[col,3*Node_Number+2] = 0
        
        for Node_Number in self.Fix_Node_dict['x']:
            self.Calc_E[3*Node_Number,3*Node_Number] = 1
        for Node_Number in self.Fix_Node_dict['y']:
            self.Calc_E[3*Node_Number+1,3*Node_Number+1] = 1
        for Node_Number in self.Fix_Node_dict['z']:
            self.Calc_E[3*Node_Number+2,3*Node_Number+2] = 1

    # 定义位移边界条件
    def Displacement(self,Node_Number,value):
        Node_Number = int(Node_Number)
        if value[0] == 0:
            self.Total_Dof -= 1
            self.Groupe_P[3*Node_Number] = 0
            
            # 改1法 (固定)
            self.Fix_Node[3*Node_Number] = 1
            if Node_Number not in self.Fix_Node_dict['x']:
                self.Fix_Node_dict['x'].append(Node_Number)
            """for col in range(3*self.Node_cnt):
                if self.Calc_E[3*Node_Number,col] == 0 and self.Calc_E[col,3*Node_Number] == 0:
                    continue
                self.Calc_E[3*Node_Number,col] = 0
                self.Calc_E[col,3*Node_Number] = 0
            self.Calc_E[3*Node_Number,3*Node_Number] = 1"""

        elif value[0] != '':
            self.Total_Dof -= 1
            self.Calc_E[3*Node_Number,3*Node_Number] = 10e20*1 # type: ignore
            self.Groupe_P[3*Node_Number] = 10e20*value[0]

        if value[1] == 0:
            self.Total_Dof -= 1
            self.Groupe_P[3*Node_Number+1] = 0
            
            # 改1法(fix)
            self.Fix_Node[3*Node_Number+1] = 1
            if Node_Number not in self.Fix_Node_dict['y']:
                self.Fix_Node_dict['y'].append(Node_Number)
            """for col in range(3*self.Node_cnt):
                if self.Calc_E[3*Node_Number+1,col] == 0 and self.Calc_E[col,3*Node_Number+1] == 0:
                    continue
                self.Calc_E[3*Node_Number+1,col] = 0
                self.Calc_E[col,3*Node_Number+1] = 0
            self.Calc_E[3*Node_Number+1,3*Node_Number+1] = 1"""

        elif value[1] != '':
            self.Total_Dof -= 1
            self.Calc_E[3*Node_Number+1, 3*Node_Number+1] = 10e20*1  # type: ignore
            self.Groupe_P[3*Node_Number+1] = 10e20*value[1]

        if value[2] == 0:
            self.Total_Dof -= 1
            self.Groupe_P[3*Node_Number+2] = 0
            
            # 改1法(fix)
            self.Fix_Node[3*Node_Number+2] = 1
            if Node_Number not in self.Fix_Node_dict['z']:
                self.Fix_Node_dict['z'].append(Node_Number)
            """for col in range(3*self.Node_cnt):
                if self.Calc_E[3*Node_Number+2,col] == 0 and self.Calc_E[col,3*Node_Number+2] == 0:
                    continue
                self.Calc_E[3*Node_Number+2,col] = 0
                self.Calc_E[col,3*Node_Number+2] = 0
            self.Calc_E[3*Node_Number+2,3*Node_Number+2] = 1"""


        elif value[2] != '':
            self.Total_Dof -= 1
            self.Calc_E[3*Node_Number+2, 3*Node_Number+2] = 10e20*1  # type: ignore
            self.Groupe_P[3*Node_Number+2] = 10e20*value[2]

        return
    
    #判断节点编号连续性 单元编号唯一性 计算自由度数量
    def Node_Elment_Number_Check(self):
        #判断节点编号连续性
        number = []
        for k in self.Node:
            number.append(k)
        number.sort()
        for i in range(len(number)):
            if i != number[i]:
                return False,'Node Number is Not Consecutive, Maker Sure it is Like [0,1,2...]'

        number = []
        for i in self.ElementGroup:
            self.Total_Dof += i.Dof
            if i.Error == True:
                return False, 'Element Warning on No.%s' %i.number
            if i.number in number:
                return False, 'More Than One Elements Have Same Number:%s'%i.number

        return True,'======> Node&Element Number Check Passed! <======'

    # 整体刚度矩阵
    def Calc_Grouped_E(self):
        Gr_E = lil_matrix((self.Node_cnt*3, self.Node_cnt*3))
        elm_count = len(self.ElementGroup)
        #print(Gr_E==0)
        #print('---',end='')
        print('---Calculating E: 000%', end='')
        for i in self.ElementGroup:
            #print('\n---',end='')
            if i.number%100 == 1 and i.number!=1:
                print("\r", end='', flush=True)
                print('---Calculating E: %03d%%'%(100*i.number/elm_count), end='')
                #print(time.strftime("当前时间为：%Y-%m-%d %H:%M:%S", time.localtime()), end="")
            Pose = i.Nd_number
            Ee = i.Element_E
            #print(i.Volume)
            for row in range(len(i.Nd_number)):
                for col in range(len(i.Nd_number)):
                    G_x = int(Pose[row])
                    G_y = int(Pose[col])
                    
                    Gr_E[3*G_x,3*G_y] += Ee[3*row][3*col]
                    Gr_E[3*G_x,3*G_y+1] += Ee[3*row][3*col+1]
                    Gr_E[3*G_x,3*G_y+2] += Ee[3*row][3*col+2]

                    Gr_E[3*G_x+1,3*G_y] += Ee[3*row+1][3*col]
                    Gr_E[3*G_x+1,3*G_y+1] += Ee[3*row+1][3*col+1]
                    Gr_E[3*G_x+1,3*G_y+2] += Ee[3*row+1][3*col+2]
                    
                    Gr_E[3*G_x+2,3*G_y] += Ee[3*row+2][3*col]
                    Gr_E[3*G_x+2,3*G_y+1] += Ee[3*row+2][3*col+1]
                    Gr_E[3*G_x+2,3*G_y+2] += Ee[3*row+2][3*col+2]
                    
        #print(Gr_E)
        #print(Gr_E.T==Gr_E)   
        print("\r", end='', flush=True)
        print('---Calculating E: %2d%%'%(100), end='')
        print('')
        return Gr_E



#获取字典中最大的值 return 节点dict 最大 最小
def get_von_mises(ans_dict, dim=2):
    if dim == 2:
        return 0,0


if __name__ == '__main__':
    Nd = FemNodes.Fem_Nodes() #type:ignore
    Nd.Add_Fem_Nodes_With_Number([ [0,0,0],[3,0,0],[0,4,0],[2,8,0] ],[ 0,1,2,3 ])
    Fe = FemElement.Triangle3Node_2d(1,[0,1,2],Nd,{'E':2e11,'t':1,'v':0.2})  # type: ignore
    #print(Fe.Element_E)
    a = Solver_Static_2D(Nd,[Fe])
    print(a.Calc_E)
    a.Displacement(0,[0,''])
    print('------------------')
    print(a.Calc_E)
    