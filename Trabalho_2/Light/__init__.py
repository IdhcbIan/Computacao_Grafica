"""
Light package - Lighting/Shading model implementations

Contains all lighting model implementations:
- LightingFlat: Flat shading (GL_FLAT) - one color per polygon
- LightingGouraud: Gouraud shading (GL_SMOOTH) - lighting at vertices
- LightingPhong: Phong shading - per-fragment lighting with GLSL shaders
"""

from . import LightingFlat
from . import LightingGouraud
from . import LightingPhong

__all__ = ['LightingFlat', 'LightingGouraud', 'LightingPhong']
