"""
Sphere shape module for 3D rendering
"""
from OpenGL.GL import *
from OpenGL.GLU import *

def draw_sphere(material_colors, material_name='orange'):
    """Draw a sphere with the specified material"""
    quadric = gluNewQuadric()
    gluQuadricNormals(quadric, GLU_SMOOTH)
    
    material = material_colors.get(material_name, material_colors['orange'])
    glMaterialfv(GL_FRONT, GL_AMBIENT, material['ambient'])
    glMaterialfv(GL_FRONT, GL_DIFFUSE, material['diffuse'])
    glMaterialfv(GL_FRONT, GL_SPECULAR, material['specular'])
    glMaterialf(GL_FRONT, GL_SHININESS, material['shininess'])
    
    gluSphere(quadric, 1, 32, 32)
    gluDeleteQuadric(quadric)

def get_name():
    """Return the display name of this shape"""
    return "Sphere"

