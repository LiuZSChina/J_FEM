import src.FemNodes
import src.FemElement

Nd = src.FemNodes.Fem_Nodes()
Nd.Add_Fem_Nodes([[0,0,0],[1,0,0],[1,1,0],[2,1,0]])
print(Nd.GetFemNodesAll())
print(Nd.GetFemNodesCount())
#Nd.PrintFemNodes2d()
Fl1 = src.FemElement.Triangle3Node([0,1,2],Nd,{},[])
Fl2 = src.FemElement.Triangle3Node([0,2,3],Nd,{},[])
print(Nd.Add_Fem_Nodes([[0,0,0]]))
print(Nd.GetFemNodesAll())
Fl1.Draw_Elm()
Fl2.Draw_Elm()