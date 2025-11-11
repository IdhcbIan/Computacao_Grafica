"""
Pyramid shape module for 3D rendering

A pyramid has 5 faces: 1 square base and 4 triangular sides
"""
from OpenGL.GL import *

def draw_pyramid(material_colors, material_name='orange'):
    """Draw a pyramid with the specified material"""
    material = material_colors.get(material_name, material_colors['orange'])
    glMaterialfv(GL_FRONT, GL_AMBIENT, material['ambient'])
    glMaterialfv(GL_FRONT, GL_DIFFUSE, material['diffuse'])
    glMaterialfv(GL_FRONT, GL_SPECULAR, material['specular'])
    glMaterialf(GL_FRONT, GL_SHININESS, material['shininess'])

    # Pyramid vertices
    apex = [0, 1.5, 0]  # Top point
    base = [
        [-1, -1, 1],   # Front left
        [1, -1, 1],    # Front right
        [1, -1, -1],   # Back right
        [-1, -1, -1]   # Back left
    ]

    # Draw base (square)
    glBegin(GL_QUADS)
    glNormal3f(0, -1, 0)  # Normal pointing down
    for vertex in reversed(base):  # Reversed for correct winding
        glVertex3fv(vertex)
    glEnd()

    # Draw triangular faces
    glBegin(GL_TRIANGLES)

    # Front face
    glNormal3f(0, 0.5, 1)
    glVertex3fv(apex)
    glVertex3fv(base[0])
    glVertex3fv(base[1])

    # Right face
    glNormal3f(1, 0.5, 0)
    glVertex3fv(apex)
    glVertex3fv(base[1])
    glVertex3fv(base[2])

    # Back face
    glNormal3f(0, 0.5, -1)
    glVertex3fv(apex)
    glVertex3fv(base[2])
    glVertex3fv(base[3])

    # Left face
    glNormal3f(-1, 0.5, 0)
    glVertex3fv(apex)
    glVertex3fv(base[3])
    glVertex3fv(base[0])

    glEnd()

def get_name():
    """Return the display name of this shape"""
    return "Pyramid"
