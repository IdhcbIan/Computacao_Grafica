"""
Cube shape module for 3D rendering
"""
from OpenGL.GL import *

def draw_cube(material_colors, material_name='orange'):
    """Draw a cube with the specified material"""
    material = material_colors.get(material_name, material_colors['orange'])
    glMaterialfv(GL_FRONT, GL_AMBIENT, material['ambient'])
    glMaterialfv(GL_FRONT, GL_DIFFUSE, material['diffuse'])
    glMaterialfv(GL_FRONT, GL_SPECULAR, material['specular'])
    glMaterialf(GL_FRONT, GL_SHININESS, material['shininess'])
    
    # Define cube vertices
    vertices = [
        [-1, -1, -1], [1, -1, -1], [1, 1, -1], [-1, 1, -1],  
        [-1, -1, 1], [1, -1, 1], [1, 1, 1], [-1, 1, 1]       
    ]
    
    # Define faces (each face has 4 vertices for the CUBE!!)
    faces = [
        [0, 1, 2, 3],  # Back
        [4, 5, 6, 7],  # Front
        [0, 1, 5, 4],  # Bottom
        [2, 3, 7, 6],  # Top
        [0, 3, 7, 4],  # Left
        [1, 2, 6, 5]   # Right
    ]
    
    # Face normals (For direction!!)
    normals = [
        [0, 0, -1],   # Back
        [0, 0, 1],    # Front
        [0, -1, 0],   # Bottom
        [0, 1, 0],    # Top
        [-1, 0, 0],   # Left
        [1, 0, 0]     # Right
    ]
    
    glBegin(GL_QUADS)
    for i, face in enumerate(faces):
        glNormal3fv(normals[i])
        for vertex_idx in face:
            glVertex3fv(vertices[vertex_idx])
    glEnd()

def get_name():
    return "Cube"

