import os, time
import numpy as np
from ctypes import CDLL ,c_double, c_int

def Doolittle_solver(mat_A,mat_B):
    path = os.path.join(os.getcwd(),'src\\dolt.dll')
    dll = CDLL(path)
    dim = int(len(mat_B))
    a = (c_double*dim*dim)()

    for i in range(dim):
        for j in range(dim):
            a[i][j] = mat_A[i][j]
    b = (c_double*dim)()
    for i in range(dim):
        b [i] = mat_B[i]

    ans = (c_double*dim)()
    dim_ = (c_int)
    dim_ = dim

    #print([i[0] for i in a],[i[1] for i in a])
    dll.set_dim(dim_)
    dll.doolittle_solver(a,b,ans,dim_)
    #print([i for i in ans])
    anser = np.zeros((dim,1))
    for i in range(dim):
        anser[i][0] = ans[i]
    return anser