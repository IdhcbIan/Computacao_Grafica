"""
Flat Shading Implementation

Flat shading calculates the lighting once per polygon face.
All pixels in a face receive the same color, creating a faceted appearance.

How it works:
- Uses the face normal (not vertex normals)
- Lighting calculation happens once per polygon
- No interpolation across the face
- Fast but less realistic

In OpenGL: GL_FLAT shading model
"""
from OpenGL.GL import *

def enable():
    """
    Ativa o modo de sombreamento flat (facetado)

    Importante: Reativa o pipeline fixo do OpenGL caso shaders estejam ativos
    """
    # Desativar qualquer shader que possa estar ativo
    glUseProgram(0)

    # Garantir que o lighting está habilitado (pode ter sido desabilitado por shaders)
    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)

    # Configurar para flat shading
    glShadeModel(GL_FLAT)

def get_name():
    """Return the display name of this lighting model"""
    return "Flat"

def get_description():
    """Return a description of this lighting model"""
    return "One color per polygon face - faceted appearance"
