import src.FemNodes
import src.FemElement
import numpy as np

Nd = src.FemNodes.Fem_Nodes()
print(Nd.Add_Fem_Nodes([[0,0,0],[1,0,0],[1,1,0],[2,1,0]]))
print(Nd.Add_Fem_Nodes([[0,0,0],[2,1,0],[1,0,0],[1,1,0]]))
#Nd.PrintFemNodes2d()
#Fl1 = src.FemElement.Triangle3Node([0,1,2],Nd,{},[])
Fl2 = src.FemElement.Triangle3Node([0,1,2],Nd,{},[])
print(Fl2.Generate_Elm_E({'E':100,'t':1,'v':0.3}))
print(Fl2.Get_abc())

print(Nd.GetFemNodesAll())
#Fl1.Draw_Elm()
Fl2.Draw_Elm()

a = np.array([[1,2],[3,4]])
print(a)
a[0][1] = 9
print(a)