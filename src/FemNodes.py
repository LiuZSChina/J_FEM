from sys import maxsize
from telnetlib import NOP
from tkinter.messagebox import NO
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

class Fem_Nodes():
    def __init__(self):
        self.Fem_Nodes_List = []
        self.Fem_Nodes_Dic = {} # {number<int>:[x,y,z]}
        #self.Fem_Nodes_Dof = {} # {number<int>:Dof:int} 3->xyz; 6-xyz + theta xyz;
        self.Fem_Node_Elm = {} # {number<int>:[Elms]<list>} Elm have this Node
        #self.Fem_Nodes_Surface = {} # {'number':[x,y,z]}
        self.Fem_Nodes_count = 0
    
    def Set_Node_in_Elm(self,Elm_num:int, Node_num:list):
        for nd in Node_num:
            self.Fem_Node_Elm[nd].append(Elm_num)

    def Add_one_Node(self, Node_number:int, Node_Cord:list):
        index = -1
        if_new_number = False
        #新节点
        if Node_Cord not in self.Fem_Nodes_List: 
            # 新编号
            if Node_number not in self.Fem_Nodes_Dic:
                self.Fem_Nodes_Dic[Node_number] = Node_Cord
                self.Fem_Nodes_List.append(Node_Cord)
                index = Node_number
                self.Fem_Nodes_count+=1
                self.Fem_Node_Elm[Node_number] = []
                if_new_number = True
            #编号存在，覆盖原有节点
            else:
                self.Fem_Nodes_List.remove(self.Fem_Nodes_Dic[Node_number])
                self.Fem_Nodes_Dic[Node_number] = Node_Cord
                self.Fem_Nodes_List.append(Node_Cord)
                index = Node_number
            
        #已有节点
        else:
            #找到节点编号
            for key in self.Fem_Nodes_Dic:
                if self.Fem_Nodes_Dic[key] == Node_Cord:
                    index = key
                    if_new_number = False
                    break
        return index , if_new_number

    def Add_Fem_Nodes_With_Number(self, New_Node_List, Node_pos):
        junk = [] #维度不对的就返回，不加入进去
        index = []
        #逐个加入
        for i in range(len(New_Node_List)):
            Node_Cord = New_Node_List[i]
            Node_number = Node_pos[i]
            if len(Node_Cord) != 3:
                junk.append(Node_Cord)

            ind, new_num = self.Add_one_Node(Node_number, Node_Cord)
            index.append(ind)
            """#新节点
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
            """

        return index

    def Add_Fem_Nodes_With_Start_Number_Step(self, start, step, number, start_number):
        print('---Adding Nodes [%s : %s] ---'%(int(start_number),int(start_number+number-1)))
        index = []
        for i in range(int(number)):
            x = start[0] + i*step[0]
            y = start[1] + i*step[1]
            z = start[2] + i*step[2]
            key, new_num = self.Add_one_Node(start_number+i,[x, y, z])
            """self.Fem_Nodes_Dic[start_number+i] = [x, y, z]
            self.Fem_Nodes_List.append([x, y, z])"""
            index.append(key)
            #self.Fem_Nodes_count+=1

    def Add_Fem_Nodes_Auto_Number(self, Node_pos)->list:
        i = self.Fem_Nodes_count
        while i in self.Fem_Nodes_Dic:
            i += 1
        pos = [] #加入后的编号
        for nd in range(len(Node_pos)):
            key, new_num = self.Add_one_Node(i,Node_pos[nd])
            pos.append(key)
            if new_num:
                i += 1
            """if Node_pos[nd] not in self.Fem_Nodes_List:
                pos.append(i)
                self.Fem_Nodes_Dic[i] = Node_pos[nd]
                self.Fem_Nodes_List.append(Node_pos[nd])
                self.Fem_Nodes_count += 1
                i += 1
            else:
                for key in self.Fem_Nodes_Dic:
                    if self.Fem_Nodes_Dic[key] == Node_pos[nd]:
                        pos.append(key)
                        break"""
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
        plt.ion()
        print('Plotting Nodes')
        for k in self.Fem_Nodes_Dic:
            plt.text(self.Fem_Nodes_Dic[k][0],self.Fem_Nodes_Dic[k][1],k,ha='center',va='bottom',fontsize=Size[1])
            plt.plot(self.Fem_Nodes_Dic[k][0],self.Fem_Nodes_Dic[k][1], c='red', marker='o',ls="")
        plt.axis('equal')
        plt.show()
        #plt.close()

    #寻找某条线上的节点 Line:[start:[x,y,z], end:[x,y,z]]
    def Find_Nodes_on_Line(self, Line:list)->list:
        nd_list = []
        direction = [Line[1][0]-Line[0][0], Line[1][1]-Line[0][1] ,Line[1][2]-Line[0][2]]
        print("_________________________________________UNFINISHED(Find_Nodes_on_Line)______________________________________________")
        return nd_list

    #寻找某个坐标的节点 [x,y,z]
    def Find_Nodes_by_Coord(self, Pos:list)->list:
        for i in self.Fem_Nodes_Dic:
            xyz = self.Fem_Nodes_Dic[i]
            if xyz[0] != Pos[0]:
                continue
            elif xyz[1] != Pos[1]:
                continue
            if len(Pos) == 2:
                return i
            elif xyz[2] != Pos[2]:
                continue
            return i
            
        return []

    #寻找坐标范围内的节点 cord_range:{'x\y\z':[start,end]} eg{'y':[0,0]}
    def Find_Nodes_Cord_Range(self, cord_range:dict)->list:
        """ # 给定节点满足的x、y、z条件 eg->(x==..)
            返回满足的所有节点编号"""
        nd_list = []
        c_range_list = [None, None, None]
        for key in cord_range:
            if key == 'x':
                c_range_list[0] = cord_range[key]

            elif key == 'y':
                c_range_list[1] = cord_range[key]
                    
            elif key == 'z':
                c_range_list[2] = cord_range[key]
        #print(c_range_list)
        for i in self.Fem_Nodes_Dic:
            xyz = self.Fem_Nodes_Dic[i]
            xr = c_range_list[0]
            yr = c_range_list[1]
            zr = c_range_list[2]
            if xr != None:
                if len(xr) == 1:
                    if xyz[0] != xr[0]:
                        continue
                else:
                    if xyz[0] < xr[0] or xyz[0] > xr[1]:
                        continue

            if yr != None:
                if len(yr) == 1:
                    if xyz[1] != yr[0]:
                        continue
                else:
                    if xyz[1] < yr[0] or xyz[1] > yr[1]:
                        #print(xyz[1])
                        continue

            if zr != None:
                if len(zr) == 1:
                    if xyz[2] != zr[0]:
                        continue
                else:
                    if xyz[2] < zr[0] or xyz[2] > zr[1]:
                        continue
            
            nd_list.append(i)

        return nd_list
    
    #找到在 Ax+By+Cz+D = 0 上的节点
    def Find_Nodes_Surface(self, abcd:list, cord_range:dict = {},dif=1e-12)->list:
        ans = []
        for i in self.Fem_Nodes_Dic:
            xyz = self.Fem_Nodes_Dic[i]
            if cord_range != {} and 'x' in cord_range and (xyz[0]<cord_range['x'][0] or xyz[0]>cord_range['x'][1]):
                continue
            if cord_range != {} and 'y' in cord_range and (xyz[1]<cord_range['y'][0] or xyz[1]>cord_range['y'][1]):
                continue
            if cord_range != {} and 'z' in cord_range and (xyz[2]<cord_range['z'][0] or xyz[2]>cord_range['z'][1]):
                continue
            
            if abs(xyz[0]*abcd[0] + xyz[1]*abcd[1] +xyz[2]*abcd[2] + abcd[3]) < dif:
                ans.append(i)
        return ans
    
    #找到在 z方向的圆柱上的节点
    def Find_Nodes_Cylinder_Z(self, center:list, r:float, dif=1e-7)->list:
        ans = []
        for i in self.Fem_Nodes_Dic:
            xyz = self.Fem_Nodes_Dic[i]
            if xyz[0] < center[0]-r or xyz[0] > center[0]+r:
                continue
            if xyz[1] < center[1]-r or xyz[1] > center[1]+r:
                continue
            if abs((xyz[0]-center[0])**2 + (xyz[1]-center[1])**2 - r**2) <dif:
                ans.append(i)
        return ans

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