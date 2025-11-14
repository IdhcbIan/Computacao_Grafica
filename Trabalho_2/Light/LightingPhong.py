"""
Phong Shading Implementation
"""

from OpenGL.GL import *
from OpenGL.GL.shaders import compileProgram, compileShader
import numpy as np
import math
from Aux_3D import MATERIAL_COLORS, LIGHT_AMBIENT, LIGHT_DIFFUSE

# Global shader program
shaderprogram = None

# Core profile GLSL shader sources
VERTEX_SHADER_SOURCE = """
#version 330 core

layout (location = 0) in vec3 aPos;
layout (location = 1) in vec3 aNormal;

uniform mat4 modelView;
uniform mat4 projection;
uniform mat3 normalMatrix;

out vec3 fragPos;
out vec3 fragNormal;

void main() {
    gl_Position = projection * modelView * vec4(aPos, 1.0);
    fragPos = vec3(modelView * vec4(aPos, 1.0));
    fragNormal = normalMatrix * aNormal;
}
"""

FRAGMENT_SHADER_SOURCE = """
#version 330 core

in vec3 fragPos;
in vec3 fragNormal;

uniform vec3 lightPos;
uniform vec3 lightAmbient;
uniform vec3 lightDiffuse;
uniform vec3 lightSpecular;
uniform vec4 Ka;
uniform vec4 Kd;
uniform vec4 Ks;
uniform float shininess;

out vec4 FragColor;

void main() {
    vec3 N = normalize(fragNormal);
    vec3 L = normalize(lightPos - fragPos);
    vec3 V = normalize(-fragPos);
    vec3 R = reflect(-L, N);

    // Ambient
    vec3 ambient = lightAmbient * Ka.rgb;

    // Diffuse
    float diff = max(dot(N, L), 0.0);
    vec3 diffuse = lightDiffuse * Kd.rgb * diff;

    // Specular (only when surface is lit)
    float spec = 0.0;
    if (diff > 0.0) {
        spec = pow(max(dot(R, V), 0.0), shininess);
    }
    vec3 specular = lightSpecular * Ks.rgb * spec;

    vec3 result = ambient + diffuse + specular;
    FragColor = vec4(result, Kd.a);
}
"""

def compile_phong_shaders():
    """
    Compiles the vertex and fragment shaders for Phong shading.
    """
    try:
        vertex_shader = compileShader(VERTEX_SHADER_SOURCE, GL_VERTEX_SHADER)
        fragment_shader = compileShader(FRAGMENT_SHADER_SOURCE, GL_FRAGMENT_SHADER)
        program = compileProgram(vertex_shader, fragment_shader)
        print("Phong shaders compiled successfully!")
        return program
    except Exception as e:
        print(f"Error compiling Phong shaders: {e}")
        return None

def enable(estado=None):
    """
    Enables the Phong shader program.
    """
    global shaderprogram
    if shaderprogram is None:
        shaderprogram = compile_phong_shaders()
        if not shaderprogram:
            print("Warning: Phong shader compilation failed, falling back to smooth shading")
            glShadeModel(GL_SMOOTH)
            glEnable(GL_LIGHTING)
            return
    glUseProgram(shaderprogram)
    glDisable(GL_LIGHTING)

def disable():
    """
    Disables the Phong shader program and re-enables fixed pipeline lighting.
    """
    global shaderprogram
    if shaderprogram:
        glUseProgram(0)
    glEnable(GL_LIGHTING)
    glShadeModel(GL_SMOOTH)

def generate_sphere_triangles(slices=32, stacks=32):
    """
    Generates vertex positions and normals for a unit sphere using triangles.
    Returns lists of [x,y,z] for positions and normals.
    """
    pos = []
    norm = []
    for i in range(stacks + 1):
        lat0 = math.pi * (-0.5 + float(i) / stacks)
        z0 = math.sin(lat0)
        zr0 = math.cos(lat0)
        lat1 = math.pi * (-0.5 + float(i + 1) / stacks)
        z1 = math.sin(lat1)
        zr1 = math.cos(lat1)
        for j in range(slices):
            lng0 = 2 * math.pi * float(j) / slices
            x0 = math.cos(lng0)
            y0 = math.sin(lng0)
            lng1 = 2 * math.pi * float(j + 1) / slices
            x1 = math.cos(lng1)
            y1 = math.sin(lng1)
            # Triangle 1: Reversed order for CCW (v0, v2, v1 instead of v0,v1,v2 for southern hemisphere)
            if i < stacks:
                # Bottom triangle (pointing outward)
                pos.extend([[x0 * zr0, y0 * zr0, z0], [x1 * zr1, y1 * zr1, z1], [x1 * zr0, y1 * zr0, z0]])
                norm.extend([[x0 * zr0, y0 * zr0, z0], [x1 * zr1, y1 * zr1, z1], [x1 * zr0, y1 * zr0, z0]])
                # Top triangle
                pos.extend([[x0 * zr0, y0 * zr0, z0], [x0 * zr1, y0 * zr1, z1], [x1 * zr1, y1 * zr1, z1]])
                norm.extend([[x0 * zr0, y0 * zr0, z0], [x0 * zr1, y0 * zr1, z1], [x1 * zr1, y1 * zr1, z1]])
    return pos, norm

