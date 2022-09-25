import math
from pydoc import doc
import numpy as np
import matplotlib.patches as mpatch
import matplotlib.pyplot as plt

try:
    import FemNodes
    import FemElement
except ModuleNotFoundError:
    import src.FemNodes
    import src.FemElement


class Solver_Static():
    def __init__(self, Nd, EleList) -> None:

        self.Node, self.Node_cnt = Nd.GetFemNodesAll()
        self.ElementGroup = EleList

        #判断节点可用
        nNc,word = self.Node_Elment_Number_Check()
        if not nNc:
            print(word)
            exit()
        print(word)
        
        # 载荷矩阵
        self.Groupe_P = np.zeros((2*self.Node_cnt,1))

        # 总体刚度矩阵
        self.Groupe_E = self.Calc_Grouped_E()

    #求解
    def solve(self):
        #计算整体的节点位移
        Node_displacement = np.dot(np.linalg.inv(self.Groupe_E),self.Groupe_P)

        #计算计算各个单元内应变
        eps = {}
        sigma = {}
        for i in self.ElementGroup:
            ae = np.dot(i.Generate_Elm_G(self.Node_cnt),Node_displacement)
            eps_e = np.dot(i.Generate_Elm_B(),ae)
            D = np.array([
                [1, i.MaterialProp['v'], 0],
                [i.MaterialProp['v'], 1, 0],
                [0, 0, (1-i.MaterialProp['v'])/2]])
            D = (i.MaterialProp['E']/(1-math.pow(i.MaterialProp['v'],2)))*D
            sig_e = np.dot(D,eps_e)
            eps[i.number] = eps_e
            sigma[i.number] = sig_e

        #计算各个单元应力

        return {'Displacement':Node_displacement,'Strain':eps,'Stress':sigma}

    # 显示所有的网格
    def Draw_Mesh(self,Size = [10,20]):
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
                for j in range(3):
                    Pos = i.Nd_i_j_m[j]
                    Numb = i.Nd_number[j]
                    plt.scatter(Pos[0], Pos[1], c='red', s=Size[0], label='Nodes')
                    plt.text(Pos[0],Pos[1],Numb,ha='center',va='bottom',fontsize=Size[1])
                    x.append(Pos[0])
                    y.append(Pos[1])
                    
            ax.plot(x,y,c='w')

        plt.show()

    #后处理，获得节点位移
    def Post_Node_Displacement(self,Displacement,Node_number,scaler=1):
        x_disp = scaler*Displacement[Node_number*2][0]
        y_disp = scaler*Displacement[Node_number*2+1][0]
        return {'x':x_disp,'y':y_disp}

    # 定义载荷边界条件
    def Payload(self,Node_Number,value):
        if value[0] != '':
            self.Groupe_P[2*Node_Number][0] = value[0]
        if value[1] != '':
            self.Groupe_P[2*Node_Number+1][0] = value[1]
        return

    # 定义位移边界条件
    def Displacement(self,Node_Number,value):
        if value[0] == 0:
            self.Groupe_P[2*Node_Number] = 0
            
            # 改1法
            for col in range(2*self.Node_cnt):
                if col != 2*Node_Number:
                    self.Groupe_E[2*Node_Number][col] = 0
                else:
                    self.Groupe_E[2*Node_Number][col] = 1
            for row in range(2*self.Node_cnt):
                if row != 2*Node_Number:
                    self.Groupe_E[row][2*Node_Number] = 0
                else:
                    self.Groupe_E[row][2*Node_Number] = 1

        elif value[0] != '':
            self.Groupe_E[2*Node_Number][2*Node_Number] = 10e20*self.Groupe_E[2*Node_Number][2*Node_Number]
            self.Groupe_P[2*Node_Number] = value[0]

        if value[1] == 0:
            self.Groupe_P[2*Node_Number+1] = 0
            
            # 改1法
            for col in range(2*self.Node_cnt):
                if col != 2*Node_Number+1:
                    self.Groupe_E[2*Node_Number+1][col] = 0
                else:
                    self.Groupe_E[2*Node_Number+1][col] = 1
            for row in range(2*self.Node_cnt):
                if row != 2*Node_Number+1:
                    self.Groupe_E[row][2*Node_Number+1] = 0
                else:
                    self.Groupe_E[row][2*Node_Number+1] = 1

        elif value[1] != '':
            self.Groupe_E[2*Node_Number+1][2*Node_Number+1] = 10e20*self.Groupe_E[2*Node_Number+1][2*Node_Number+1]
            self.Groupe_P[2*Node_Number+1] = value[1]

        return
    
    #判断节点编号连续性 单元编号唯一性
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
            if i.Warning == True:
                return False, 'Element Warning on No.%s' %i.number
            if i.number in number:
                return False, 'More Than One Elements Have Same Number:%s'%i.number

        return True,'======> Node&Element Number Check Passed! <======'

    # 整体刚度矩阵
    def Calc_Grouped_E(self):
        Gr_E = np.zeros((self.Node_cnt*2, self.Node_cnt*2))
        for i in self.ElementGroup:
            elm_g = i.Generate_Elm_G(self.Node_cnt)
            Gr_E = Gr_E + np.dot(elm_g.T,np.dot(i.Element_E,elm_g))
        return Gr_E



if __name__ == '__main__':
    Nd = FemNodes.Fem_Nodes()
    Nd.Add_Fem_Nodes_With_Number([ [0,0,0],[3,0,0],[0,4,0],[2,8,0] ],[ 0,1,2,3 ])
    Fe = FemElement.Triangle3Node([0,1,2],Nd,{'E':2e11,'t':1,'v':0.2})
    #print(Fe.Element_E)
    a = Solver_Static(Nd,[Fe])
    print(a.Groupe_E)
    a.Displacement(0,[0,''])
    print('------------------')
    print(a.Groupe_E)
    