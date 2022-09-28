from textwrap import indent
import matplotlib.pyplot as plt

class Fem_Nodes():
    def __init__(self):
        self.Fem_Nodes_List = []
        self.Fem_Nodes_Dic = {} # {'number':[x,y,z]}
        self.Fem_Nodes_count = 0
    
    def Add_Fem_Nodes_With_Number(self, New_Node_List,Node_pos):
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

    def GetFemNodes(self,key):
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
            plt.scatter(self.Fem_Nodes_Dic[k][0],self.Fem_Nodes_Dic[k][1], c='red', s=Size[0], label='Nodes')
        plt.show()