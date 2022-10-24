from re import S
from sys import maxsize
from scipy.spatial import Delaunay
import numpy as np
import matplotlib.pyplot as plt
import math

# 计算三角形的面积
def Calc_Tri_2D_Size(Node_Pos:list):
    A = np.array([ [Node_Pos[0][0], Node_Pos[0][1], 1],
                   [Node_Pos[1][0], Node_Pos[1][1], 1], 
                   [Node_Pos[2][0], Node_Pos[2][1], 1]])
    aera = np.linalg.det(A)/2
    return abs(aera)

# 获得三角形的形心坐标
def Calc_Tri_2D_Weight_Center(Node_Pos:list) ->list:
    xc = sum([i[0] for i in Node_Pos])/3
    yc = sum([i[1] for i in Node_Pos])/3
    return [xc,yc]

# 获得三角形的形状比例（最长边比最短边）返回 [比例, 最长start，最长end]
def Calc_Tri_2D_Shape_Rate(Node_Pos:list) ->list:
    max_line = [Node_Pos[0],Node_Pos[1]]
    max_length = (Node_Pos[0][0]-Node_Pos[1][0])**2 + (Node_Pos[0][1]-Node_Pos[1][1])**2
    min_line = [Node_Pos[0],Node_Pos[1]]
    min_length = max_length
    for i in range(1,3):
        length = (Node_Pos[i][0]-Node_Pos[(i+1)%3][0])**2 + (Node_Pos[i][1]-Node_Pos[(i+1)%3][1])**2 
        if length > max_length:
            max_length = length
            max_line = [Node_Pos[i],Node_Pos[(i+1)%3]]
        elif length < min_length:
            min_length = length
            min_line = [Node_Pos[i],Node_Pos[(i+1)%3]]
    rate = math.sqrt(max_length/min_length)
    return [rate] + list(max_line)

# 获得边上的某个点的中点，注意此处可能是曲面等 [start, end]  curve：[[圆心], 半径, [顺时针/deg--起始弧度，终止弧度；（-1）表示一整圈]]
def Edge_Center_2D(Node_Pos:list, curve:list = [])->list:
    #没有任何的曲边
    if curve == []:
        #print(Node_Pos)
        return [(Node_Pos[0][0] + Node_Pos[1][0])/2 , (Node_Pos[0][1] + Node_Pos[1][1])/2]

    return []


# 划分平面三角形网格
def Mesher_Tri_2D(Node_cloud:np.ndarray, max_volume:float = 0, max_shape_rate:float = 0, max_refine = 10,refine:bool = True) ->list[np.ndarray]:
    print("=======Shape Must Be Convex=======")
    Meshes = Delaunay(Node_cloud).simplices
    ifgo = True
    
    cnt = 0
    # 迭代进行优化
    if max_shape_rate <2.5 and refine:
        print("=======Shape Rate too Small May Cause Problems=======")
    while ifgo and refine and cnt < max_refine:
        cnt+=1
        ifgo = False
        Meshes = Delaunay(Node_cloud).simplices
        for i in Meshes:
            Node_Pos = [list(Node_cloud[i[0]]),list(Node_cloud[i[1]]),list(Node_cloud[i[2]])]

            sp = Calc_Tri_2D_Shape_Rate(list(Node_Pos))
            rate = sp[0]
            long_edge = [sp[1], sp[2]]
            if max_shape_rate> 1.01 and rate > max_shape_rate:
                ifgo = True
                center = Edge_Center_2D(long_edge)
                #print(center)
                Node_cloud = np.append(Node_cloud,[center],axis=0)
                #continue
            
            Mesh_Size = Calc_Tri_2D_Size(Node_Pos)
            if max_volume>0 and Mesh_Size>max_volume:
                ifgo = True
                wc = Calc_Tri_2D_Weight_Center(Node_Pos)
                Node_cloud = np.append(Node_cloud,[wc],axis=0)
                #print(Mesh_Size)
            
    Meshes = Delaunay(Node_cloud).simplices
    if cnt == max_refine and ifgo:
        print("=======Max Refine Times Reached But Not Finished=======")

    return [Node_cloud, Meshes]

if __name__ == '__main__':
    points = np.array([[0,0],[0.5,0],[1,0],[1.5,0],[2,0],[1.75,0.25],[1.5,0.5],[1.25,0.75],[1,1],[0.75,1],[0.5,1],[0.25,1],[0,1],[0,0.75],[0,0.5],[0,0.25]])
    points, Mesh = Mesher_Tri_2D(points, max_volume=0.04, max_shape_rate=2.5, refine=True)
    #print(points)
    #print(Mesh)
    plt.figure(figsize=(10, 5)) 
    plt.triplot(points[:, 0], points[:, 1], Mesh.copy()) 
    plt.tick_params(labelbottom='off', labelleft='off', left='off', right='off', bottom='off', top='off') 
    ax = plt.gca() 
    plt.scatter(points[:,0],points[:,1], color='r')
    #plt.grid()
    plt.axis('equal')
    plt.show()

