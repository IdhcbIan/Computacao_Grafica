"""
Gouraud Shading Implementation

Gouraud shading calculates lighting at each vertex, then interpolates
the colors across the face.

In OpenGL: GL_SMOOTH shading model
"""
from OpenGL.GL import *

def enable():
    """
    Ativate defaut OpenGL Gouraud (smooth)
    """
    glUseProgram(0)

    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)

    glShadeModel(GL_SMOOTH)   # Use internal OpenGL Implementation

def get_name():
    return "Gouraud"

def get_description():
    return "Lighting at vertices, interpolated across faces"
