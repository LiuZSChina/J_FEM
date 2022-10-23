import pyvista

class Rect_2D():
    def __init__(self, Nodes:list) -> None:
        if len(Nodes) != 4:
            self.Nodes = []
            return
        self.Nodes = Nodes
    def draw(self):
        rect = pyvista.Rectangle([i for i in self.Nodes])
        return rect

class Model_2D():
    def __init__(self) -> None:
        self.geometray = []
        self.geo_bool = []
    
    def draw_model(self, show_edge= True, line_width = 5):
        p = pyvista.Plotter(window_size=[1000, 1000])
        for i in self.geometray:
            shape = i.draw()
            p.add_mesh(shape, color='silver', specular=1.0, specular_power=10, show_edges=show_edge, line_width=line_width)
        #p.enable_shadows()
        p.show()

    def add_rec(self, rect_nodes:list) -> bool:
        rect = Rect_2D(rect_nodes)
        if rect != []:
            self.geometray.append(rect)
            return True
        return False


if __name__ == "__main__":
    md = Model_2D()
    md.add_rec([[0,0,0], [1,0,0], [1,1,0], [0,1,0]]) 
    md.add_rec([[1,0,0], [2,0,0], [2,1,0], [1,1,0]]) 
    md.draw_model()