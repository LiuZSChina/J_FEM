
import string
from tokenize import String
import matplotlib.patches as mpatch
import matplotlib.pyplot as plt
import numpy as np
import math
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

class Triangle3Node_2d():
    # Elm_num -->单元编号 Nodes_number-->[i,j,m]结点编号; Node_classs--> class Fem_Nodes();  MaterialProp-->{'E':弹性模量pa,'v':泊松比,'t':厚度m，}
    def __init__(self,Elm_num,Nodes_number,Nodes_class,MaterialProp,solve_type='2d_strain') -> None:
        self.Dof = 6
        self.Warning = False
        self.number = Elm_num
        self.MaterialProp = MaterialProp
        #得到节点坐标
        Nodes = Nodes_class.GetFemNodes(Nodes_number)
        self.solve_type = solve_type
        #判断节点坐标是否满足要求————平面，三个
        if len(Nodes)!=3:
            self.Warning = True
            print('!===Not Enough Nodes===!')
            return
        for i in Nodes:
            if len(i)!=3:
                self.Warning = True
                print('!===Node Dim ERR===!')
                return

        # 将矩阵节点参数储存
        self.Nd_i_j_m = [Nodes[0],Nodes[1],Nodes[2]]
        self.Nd_number = Nodes_number # 节点的编号
        self.abc = self.Get_abc()

        self.Elm_pos = np.array([[Nodes[0][0]],
                                [Nodes[0][1]],
                                [Nodes[1][0]],
                                [Nodes[1][1]],
                                [Nodes[2][0]],
                                [Nodes[2][1]]])

    
        #计算矩阵面积
        self.Area = (self.abc[1][0]*self.abc[2][1]-self.abc[1][1]*self.abc[2][0])/2
        #print(self.Area)
        if self.Area == 0:#如果面积为0则矩阵出现问题
            self.Warning = True
            print('!===ELm Aera = 0===!')
            return

        #计算刚度矩阵 载荷矩阵
        self.Element_E = self.Generate_Elm_E(MaterialProp)
        self.Element_P = [0]*6
        
        return

    # 将单元绘制出来
    def Draw_Elm(self,Size = [10,10],ifNode=True):
        fig,ax =plt.subplots()
        pot = [i[0:2] for i in self.Nd_i_j_m]
        tri = mpatch.Polygon(pot)
        #ax.set_xlim(-1,5)
        #ax.set_ylim(-1,5)
        ax.add_patch(tri)
        
        if ifNode:
            for i in range(3):
                Pos = self.Nd_i_j_m[i]
                Numb = self.Nd_number[i]
                plt.scatter(Pos[0], Pos[1], c='red', s=Size[0], label='Nodes')
                plt.text(Pos[0],Pos[1],Numb,ha='center',va='bottom',fontsize=Size[1])
        plt.show()

    """# 根据需要的大小生成给定的转换矩阵 输入节点数
    def Generate_Elm_G(self, num_N):
        i = int(self.Nd_number[0])
        j = int(self.Nd_number[1])
        m = int(self.Nd_number[2])
        G = np.zeros((6,2*num_N))
        
        G[0][2*i] = 1
        G[1][2*i+1] = 1
        G[2][2*j] = 1
        G[3][2*j+1] = 1
        G[4][2*m] = 1
        G[5][2*m+1] = 1
        return G"""

    # 生成单元刚度矩阵
    def Generate_Elm_E(self,Material):
        #获取矩阵前乘常量
        try :
            E0 = Material['E']
            thik = Material['t']
            #BDBtA = Material['E']*Material['t']/( 4*self.Area* (1-math.pow(Material['v'],2)) )
            v0 = Material['v']
        except KeyError:
            self.Warning = True
            return np.ndarray((0))

        #判断平面应力还是应变
        if self.solve_type == '2d_strain':
            #print('a')
            E0 = E0/(1-math.pow(Material['v'],2))
            v0 = v0/(1-v0)

        BDBtA = E0*thik/(  4*self.Area* (1-math.pow(v0,2)) )
        #开始计算E矩阵
        E = np.zeros((6,6))


        for r in range(3):
            for s in range(3):
                K1 = self.abc[1][r]*self.abc[1][s] + ((1-v0)/2)*self.abc[2][r]*self.abc[2][s]
                K2 = v0*self.abc[2][r]*self.abc[1][s] + ((1-v0)/2)*self.abc[1][r]*self.abc[2][s]
                K3 = v0*self.abc[1][r]*self.abc[2][s] + ((1-v0)/2)*self.abc[2][r]*self.abc[1][s]
                K4 = self.abc[2][r]*self.abc[2][s] + ((1-v0)/2)*self.abc[1][r]*self.abc[1][s]

                E[2*r][2*s] = K1
                E[2*r+1][2*s] = K2
                E[2*r][2*s+1] = K3
                E[2*r+1][2*s+1] = K4
                
        E = BDBtA*E
        #print(E)
        return E

    #生成单元应变矩阵
    def Generate_Elm_B(self):
        B_mat = np.array([[self.abc[1][0], 0 , self.abc[1][1], 0 , self.abc[1][2], 0],
                            [0 , self.abc[2][0], 0 , self.abc[2][1], 0 , self.abc[2][2]],   
                            [self.abc[2][0], self.abc[1][0], self.abc[2][1], self.abc[1][1], self.abc[2][2], self.abc[1][2]]])
        B_mat = (1/(2*self.Area))*B_mat
        return B_mat

    # 生成矩阵位置参数abc
    def Get_abc(self):
        ai = self.Nd_i_j_m[1][0]*self.Nd_i_j_m[2][1] - self.Nd_i_j_m[2][0]*self.Nd_i_j_m[1][1]
        aj = self.Nd_i_j_m[2][0]*self.Nd_i_j_m[0][1] - self.Nd_i_j_m[0][0]*self.Nd_i_j_m[2][1]
        am = self.Nd_i_j_m[0][0]*self.Nd_i_j_m[1][1] - self.Nd_i_j_m[1][0]*self.Nd_i_j_m[0][1]

        bi = self.Nd_i_j_m[1][1] - self.Nd_i_j_m[2][1]
        bj = self.Nd_i_j_m[2][1] - self.Nd_i_j_m[0][1]
        bm = self.Nd_i_j_m[0][1] - self.Nd_i_j_m[1][1]

        ci = self.Nd_i_j_m[2][0] - self.Nd_i_j_m[1][0]
        cj = self.Nd_i_j_m[0][0] - self.Nd_i_j_m[2][0]
        cm = self.Nd_i_j_m[1][0] - self.Nd_i_j_m[0][0]

        return [[ai,aj,am],[bi,bj,bm],[ci,cj,cm]]



