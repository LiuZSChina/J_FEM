from tkinter.messagebox import NO
import matplotlib.patches as mpatch
import matplotlib.pyplot as plt

class Triangle3Node():
    # Nodes-->[i,j,m]结点编号  MaterialProp {'E':弹性模量Mpa,'v':泊松比,'t':厚度mm，} G_mat 转换矩阵
    def __init__(self,Nodes_number,Nodes_class,MaterialProp,G_mat) -> None:
        Nodes = Nodes_class.GetFemNodes(Nodes_number)
        if len(Nodes)!=3:
            return
        for i in Nodes:
            if len(i)!=3:
                return

        self.Nd_i_j_m = [Nodes[0],Nodes[1],Nodes[2]]

        return

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
