from asyncio.windows_events import NULL
import nntplib
import matplotlib.patches as mpatch
import matplotlib.pyplot as plt
import numpy as np
import math

class Triangle3Node():
    # Nodes-->[i,j,m]结点编号  MaterialProp {'E':弹性模量pa,'v':泊松比,'t':厚度m，} G_mat 转换矩阵
    def __init__(self,Nodes_number,Nodes_class,MaterialProp) -> None:
        self.Warning = False
        #得到节点坐标
        Nodes = Nodes_class.GetFemNodes(Nodes_number)

        #判断节点坐标是否满足要求————平面，三个
        if len(Nodes)!=3:
            self.Warning = True
            return
        for i in Nodes:
            if len(i)!=3:
                self.Warning = True
                return

        # 将矩阵节点参数储存
        self.Nd_i_j_m = [Nodes[0],Nodes[1],Nodes[2]]
        self.Nd_number = Nodes_number # 节点的编号
        self.abc = self.Get_abc()
    
        #计算矩阵面积
        A_mat = np.mat([[Nodes[0][0], Nodes[0][1], 1],
                        [Nodes[1][0], Nodes[1][1], 1],
                        [Nodes[2][0], Nodes[2][1], 1]])
        self.Area = abs(np.linalg.det(A_mat))/2.0
        if self.Area == 0:#如果面积为0则矩阵出现问题
            self.Warning = True
            return

        #计算刚度矩阵 载荷矩阵
        self.Element_E = self.Generate_Elm_E(MaterialProp)
        self.Element_P = [0]*6
        
        return

    # 将单元绘制出来
    def Draw_Elm(self,Size = [10,15],ifNode=True):
        fig,ax =plt.subplots()
        pot = [i[0:2] for i in self.Nd_i_j_m]
        tri = mpatch.Polygon(pot)
        ax.set_xlim(-1,5)
        ax.set_ylim(-1,5)
        ax.add_patch(tri)
        
        if ifNode:
            for i in range(3):
                Pos = self.Nd_i_j_m[i]
                Numb = self.Nd_number[i]
                plt.scatter(Pos[0], Pos[1], c='red', s=Size[0], label='Nodes')
                plt.text(Pos[0],Pos[1],Numb,ha='center',va='bottom',fontsize=Size[1])
        plt.show()

    # 根据需要的大小生成给定的转换矩阵
    def Generate_Elm_G(self, num_N):
        i = self.Nd_number[0]
        j = self.Nd_number[1]
        m = self.Nd_number[2]
        G = np.zeros((6,2*num_N))
        
        G[0][2*i] = 1
        G[1][2*i+1] = 1
        G[2][2*j] = 1
        G[3][2*j+1] = 1
        G[4][2*m] = 1
        G[5][2*m+1] = 1
        return G

    # 生成单元刚度矩阵
    def Generate_Elm_E(self,Material):
        #获取矩阵前乘常量
        try :
            BDBtA = Material['E']*Material['t']/( 4*self.Area*(1-math.pow(Material['v'],2)) )
            v0 = Material['v']
        except KeyError:
            self.Warning = True
            return np.ndarray((0))
        
        #开始计算E矩阵
        E = np.zeros((6,6))


        for r in range(3):
            for s in range(3):
                K1 = self.abc[1][r]*self.abc[1][s] + ((1-v0)/2)*self.abc[2][r]*self.abc[2][s]
                K2 = v0*self.abc[2][r]*self.abc[1][s] + ((1-v0)/2)*self.abc[1][r]*self.abc[2][s]
                K3 = v0*self.abc[1][r]*self.abc[1][s] + ((1-v0)/2)*self.abc[2][r]*self.abc[1][s]
                K4 = self.abc[2][r]*self.abc[2][s] + ((1-v0)/2)*self.abc[1][r]*self.abc[1][s]

                E[2*r][2*s] = K1
                E[2*r+1][2*s] = K2
                E[2*r][2*s+1] = K3
                E[2*r+1][2*s+1] = K4
                
        E = BDBtA*E
        #print(E)
        return E

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