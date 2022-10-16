from sys import maxsize
from telnetlib import NOP
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

class Fem_Nodes():
    def __init__(self):
        self.Fem_Nodes_List = []
        self.Fem_Nodes_Dic = {} # {'number':[x,y,z]}
        self.Fem_Nodes_count = 0
    
    def Add_Fem_Nodes_With_Number(self, New_Node_List, Node_pos):
        junk = [] #维度不对的就返回，不加入进去
        index = []
        #逐个加入
        for i  in range(len(New_Node_List)):
            Node_Cord = New_Node_List[i]
            Node_number = Node_pos[i]
            if len(Node_Cord) != 3:
                junk.append(Node_Cord)

            #新节点
            if Node_Cord not in self.Fem_Nodes_List: 
                # 新编号
                if Node_number not in self.Fem_Nodes_Dic:
                    self.Fem_Nodes_Dic[Node_number] = Node_Cord
                    self.Fem_Nodes_List.append(Node_Cord)
                    index.append(Node_number)
                    self.Fem_Nodes_count+=1
                #编号存在，覆盖原有节点
                else:
                    self.Fem_Nodes_List.remove(self.Fem_Nodes_Dic[Node_number])
                    self.Fem_Nodes_Dic[Node_number] = Node_Cord
                    self.Fem_Nodes_List.append(Node_Cord)
                    index.append(Node_number)
            
            #已有节点
            else:

                #找到节点编号
                for key in self.Fem_Nodes_Dic:
                    if self.Fem_Nodes_Dic[key] == Node_Cord:
                        index.append(key)
                        break
                
                junk.append(Node_Cord)

        return index,junk

    def Add_Fem_Nodes_With_Start_Number_Step(self, start, step, number, start_number):
        print('---Adding Nodes [%s : %s] ---'%(int(start_number),int(start_number+number-1)))
        index = []
        for i in range(int(number)):
            x = start[0] + i*step[0]
            y = start[1] + i*step[1]
            z = start[2] + i*step[2]
            self.Fem_Nodes_Dic[start_number+i] = [x, y, z]
            self.Fem_Nodes_List.append([x, y, z])
            index.append(start_number+i)
            self.Fem_Nodes_count+=1

    def Add_Fem_Nodes_Auto_Number(self, Node_pos)->list:
        i = self.Fem_Nodes_count
        while i in self.Fem_Nodes_Dic:
            i += 1
        pos = []
        for nd in range(len(Node_pos)):
            if Node_pos[nd] not in self.Fem_Nodes_List:
                pos.append(i)
                self.Fem_Nodes_Dic[i] = Node_pos[nd]
                self.Fem_Nodes_List.append(Node_pos[nd])
                self.Fem_Nodes_count += 1
                i += 1
            else:
                for key in self.Fem_Nodes_Dic:
                    if self.Fem_Nodes_Dic[key] == Node_pos[nd]:
                        pos.append(key)
                        break
        return pos

    def GetFemNodes(self,key:list)->list:
        nd = []
        for i in key:
            if i in self.Fem_Nodes_Dic:
                 nd.append(self.Fem_Nodes_Dic[int(i)]) 
        return nd

    def GetFemNodesAll(self):
        return self.Fem_Nodes_Dic,self.Fem_Nodes_count

    def GetFemNodesCount(self):
        return self.Fem_Nodes_count

    def PrintFemNodes2d(self,Size=[10,20]):
        plt.figure()
        print('Plotting Nodes')
        for k in self.Fem_Nodes_Dic:
            plt.text(self.Fem_Nodes_Dic[k][0],self.Fem_Nodes_Dic[k][1],k,ha='center',va='bottom',fontsize=Size[1])
            plt.plot(self.Fem_Nodes_Dic[k][0],self.Fem_Nodes_Dic[k][1], c='red', marker='o',ls="")
        plt.show()

    #三维模式下绘图 Nodes = [] 绘制所有
    def PrintFemNodes3d(self, Nodes:list, psize=[10,5], scale = [1e-2,1e-2,1e-2]):   
        fig = plt.figure()
        ax = fig.add_subplot(111, projection='3d')

        # find nodes for printing
        print_list = []
        #ax.set_aspect('auto', adjustable=None, anchor=None, share=False)
        if Nodes == []:
            print_list = self.Fem_Nodes_List
        else:
            for i in Nodes:
                print_list.append(self.Fem_Nodes_Dic[i])

        # Change the axis aspect to fit
        x_bound = [min([i[0] for i in print_list]),max([i[0] for i in print_list])]
        y_bound = [min([i[1] for i in print_list]),max([i[1] for i in print_list])]
        z_bound = [min([i[2] for i in print_list]),max([i[2] for i in print_list])]   
        max_size = max([x_bound[1]-x_bound[0], y_bound[1]-y_bound[0], y_bound[1]-y_bound[0]])
        ax.set_xlim([(sum(x_bound)/2) - max_size/2 , (sum(x_bound)/2) + max_size/2])  # type: ignore
        ax.set_ylim([(sum(y_bound)/2) - max_size/2 , (sum(y_bound)/2) + max_size/2])  # type: ignore
        ax.set_zlim([(sum(z_bound)/2) - max_size/2 , (sum(z_bound)/2) + max_size/2])  # type: ignore

        #Printing nodes
        for k in range(len(print_list)):
            i = print_list[k]
            ax.text(i[0], i[1], i[2],c = 'k',ha='center',va='bottom',s=k, fontsize=psize[0])  # type: ignore
            ax.plot(i[0], i[1], i[2],c='red', marker='.',ls="",ms=psize[1])
        
        plt.show()