class Quad4Node_2d():
    # Elm_num -->单元编号 Nodes_number-->[i,j,m]结点编号; Node_classs--> class Fem_Nodes();  MaterialProp-->{'E':弹性模量pa,'v':泊松比,'t':厚度m，}
    def __init__(self,Elm_num,Nodes_number,Nodes_class,MaterialProp,solve_type='2d_strain') -> None:
        self.Dof = 8
        self.Warning = False
        self.number = Elm_num
        self.MaterialProp = MaterialProp
        #得到节点坐标
        Nodes = Nodes_class.GetFemNodes(Nodes_number)
        self.solve_type = solve_type
        #判断节点坐标是否满足要求————平面，三个
        if len(Nodes)!=4:
            self.Warning = True
            print('!===Not Enough Nodes===!')
            return
        for i in Nodes:
            if len(i)!=3:
                self.Warning = True
                print('!===Node Dim ERR===!')
                return

        # 将矩阵节点参数储存
        self.Nd_i_j_m = [Nodes[0],Nodes[1],Nodes[2],Nodes[3]]
        self.Nd_number = Nodes_number # 节点的编号
        self.abc = self.Get_abc()

        self.Elm_pos = np.array([[Nodes[0][0]], 
                                [Nodes[0][1]],
                                [Nodes[1][0]],
                                [Nodes[1][1]],
                                [Nodes[2][0]],
                                [Nodes[2][1]],
                                [Nodes[3][0]],
                                [Nodes[3][1]]])# aka u v

        """-----------------------------------------------------------------------------"""
        self.Warning = True
        """-----------------------------------------------------------------------------"""
        self.Area = 0
        """#计算矩阵面积
        self.Area = (self.abc[1][0]*self.abc[2][1]-self.abc[1][1]*self.abc[2][0])/2
        #print(self.Area)
        if self.Area == 0:#如果面积为0则矩阵出现问题
            self.Warning = True
            print('!===ELm Aera = 0===!')
            return

        #计算刚度矩阵 载荷矩阵
        self.Element_E = self.Generate_Elm_E(MaterialProp)
        self.Element_P = [0]*6
        """
        return

    # 将单元绘制出来
    def Draw_Elm(self,Size = [10,10],ifNode=True):
        fig,ax =plt.subplots()
        pot = [i[0:2] for i in self.Nd_i_j_m]
        tri = mpatch.Polygon(pot)
        #ax.set_xlim(-1,5)
        #ax.set_ylim(-1,5)
        ax.add_patch(tri)
        
        if ifNode:
            for i in range(4):
                Pos = self.Nd_i_j_m[i]
                Numb = self.Nd_number[i]
                plt.scatter(Pos[0], Pos[1], c='red', s=Size[0], label='Nodes')
                plt.text(Pos[0],Pos[1],Numb,ha='center',va='bottom',fontsize=Size[1])
        plt.show()

    # 生成单元刚度矩阵
    def Generate_Elm_E(self,Material):
        #获取矩阵前乘常量
        try :
            E0 = Material['E']
            thik = Material['t']
            #BDBtA = Material['E']*Material['t']/( 4*self.Area* (1-math.pow(Material['v'],2)) )
            v0 = Material['v']
        except KeyError:
            self.Warning = True
            return np.ndarray((0))

        #判断平面应力还是应变
        if self.solve_type == '2d_strain':
            #print('a')
            E0 = E0/(1-math.pow(Material['v'],2))
            v0 = v0/(1-v0)

        BDBtA = E0*thik/(  4*self.Area* (1-math.pow(v0,2)) )
        #开始计算E矩阵
        E = np.zeros((6,6))


        for r in range(3):
            for s in range(3):
                K1 = self.abc[1][r]*self.abc[1][s] + ((1-v0)/2)*self.abc[2][r]*self.abc[2][s]
                K2 = v0*self.abc[2][r]*self.abc[1][s] + ((1-v0)/2)*self.abc[1][r]*self.abc[2][s]
                K3 = v0*self.abc[1][r]*self.abc[2][s] + ((1-v0)/2)*self.abc[2][r]*self.abc[1][s]
                K4 = self.abc[2][r]*self.abc[2][s] + ((1-v0)/2)*self.abc[1][r]*self.abc[1][s]

                E[2*r][2*s] = K1
                E[2*r+1][2*s] = K2
                E[2*r][2*s+1] = K3
                E[2*r+1][2*s+1] = K4
                
        E = BDBtA*E
        #print(E)
        return E

    #生成单元应变矩阵
    def Generate_Elm_B(self):
        B_mat = np.array([[self.abc[1][0], 0 , self.abc[1][1], 0 , self.abc[1][2], 0],
                            [0 , self.abc[2][0], 0 , self.abc[2][1], 0 , self.abc[2][2]],   
                            [self.abc[2][0], self.abc[1][0], self.abc[2][1], self.abc[1][1], self.abc[2][2], self.abc[1][2]]])
        B_mat = (1/(2*self.Area))*B_mat
        return B_mat

    # 生成矩阵位置参数abc
    def Get_abc(self):
        ai = self.Nd_i_j_m[1][0]*self.Nd_i_j_m[2][1] - self.Nd_i_j_m[2][0]*self.Nd_i_j_m[1][1]
        aj = self.Nd_i_j_m[2][0]*self.Nd_i_j_m[0][1] - self.Nd_i_j_m[0][0]*self.Nd_i_j_m[2][1]
        am = self.Nd_i_j_m[0][0]*self.Nd_i_j_m[1][1] - self.Nd_i_j_m[1][0]*self.Nd_i_j_m[0][1]

        bi = self.Nd_i_j_m[1][1] - self.Nd_i_j_m[2][1]
        bj = self.Nd_i_j_m[2][1] - self.Nd_i_j_m[0][1]
        bm = self.Nd_i_j_m[0][1] - self.Nd_i_j_m[1][1]

        ci = self.Nd_i_j_m[2][0] - self.Nd_i_j_m[1][0]
        cj = self.Nd_i_j_m[0][0] - self.Nd_i_j_m[2][0]
        cm = self.Nd_i_j_m[1][0] - self.Nd_i_j_m[0][0]

        return [[ai,aj,am],[bi,bj,bm],[ci,cj,cm]]