def generate_cube_triangles():
    """
    Generates vertex positions and normals for a cube using triangles (duplicated verts for flat shading).
    Returns lists of [x,y,z] for positions and normals.
    """
    pos = []
    norm = []
    half = 1.0
    # Back face (z = -half), viewed from back: CCW [0,3,2,1] -> triangles [0,3,2] and [0,2,1]
    n = [0, 0, -1]
    # Tri 1: bottom-left, top-left, top-right
    pos.extend([[-half, -half, -half], [-half, half, -half], [half, half, -half]])
    norm.extend([n, n, n])
    # Tri 2: bottom-left, top-right, bottom-right
    pos.extend([[-half, -half, -half], [half, half, -half], [half, -half, -half]])
    norm.extend([n, n, n])
    # Front face (z = half), viewed from front: CCW [4,5,7,6] -> [4,5,7] [4,7,6]
    n = [0, 0, 1]
    pos.extend([[-half, -half, half], [half, -half, half], [half, half, half]])
    norm.extend([n, n, n])
    pos.extend([[-half, -half, half], [half, half, half], [-half, half, half]])
    norm.extend([n, n, n])
    # Bottom face (y = -half), viewed from below: CCW [0,4,5,1] but reverse for outward -> [0,1,5,4]
    n = [0, -1, 0]
    pos.extend([[half, -half, -half], [half, -half, half], [-half, -half, half]])
    norm.extend([n, n, n])
    pos.extend([[half, -half, -half], [-half, -half, half], [-half, -half, -half]])
    norm.extend([n, n, n])
    # Top face (y = half), viewed from above: CCW [3,2,6,7]
    n = [0, 1, 0]
    pos.extend([[-half, half, -half], [half, half, -half], [half, half, half]])
    norm.extend([n, n, n])
    pos.extend([[-half, half, -half], [half, half, half], [-half, half, half]])
    norm.extend([n, n, n])
    # Left face (x = -half), viewed from left: CCW [0,4,7,3]
    n = [-1, 0, 0]
    pos.extend([[-half, -half, -half], [-half, -half, half], [-half, half, half]])
    norm.extend([n, n, n])
    pos.extend([[-half, -half, -half], [-half, half, half], [-half, half, -half]])
    norm.extend([n, n, n])
    # Right face (x = half), viewed from right: CCW [1,5,6,2]
    n = [1, 0, 0]
    pos.extend([[half, -half, half], [half, -half, -half], [half, half, -half]])
    norm.extend([n, n, n])
    pos.extend([[half, -half, half], [half, half, -half], [half, half, half]])
    norm.extend([n, n, n])
    return pos, norm

def generate_torus_triangles(rings=24, sides=48):
    """
    Generates vertex positions and normals for a torus using triangles.
    Returns lists of [x,y,z] for positions and normals.
    """
    pos = []
    norm = []
    inner_radius = 0.4
    outer_radius = 1.0
    for i in range(rings):
        theta0 = i * 2.0 * math.pi / rings
        theta1 = (i + 1) * 2.0 * math.pi / rings
        for j in range(sides):
            phi0 = j * 2.0 * math.pi / sides
            phi1 = (j + 1) * 2.0 * math.pi / sides
            
            # Quad vertices (v0 bottom-left, v1 bottom-right, v2 top-right, v3 top-left)
            # v0
            x0 = (outer_radius + inner_radius * math.cos(phi0)) * math.cos(theta0)
            y0 = (outer_radius + inner_radius * math.cos(phi0)) * math.sin(theta0)
            z0 = inner_radius * math.sin(phi0)
            n0 = [math.cos(phi0) * math.cos(theta0), math.cos(phi0) * math.sin(theta0), math.sin(phi0)]
            # v1
            x1 = (outer_radius + inner_radius * math.cos(phi1)) * math.cos(theta0)
            y1 = (outer_radius + inner_radius * math.cos(phi1)) * math.sin(theta0)
            z1 = inner_radius * math.sin(phi1)
            n1 = [math.cos(phi1) * math.cos(theta0), math.cos(phi1) * math.sin(theta0), math.sin(phi1)]
            # v2
            x2 = (outer_radius + inner_radius * math.cos(phi1)) * math.cos(theta1)
            y2 = (outer_radius + inner_radius * math.cos(phi1)) * math.sin(theta1)
            z2 = inner_radius * math.sin(phi1)
            n2 = [math.cos(phi1) * math.cos(theta1), math.cos(phi1) * math.sin(theta1), math.sin(phi1)]
            # v3
            x3 = (outer_radius + inner_radius * math.cos(phi0)) * math.cos(theta1)
            y3 = (outer_radius + inner_radius * math.cos(phi0)) * math.sin(theta1)
            z3 = inner_radius * math.sin(phi0)
            n3 = [math.cos(phi0) * math.cos(theta1), math.cos(phi0) * math.sin(theta1), math.sin(phi0)]
            
            # Triangle 1: v0, v1, v2 (CCW when viewed from outside)
            pos.extend([[x0, y0, z0], [x1, y1, z1], [x2, y2, z2]])
            norm.extend([n0, n1, n2])
            # Triangle 2: v0, v2, v3 (CCW)
            pos.extend([[x0, y0, z0], [x2, y2, z2], [x3, y3, z3]])
            norm.extend([n0, n2, n3])
    return pos, norm

