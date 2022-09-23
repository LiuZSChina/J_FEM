import matplotlib.pyplot as plt

class Fem_Nodes():
    def __init__(self):
        self.Fem_Nodes_List = []
        self.Fem_Nodes_Dic = {}
        self.Fem_Nodes_count = 0
    
    def Add_Fem_Nodes(self, New_Node_List):
        junk = [] #维度不对的就返回，不加入进去
        for i in New_Node_List:
            if len(i) != 3:
                junk.append(i)
            if i not in self.Fem_Nodes_List:
                self.Fem_Nodes_Dic[self.Fem_Nodes_count] = i
                self.Fem_Nodes_List.append(i)
                self.Fem_Nodes_count+=1
            else:
                junk.append(i)

        return junk

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

    def PrintFemNodes2d(self,size=10):
        plt.figure()
        for i in self.Fem_Nodes_List:
            plt.scatter(i[0], i[1], c='red', s=size, label='Nodes')
        plt.show()