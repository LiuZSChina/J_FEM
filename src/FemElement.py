from email.policy import default
import matplotlib.patches as mpatch
import matplotlib.pyplot as plt
import numpy as np
import math

class Triangle3Node():
    # Nodes-->[i,j,m]结点编号  MaterialProp {'E':弹性模量Mpa,'v':泊松比,'t':厚度mm，} G_mat 转换矩阵
    def __init__(self,Nodes_number,Nodes_class,MaterialProp,G_mat) -> None:
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

        # 将矩阵参数储存
        self.Nd_i_j_m = [Nodes[0],Nodes[1],Nodes[2]]
        self.Nd_number = Nodes_number
        self.abc = self.Get_abc()
    
        #计算矩阵面积
        A_mat = np.mat([[Nodes[0][0], Nodes[0][1], 1],
                        [Nodes[1][0], Nodes[1][1], 1],
                        [Nodes[2][0], Nodes[2][1], 1]])
        self.Area = abs(np.linalg.det(A_mat))/2.0
        if self.Area == 0:#如果面积为0则矩阵出现问题
            self.Warning = True
            return
        
        #print('Size=',str(self.Area))
        
        return

    # 将单元绘制出来
    def Draw_Elm(self):
        fig,ax =plt.subplots()
        pot = [i[0:2] for i in self.Nd_i_j_m]
        tri = mpatch.Polygon(pot)
        ax.set_xlim(-1,5)
        ax.set_ylim(-1,5)
        ax.add_patch(tri)

        for i in self.Nd_i_j_m:
            plt.scatter(i[0], i[1], c='red', s=10, label='Nodes')
        plt.show()

    # 生成单元刚度矩阵
    def Generate_Elm_E(self,Material):
        #获取矩阵前乘常量
        try :
            BDBtA = Material['E']*Material['t']/( 4*self.Area*(1-math.pow(Material['v'],2)) )
            v0 = Material['v']
        except KeyError:
            self.Warning = True
            return np.mat([])
        
        #开始计算E矩阵
        E = np.zeros((6,6))
        print(E)

        for r in range(3):
            for s in range(3):
                continue


        return BDBtA

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