def generate_pyramid_triangles():
    """
    Generates vertex positions and normals for a pyramid using triangles.
    Returns lists of [x,y,z] for positions and normals.
    """
    pos = []
    norm = []
    apex = [0, -1.5, 0]
    base = [
        [-1, 1, 1],   # 0 front left (now at y=1)
        [1, 1, 1],    # 1 front right
        [1, 1, -1],   # 2 back right
        [-1, 1, -1]   # 3 back left
    ]
    # Base (quad as two triangles) now on top, normal pointing up
    n_base = [0, 1, 0]
    pos.extend([base[0], base[1], base[2]])
    norm.extend([n_base, n_base, n_base])
    pos.extend([base[0], base[2], base[3]])
    norm.extend([n_base, n_base, n_base])
    # Front face: ensure outward normal points toward +Z
    n_front = [0, -0.5, 1]
    pos.extend([apex, base[1], base[0]])
    norm.extend([n_front, n_front, n_front])
    # Right face: outward normal toward +X
    n_right = [1, -0.5, 0]
    pos.extend([apex, base[2], base[1]])
    norm.extend([n_right, n_right, n_right])
    # Back face: outward normal toward -Z
    n_back = [0, -0.5, -1]
    pos.extend([apex, base[3], base[2]])
    norm.extend([n_back, n_back, n_back])
    # Left face: outward normal toward -X
    n_left = [-1, -0.5, 0]
    pos.extend([apex, base[0], base[3]])
    norm.extend([n_left, n_left, n_left])
    return pos, norm

