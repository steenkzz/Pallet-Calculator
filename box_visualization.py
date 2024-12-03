import numpy as np
import pyqtgraph.opengl as gl

def create_box_mesh(x, y, z, length, width, height):
    verts = np.array([
        [0, 0, 0],
        [length, 0, 0],
        [length, width, 0],
        [0, width, 0],
        [0, 0, height],
        [length, 0, height],
        [length, width, height],
        [0, width, height]
    ])
    faces = np.array([
        [0, 1, 2], [0, 2, 3],
        [4, 5, 6], [4, 6, 7],
        [0, 1, 5], [0, 5, 4],
        [1, 2, 6], [1, 6, 5],
        [2, 3, 7], [2, 7, 6],
        [3, 0, 4], [3, 4, 7]
    ])
    # Remove diagonal edges
    faces = faces[[0, 1, 2, 3, 4, 5, 8, 9, 10, 11]]
    colors = np.array([[1.0, 0.89, 0.24, 1.0]] * len(faces))  # Color FFE33C
    mesh = gl.GLMeshItem(vertexes=verts, faces=faces, faceColors=colors, drawEdges=True, edgeColor=(0.84, 0.47, 0.0, 1.0))  # Edge color D77900
    mesh.translate(x, y, z)
    return mesh