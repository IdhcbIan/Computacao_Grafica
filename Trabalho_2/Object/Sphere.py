"""
Sphere shape module for 3D rendering

Use internal OpenGL Functoion!! diferent from vertice like code for polygons!!
"""
from OpenGL.GL import *
from OpenGL.GLU import *

def draw_sphere(material_colors, material_name='orange'):
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
    return "Sphere"

