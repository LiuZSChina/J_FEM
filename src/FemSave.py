import meshio


def FemSave(points:list, cells:dict, f_name:str, point_data:dict = {}, cell_data:dict = {}):
    """# Save points, cells and some data
    points = [
        [0.0, 0.0],
        [1.0, 0.0],
        [0.0, 1.0],
        [1.0, 1.0],
        [2.0, 0.0],
        [2.0, 1.0],
    ]
    cells = [
        ("triangle", [[0, 1, 2], [1, 3, 2]]),
        ("quad", [[1, 4, 5, 3]]),
    ]
    point_data={"T": [0.3, -1.2, 0.5, 0.7, 0.0, -3.0]},
    cell_data={"a": [[0.1, 0.2], [0.4]]},
    """
    if point_data!={}:
        for i in point_data:
            if len(point_data[i])!=len(points):
                print("Warning==>Point data does not match points list==Data will be discarded")

    if cell_data!={}:
        len_cell = []
        for i in cells:
            len_cell.append(len(cells[i]))
        
        k = 0
        for i in cell_data:#不同组数据
            d_len = []
            for j in cell_data[i]:
                d_len.append(len(j))
            if d_len != len_cell:
                cell_data = {}
                print("Warning==>Cell data does not match points list==Data will be discarded")
                break
            k += 1
    
    if point_data == {} and cell_data == {}:
        mesh = meshio.Mesh(
            points,
            cells
        )
    elif point_data == {} and cell_data != {}:
        mesh = meshio.Mesh(
            points,
            cells,
            # Each item in cell data must match the cells array
            cell_data = cell_data,
        )
    elif cell_data == {} and point_data != {}:
        mesh = meshio.Mesh(
            points,
            cells,
            # Each item in cell data must match the cells array
            point_data = point_data,
        )
    else:
        mesh = meshio.Mesh(
            points,
            cells,
            # Optionally provide extra data on points, cells, etc.
            point_data=point_data,
            # Each item in cell data must match the cells array
            cell_data=cell_data,
        )

    mesh.write(
        f_name,  # str, os.PathLike, or buffer/open file
        file_format="vtk",  # optional if first argument is a path; inferred from extension
    )