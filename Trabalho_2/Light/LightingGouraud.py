"""
Gouraud Shading Implementation

Gouraud shading calculates lighting at each vertex, then interpolates
the colors across the face.

How it works:
- Lighting calculations happen at vertices
- Colors are interpolated linearly across polygons
- Smoother appearance than flat shading
- Specular highlights can be missed if they don't hit vertices

In OpenGL: GL_SMOOTH shading model (default)
Named after Henri Gouraud who proposed it in 1971
"""
from OpenGL.GL import *

def enable():
    """
    Ativa o modo de sombreamento Gouraud (suave)

    Importante: Reativa o pipeline fixo do OpenGL caso shaders estejam ativos
    """
    # Desativar qualquer shader que possa estar ativo
    glUseProgram(0)

    # Garantir que o lighting está habilitado (pode ter sido desabilitado por shaders)
    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)

    # Configurar para smooth shading (Gouraud)
    glShadeModel(GL_SMOOTH)

def get_name():
    """Return the display name of this lighting model"""
    return "Gouraud"

def get_description():
    """Return a description of this lighting model"""
    return "Lighting at vertices, interpolated across faces"