class Tera4Node_3d(): #tetrahedron
    # Elm_num -->单元编号 Nodes_number-->[i,j,m]结点编号; Node_classs--> class Fem_Nodes();  MaterialProp-->{'E':弹性模量pa,'v':泊松比,'t':厚度m，}
    def __init__(self,Elm_num,Nodes_number,Nodes_class,MaterialProp,solve_type='2d_strain') -> None:
        self.Dof = 12
        self.Warning = False
        self.number = Elm_num
        self.MaterialProp = MaterialProp
        #得到节点坐标
        Nodes = Nodes_class.GetFemNodes(Nodes_number)
        self.solve_type = solve_type
        #判断节点坐标是否满足要求————平面，三个
        if len(Nodes)!=4:
            self.Warning = True
            print('!===Not Enough Nodes===!')
            return
        for i in Nodes:
            if len(i)!=3:
                self.Warning = True
                print('!===Node Dim ERR===!')
                return

        # 将矩阵节点参数储存
        self.Nd_i_j_m = [[i for i in Nodes[0]], [i for i in Nodes[1]], [i for i in Nodes[2]], [i for i in Nodes[3]]]
        #print(self.Nd_i_j_m)
        self.Nd_number = Nodes_number # 节点的编号

        self.abc = self.Get_abc()
        #print(self.abc)
        self.Elm_pos = np.array([[Nodes[0][0]], 
                                [Nodes[0][1]],
                                [Nodes[0][2]],
                                [Nodes[1][0]],
                                [Nodes[1][1]],
                                [Nodes[1][2]],
                                [Nodes[2][0]],
                                [Nodes[2][1]],
                                [Nodes[2][2]],
                                [Nodes[3][0]],
                                [Nodes[3][1]],
                                [Nodes[3][2]]])# aka u v

        
        self.Volume = self.calc_volume()
        #print("Volume is :%f"%self.Volume)
        if self.Volume == 0:#如果面积为0则矩阵出现问题
            self.Warning = True
            print('!===ELm Volume = 0===!')
            return

        #计算刚度矩阵 载荷矩阵
        self.Element_E = self.Generate_Elm_E(MaterialProp)
        
        self.Element_P = [0]*12
        return

    # 计算单元体积
    def calc_volume(self):
        matrix_v = np.ones((4,4))
        for i in range(4):
            for j in range(3):
                matrix_v[i][j+1] = self.Nd_i_j_m[i][j]
        #print(matrix_v)
        v = np.linalg.det(matrix_v)/6
        return abs(v)

    # 将单元绘制出来
    def Draw_Elm(self,psize = [10,10],ifNode=True):
        fig = plt.figure()
        ax = fig.add_subplot(111, projection='3d')
        
        # Set axis aspect to fit the elm.
        print_list = self.Nd_i_j_m
        x_bound = [min([i[0] for i in print_list]),max([i[0] for i in print_list])]
        y_bound = [min([i[1] for i in print_list]),max([i[1] for i in print_list])]
        z_bound = [min([i[2] for i in print_list]),max([i[2] for i in print_list])]   
        max_size = max([x_bound[1]-x_bound[0], y_bound[1]-y_bound[0], y_bound[1]-y_bound[0]])
        ax.set_xlim([(sum(x_bound)/2) - max_size/2 , (sum(x_bound)/2) + max_size/2])  # type: ignore
        ax.set_ylim([(sum(y_bound)/2) - max_size/2 , (sum(y_bound)/2) + max_size/2])  # type: ignore
        ax.set_zlim([(sum(z_bound)/2) - max_size/2 , (sum(z_bound)/2) + max_size/2])  # type: ignore
        
        # 画各个面和边线
        pol = []
        for i in range(2):
            ii = (self.Nd_i_j_m[i][0], self.Nd_i_j_m[i][1], self.Nd_i_j_m[i][2])
            for j in range(i+1,3):
                jj = (self.Nd_i_j_m[j][0], self.Nd_i_j_m[j][1], self.Nd_i_j_m[j][2])
                for k in range(j+1,4):
                    kk = (self.Nd_i_j_m[k][0], self.Nd_i_j_m[k][1], self.Nd_i_j_m[k][2])
                    pol.append([ii, jj, kk])
        
        tera = Poly3DCollection(pol,edgecolors= 'w', facecolor= [0.5, 0.5, 1], linewidths=1, alpha=0.9)
        ax.add_collection3d(tera)  # type: ignore

        #print every nodes
        for k in range(len(print_list)):
            i = print_list[k]
            ax.text(i[0], i[1], i[2],c = 'k',ha='center',va='bottom',s = str(self.Nd_number[k]), fontsize=psize[0])    # type: ignore
            ax.plot(i[0], i[1], i[2],c='red', marker='.',ls="",ms=psize[1])
        
        plt.show()

    # 生成单元刚度矩阵
    def Generate_Elm_E(self,Material):
        #获取矩阵前乘常量
        try :
            E0 = Material['E']
            v0 = Material['v']
        except KeyError:
            self.Warning = True
            return np.ndarray((0))

        #计算弹性矩阵
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
        matrix_D = D0*matrix_D
        #print(matrix_D)
        #print(matrix_D.T == matrix_D)

        #计算B矩阵
        """matB = np.zeros((6,12))
        flag = 1
        for i in range(4):
            if i == 0 or i == 2:
                flag = 1
            else:
                flag = -1
            matB[0][i*3] = self.abc[1][i]*flag
            matB[3][i*3] = self.abc[2][i]*flag
            matB[5][i*3] = self.abc[3][i]*flag

            matB[1][i*3+1] = self.abc[2][i]*flag
            matB[3][i*3+1] = self.abc[1][i]*flag
            matB[4][i*3+1] = self.abc[3][i]*flag

            matB[2][i*3+2] = self.abc[3][i]*flag
            matB[4][i*3+2] = self.abc[2][i]*flag
            matB[5][i*3+2] = self.abc[1][i]*flag"""
        matB = self.Generate_Elm_B()
        #print(matB)
        #print(matB)

        #开始计算E矩阵
        matrix_E = matB.T@matrix_D@matB
        matrix_E = self.Volume*matrix_E
        #E = np.dot(matB.T,matB)   self.Volume*
        #print(matrix_E)
        #print(matrix_E.T==matrix_E)
        return matrix_E

    #生成B矩阵
    def Generate_Elm_B(self):
       #计算B矩阵
        matB = np.zeros((6,12))
        flag = 1
        for i in range(4):
            if i == 0 or i == 2:
                flag = 1
            else:
                flag = -1
            matB[0][i*3] = self.abc[1][i]*flag
            matB[3][i*3] = self.abc[2][i]*flag
            matB[5][i*3] = self.abc[3][i]*flag

            matB[1][i*3+1] = self.abc[2][i]*flag
            matB[3][i*3+1] = self.abc[1][i]*flag
            matB[4][i*3+1] = self.abc[3][i]*flag

            matB[2][i*3+2] = self.abc[3][i]*flag
            matB[4][i*3+2] = self.abc[2][i]*flag
            matB[5][i*3+2] = self.abc[1][i]*flag
        matB = (1/(6*self.Volume))*matB
        return matB

    # 生成矩阵位置参数abc
    def Get_abc(self):
        a = [0,0,0,0]
        b = [0,0,0,0]
        c = [0,0,0,0]
        d = [0,0,0,0]
        for i in range(4):
            matrix_a = np.array([ self.Nd_i_j_m[(i+1)%4] , self.Nd_i_j_m[(i+2)%4], self.Nd_i_j_m[(i+3)%4]])
            a[i] = np.linalg.det(matrix_a)
            #print(matrix_a)
            #print(a[i])

            matrix_b = np.zeros_like(matrix_a)
            for k in range(3):
                matrix_b[k][0] = 1
                for j in range(1,3):
                    matrix_b[k][j] = matrix_a[k][j]
            b[i] = np.linalg.det(matrix_b)
            #print(matrix_b)
            #print(b[i])

            matrix_c = np.zeros_like(matrix_a)
            for k in range(3):
                matrix_c[k][1] = 1
                matrix_c[k][0] = matrix_a[k][0]
                matrix_c[k][2] = matrix_a[k][2]
            c[i] = np.linalg.det(matrix_c)
            #print(matrix_c)
            #print(c[i])

            matrix_d = np.zeros_like(matrix_a)
            for k in range(3):
                matrix_d[k][2] = 1
                matrix_d[k][0] = matrix_a[k][0]
                matrix_d[k][1] = matrix_a[k][1]
            d[i] = np.linalg.det(matrix_d)
            #print(matrix_d)
            #print(d[i])
        #print([a,b,c,d])
        return [a,b,c,d]