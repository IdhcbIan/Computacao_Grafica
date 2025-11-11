"""
Object package - 3D Shape modules

Contains all geometric shape implementations:
- Sphere: Smooth sphere using GLU quadrics
- Cube: Box with 6 faces and proper normals
- Torus: Donut shape with parametric surface
- Pyramid: Square base with 4 triangular sides
"""

from . import Sphere
from . import Cube
from . import Torus
from . import Pyramid

__all__ = ['Sphere', 'Cube', 'Torus', 'Pyramid']
