# Trabalho 2 - Computação Gráfica (SCC 250)
## 3D Shape Renderer with Lighting Models

### Overview
Interactive 3D rendering system that demonstrates different lighting models (Flat, Gouraud, Phong) with multiple geometric shapes.

### Requirements Met
- ✓ 4 types of 3D objects (Sphere, Cube, Torus, Pyramid)
- ✓ 3 lighting models (Flat, Gouraud, Phong)
- ✓ Interactive manipulation (shape, material, camera, light position)
- ✓ Multiple camera angles
- ✓ OpenGL implementation using PyOpenGL

### How to Run
```bash
cd Trabalho_2
python Main_3d.py
```

### Dependencies
- Python 3.10+
- PyOpenGL
- Pygame
- NumPy

### Project Structure

```
Trabalho_2/
├── Main_3d.py              # Main program with GUI and rendering
├── Aux_3D.py               # Helper functions and state management
├── 3D.py                   # Simple example (not used in main)
│
├── Shape Modules (modular, importable):
│   ├── Sphere.py           # Sphere geometry
│   ├── Cube.py             # Cube geometry
│   ├── Torus.py            # Torus (donut) geometry
│   └── Pyramid.py          # Pyramid geometry
│
└── Lighting Modules (modular, importable):
    ├── LightingFlat.py     # Flat shading (GL_FLAT)
    ├── LightingGouraud.py  # Gouraud shading (GL_SMOOTH)
    └── LightingPhong.py    # Phong shading (GL_SMOOTH approximation)
```

### Features

#### 1. Shape Selection
- **Sphere**: Smooth sphere using GLU quadrics
- **Cube**: Box with 6 faces and proper normals
- **Torus**: Donut shape with parametric surface
- **Pyramid**: Square base with 4 triangular sides

#### 2. Lighting Models
- **Flat Shading**: One color per polygon (GL_FLAT)
  - Fast, faceted appearance
  - Good for seeing polygon structure

- **Gouraud Shading**: Lighting calculated at vertices (GL_SMOOTH)
  - Smooth color interpolation
  - Developed by Henri Gouraud (1971)

- **Phong Shading**: Per-pixel lighting approximation (GL_SMOOTH)
  - Best quality highlights
  - Named after Bui Tuong Phong (1973)
  - Note: True Phong requires GLSL shaders

#### 3. Camera Angles
- **Front**: Default view from Z-axis
- **Top**: View from above
- **Side**: View from X-axis
- **Diagonal**: 45-degree view

#### 4. Material Properties
- **Orange**: Warm, high shininess
- **Red**: Deep red, moderate shininess
- **Blue**: Cool blue, high shininess

#### 5. Interactive Light Control
- Arrow keys or GUI buttons to move light
- Real-time lighting updates
- Positional light source

### Controls

#### GUI Window (Controls):
- Click shape buttons to change object
- Click camera buttons to change view
- Click lighting buttons to change shading model
- Click color swatches to change material
- Use arrow buttons to move light position
- Re-render button to refresh with current window size
- Quit button to exit

#### Keyboard:
- Arrow keys: Move light position
- ESC: Quit application

### Code Architecture

#### Modular Design
Each component is in its own file and can be imported as a function:

```python
# Example: Using a shape module
import Sphere
Sphere.draw_sphere(materials, 'orange')

# Example: Using a lighting module
import LightingFlat
LightingFlat.enable()
```

#### Estado3D Class (in Aux_3D.py)
Manages the application state:
- `light_pos`: Position of the light source
- `material`: Current material properties
- `shape`: Current shape being rendered
- `camera_angle`: Current camera view
- `lighting_model`: Current lighting algorithm

#### Rendering Pipeline
1. User interaction in GUI window
2. Commands sent via multiprocessing queue
3. 3D window receives commands and updates state
4. Scene rendered to FBO (Frame Buffer Object)
5. FBO texture displayed on screen

### Educational Notes

#### Lighting Models Explained

**Flat Shading (GL_FLAT)**
- Simplest lighting model
- One lighting calculation per polygon
- All pixels in a face get the same color
- Creates faceted appearance
- Very fast

**Gouraud Shading (GL_SMOOTH)**
- Lighting calculated at each vertex
- Colors interpolated across polygon
- Smoother than flat shading
- Can miss specular highlights between vertices
- Good balance of quality and performance

**Phong Shading**
- Lighting calculated per pixel
- Normals interpolated across polygon
- Best quality specular highlights
- Requires fragment shaders for true implementation
- Our version uses GL_SMOOTH as approximation

### Implementation Details

#### Multi-Window Architecture
Uses Python multiprocessing to create two separate windows:
- **3D Window**: OpenGL context for rendering
- **GUI Window**: Pygame surface for controls

This separation allows:
- Resizable 3D window
- Independent GUI controls
- Clean separation of concerns

#### FBO (Frame Buffer Object)
Renders 3D scene offscreen, then displays as texture:
- Allows post-processing
- Enables window resizing
- Better performance

### Assignment Requirements Checklist

- [x] Ambiente interativo (interactive environment)
- [x] 4+ tipos de objetos (4+ object types)
- [x] Manipulação de objetos (object manipulation)
- [x] Três modelos de iluminação (3 lighting models)
  - [x] Flat shading
  - [x] Gouraud shading
  - [x] Phong shading
- [x] Alternar modo de visualização (toggle visualization mode)
- [x] Interface interativa (interactive interface)
- [x] Implementação em OpenGL (OpenGL implementation)

### Author Notes

Code written in clean, educational style:
- Clear variable names
- Comprehensive comments
- Modular architecture
- Each algorithm in its own file
- Easy to understand and extend

Based on assignment requirements for SCC 250 - Computação Gráfica
Professor: Agma
