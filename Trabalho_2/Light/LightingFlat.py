"""
Flat Shading Implementation

In OpenGL: GL_FLAT shading model
"""
from OpenGL.GL import *

def enable():
    """
    Ativate flat (faceted) shader
    """

    glUseProgram(0)

    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)

    glShadeModel(GL_FLAT)     # Configurar para flat shading

def get_name():
    return "Flat"

def get_description():
    return "One color per polygon face - faceted appearance"