def draw_phong(estado):
    """
    Draws the selected shape using Phong shader with VBO rendering.
    """
    global shaderprogram
    if not shaderprogram:
        return
    
    # Disable culling to show all sides fully
    glDisable(GL_CULL_FACE)
    
    # Get uniform locations (get once per draw for simplicity)
    modelView_loc = glGetUniformLocation(shaderprogram, "modelView")
    projection_loc = glGetUniformLocation(shaderprogram, "projection")
    normalMatrix_loc = glGetUniformLocation(shaderprogram, "normalMatrix")
    lightPos_loc = glGetUniformLocation(shaderprogram, "lightPos")
    lightAmbient_loc = glGetUniformLocation(shaderprogram, "lightAmbient")
    lightDiffuse_loc = glGetUniformLocation(shaderprogram, "lightDiffuse")
    lightSpecular_loc = glGetUniformLocation(shaderprogram, "lightSpecular")
    Ka_loc = glGetUniformLocation(shaderprogram, "Ka")
    Kd_loc = glGetUniformLocation(shaderprogram, "Kd")
    Ks_loc = glGetUniformLocation(shaderprogram, "Ks")
    shininess_loc = glGetUniformLocation(shaderprogram, "shininess")
    
    # Get current matrices
    modelview = np.zeros((4, 4), dtype=np.float32)
    projection = np.zeros((4, 4), dtype=np.float32)
    glGetFloatv(GL_MODELVIEW_MATRIX, modelview)
    glGetFloatv(GL_PROJECTION_MATRIX, projection)

    # OpenGL matrices are column-major. Reshape to 4x4 matrix (already column-major)
    modelview_mat = modelview.reshape(4, 4)

    # For numpy calculations, we need row-major
    modelview_rm = modelview_mat.T

    # Compute normal matrix: transpose(inverse(upper-left 3x3))
    # Extract upper-left 3x3 from row-major version
    modelview_3x3 = modelview_rm[:3, :3]
    # Compute transpose(inverse(M)) which equals inverse(M).T
    normal_mat_rm = np.linalg.inv(modelview_3x3).T
    # Convert back to column-major for OpenGL
    normal_mat = normal_mat_rm.T.astype(np.float32)

    # Set matrix uniforms (all matrices should be in column-major format for OpenGL)
    glUniformMatrix4fv(modelView_loc, 1, GL_FALSE, modelview)
    glUniformMatrix4fv(projection_loc, 1, GL_FALSE, projection)
    glUniformMatrix3fv(normalMatrix_loc, 1, GL_FALSE, normal_mat.flatten())

    # Light properties - transform light position from world to view space
    # In the fixed-function pipeline (Flat/Gouraud), glLightfv transforms the light
    # position by the current modelview matrix. We need to replicate that here.
    light_pos_world = np.array(estado.light_pos, dtype=np.float32)

    # Transform using the modelview matrix (column-major from OpenGL)
    # Reshape and transpose to get row-major, then multiply
    # For a point light (w=1), this transforms it to view space
    light_pos_view_homogeneous = modelview_rm @ light_pos_world

    # Extract xyz and normalize if it's a directional light, or just take xyz for point light
    if light_pos_world[3] != 0.0:  # Point light
        light_pos = (light_pos_view_homogeneous[:3] / light_pos_view_homogeneous[3]).astype(np.float32)
    else:  # Directional light
        light_pos = light_pos_view_homogeneous[:3].astype(np.float32)
    light_ambient = np.array(LIGHT_AMBIENT[:3], dtype=np.float32)
    light_diffuse = np.array(LIGHT_DIFFUSE[:3], dtype=np.float32)
    light_specular = np.array([1.0, 1.0, 1.0], dtype=np.float32)
    
    glUniform3fv(lightPos_loc, 1, light_pos)
    glUniform3fv(lightAmbient_loc, 1, light_ambient)
    glUniform3fv(lightDiffuse_loc, 1, light_diffuse)
    glUniform3fv(lightSpecular_loc, 1, light_specular)
    
    # Material properties
    material = MATERIAL_COLORS.get(estado.material, MATERIAL_COLORS['orange'])
    Ka = np.array(material['ambient'], dtype=np.float32)
    Kd = np.array(material['diffuse'], dtype=np.float32)
    Ks = np.array(material['specular'], dtype=np.float32)
    shininess_val = material['shininess']
    
    glUniform4fv(Ka_loc, 1, Ka)
    glUniform4fv(Kd_loc, 1, Kd)
    glUniform4fv(Ks_loc, 1, Ks)
    glUniform1f(shininess_loc, shininess_val)
    
    # Generate vertices based on shape
    shape = estado.shape
    if shape == 'sphere':
        pos_list, norm_list = generate_sphere_triangles(32, 32)
    elif shape == 'cube':
        pos_list, norm_list = generate_cube_triangles()
    elif shape == 'torus':
        pos_list, norm_list = generate_torus_triangles(24, 48)
    elif shape == 'pyramid':
        pos_list, norm_list = generate_pyramid_triangles()
    else:
        pos_list, norm_list = generate_sphere_triangles(32, 32)  # Default to sphere
    
    # Create numpy arrays
    pos_data = np.array(pos_list, dtype=np.float32)
    norm_data = np.array(norm_list, dtype=np.float32)
    
    # Create and bind VBOs
    vbo_pos = glGenBuffers(1)
    glBindBuffer(GL_ARRAY_BUFFER, vbo_pos)
    glBufferData(GL_ARRAY_BUFFER, pos_data.nbytes, pos_data, GL_STATIC_DRAW)
    
    vbo_norm = glGenBuffers(1)
    glBindBuffer(GL_ARRAY_BUFFER, vbo_norm)
    glBufferData(GL_ARRAY_BUFFER, norm_data.nbytes, norm_data, GL_STATIC_DRAW)
    
    # Attribute locations
    pos_loc = glGetAttribLocation(shaderprogram, "aPos")
    norm_loc = glGetAttribLocation(shaderprogram, "aNormal")
    
    # Position attribute
    glEnableVertexAttribArray(pos_loc)
    glBindBuffer(GL_ARRAY_BUFFER, vbo_pos)
    glVertexAttribPointer(pos_loc, 3, GL_FLOAT, GL_FALSE, 0, None)
    
    # Normal attribute
    glEnableVertexAttribArray(norm_loc)
    glBindBuffer(GL_ARRAY_BUFFER, vbo_norm)
    glVertexAttribPointer(norm_loc, 3, GL_FLOAT, GL_FALSE, 0, None)
    
    # Draw
    glDrawArrays(GL_TRIANGLES, 0, len(pos_data))
    
    # Clean up
    glDisableVertexAttribArray(pos_loc)
    glDisableVertexAttribArray(norm_loc)
    glDeleteBuffers(2, [vbo_pos, vbo_norm])
    
    # Re-enable culling after draw
    glEnable(GL_CULL_FACE)

def get_name():
    """Return the display name of this lighting model."""
    return "Phong"

def get_description():
    return "True per-fragment Phong lighting with VBO-based rendering"
