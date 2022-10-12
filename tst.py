
verts = [(0, 0, 0), (0, 1, 0), (1, 1, 0), (1, 0, 0), (0.5, 0.5, 0.707)]
# 面
faces = [[0, 1, 4], [1, 2, 4], [2, 3, 4], [0, 3, 4], [0, 1, 2, 3]]
 
# 每个面对应的点坐标
poly3d = [[verts[vert_id] for vert_id in face] for face in faces]
print (poly3d)