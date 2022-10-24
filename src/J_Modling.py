from fileinput import lineno
import numpy as np
import matplotlib.pyplot as plt


class Model_2D():
    def __init__(self) -> None:
        #geometray_list = [ ['l', [start x,start y],[end], split], ['r', [center, r],[start_rad, end_rad], split]... ]
        self.geometray_list = []
        self.geometray_dict = {}
    
    #绘制当前所有的元素
    def draw_model(self, show_edge:bool = True, dSize:list[int] = [5,10]):
        fig,ax =plt.subplots()
        print(self.geometray_dict)
        for j in self.geometray_dict:
            i = self.geometray_dict[j]
            if i[0] == 'l':
                x = [i[1][0], i[2][0] ]
                y = [i[1][1], i[2][1] ]
                ax.plot(x,y, c = 'steelblue')
                ax.text(sum(x)/2,sum(y)/2,s = str(j), c = 'coral',ha='center',va='bottom',fontsize=dSize[1])
                ax.plot(i[1][0], i[1][1], marker = 'o',ls = "", c='r', ms = dSize[0])
                ax.plot(i[2][0], i[2][1], marker = 'o',ls = "", c='r', ms = dSize[0])
        #p.enable_shadows()
        plt.axis('equal')
        plt.show()

    # 绘制一条线，提供编号
    def add_line_with_number(self, line_nodes:list, number:int, split:int = -1) -> bool:
        lin = ['l', line_nodes[0], line_nodes[1], split]
        self.geometray_list.append(lin)
        self.geometray_dict[number] = lin
        return True

    # 绘制一条线，自动为其编号
    def add_line_auto_number(self, line_nodes:list, split:int = -1) -> bool:
        number = len(self.geometray_list)
        while number in self.geometray_dict:
            number += 1
        lin = ['l', line_nodes[0], line_nodes[1], split]
        self.geometray_list.append(lin)
        self.geometray_dict[number] = lin
        return True
    
    #分解边
    def split_edge_by_number(self, edge_number):
        edge = self.geometray_dict[edge_number]
        edge_type = edge[0]
        sp_cnt = edge[3]
        nd = []
        if edge_type == 'l':
            direc = [(edge[2][0]-edge[1][0])/float(sp_cnt), (edge[2][1]-edge[1][1])/float(sp_cnt)]
            for i in range(sp_cnt+1):
                nd.append([edge[1][0]+i*direc[0], edge[1][1]+i*direc[1]])
        return nd
            
            
    #返回将边分解后的点坐标
    def get_init_nd(self,split_lines = True)->list:
        if split_lines:
            nd = []
            for i in self.geometray_dict:
                edge_nd = self.split_edge_by_number(i)
                for j in edge_nd:
                    if j not in nd:
                        nd.append(j)

            return nd
        return []

    def add_rec(self, rect_nodes:list) -> bool:
        return False


if __name__ == "__main__":
    md = Model_2D()
    md.add_line_auto_number([[1,1,0], [0,0,0]], split=10) 
    md.add_line_auto_number([[0,0,0], [1,0,0]], split=5) 
    md.add_line_auto_number([[1,0,0], [1,1,0]], split=5) 
    print(md.get_init_nd())
    #md.add_rec([[1,0,0], [2,0,0], [2,1,0], [1,1,0]]) 
    md.draw_model()