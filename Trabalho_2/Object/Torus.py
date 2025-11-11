"""
Torus (donut) shape!!
"""
from OpenGL.GL import *
from OpenGL.GLUT import *
import math

def draw_torus(material_colors, material_name='orange'):
    """Draw a torus with the specified material"""
    material = material_colors.get(material_name, material_colors['orange'])
    glMaterialfv(GL_FRONT, GL_AMBIENT, material['ambient'])
    glMaterialfv(GL_FRONT, GL_DIFFUSE, material['diffuse'])
    glMaterialfv(GL_FRONT, GL_SPECULAR, material['specular'])
    glMaterialf(GL_FRONT, GL_SHININESS, material['shininess'])
    
    # Parameters
    inner_radius = 0.4
    outer_radius = 1.0
    sides = 32
    rings = 32
    
    # Draw torus!!
    for i in range(rings):
        glBegin(GL_QUAD_STRIP)
        for j in range(sides + 1):
            for k in range(2):
                s = (i + k) % rings + 0.5
                t = j % sides
                
                # Calculate angles
                theta = s * 2.0 * math.pi / rings
                phi = t * 2.0 * math.pi / sides
                
                # Calculate vertex position
                x = (outer_radius + inner_radius * math.cos(phi)) * math.cos(theta)
                y = (outer_radius + inner_radius * math.cos(phi)) * math.sin(theta)
                z = inner_radius * math.sin(phi)
                
                # Calculate normal
                nx = math.cos(phi) * math.cos(theta)
                ny = math.cos(phi) * math.sin(theta)
                nz = math.sin(phi)
                
                glNormal3f(nx, ny, nz)
                glVertex3f(x, y, z)
        glEnd()

def get_name():
    return "Torus"

