"""
Phong Shading Implementation - From Scratch
Implements true per-fragment Phong lighting using modern GLSL shaders with VBO rendering.
Supports all shapes: sphere, cube, torus, pyramid.
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

    // Specular
    float spec = pow(max(dot(R, V), 0.0), shininess);
    vec3 specular = lightSpecular * Ks.rgb * spec;

    vec3 result = ambient + diffuse + specular;
    FragColor = vec4(result, Kd.a);
}
"""

def compile_phong_shaders():
    """
    Compiles the vertex and fragment shaders for Phong shading.
    Returns the compiled program ID or None if compilation fails.
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
    Compiles the shaders if not already done.
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

def generate_sphere_triangles(slices=20, stacks=20):
    """
    Generates vertex positions and normals for a unit sphere using triangles.
    Returns lists of [x,y,z] for positions and normals.
    """
    pos = []
    norm = []
    for i in range(stacks):
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
            # Triangle 1
            pos.extend([[x0 * zr0, y0 * zr0, z0], [x1 * zr0, y1 * zr0, z0], [x1 * zr1, y1 * zr1, z1]])
            norm.extend([[x0 * zr0, y0 * zr0, z0], [x1 * zr0, y1 * zr0, z0], [x1 * zr1, y1 * zr1, z1]])
            # Triangle 2
            pos.extend([[x0 * zr0, y0 * zr0, z0], [x1 * zr1, y1 * zr1, z1], [x0 * zr1, y0 * zr1, z1]])
            norm.extend([[x0 * zr0, y0 * zr0, z0], [x1 * zr1, y1 * zr1, z1], [x0 * zr1, y0 * zr1, z1]])
    return pos, norm

def generate_cube_triangles():
    """
    Generates vertex positions and normals for a cube using triangles (duplicated verts for flat shading).
    Returns lists of [x,y,z] for positions and normals.
    """
    pos = []
    norm = []
    half = 1.0
    # Back face (z = -half)
    n = [0, 0, -1]
    pos.extend([[-half, -half, -half], [half, -half, -half], [half, half, -half],
                [-half, -half, -half], [half, half, -half], [-half, half, -half]])
    for _ in range(6):
        norm.extend(n)
    # Front face (z = half)
    n = [0, 0, 1]
    pos.extend([[-half, -half, half], [half, half, half], [half, -half, half],
                [-half, half, half], [-half, -half, half], [half, -half, half]])
    for _ in range(6):
        norm.extend(n)
    # Bottom face (y = -half)
    n = [0, -1, 0]
    pos.extend([[-half, -half, -half], [half, -half, half], [half, -half, -half],
                [-half, -half, -half], [-half, -half, half], [-half, -half, half]])
    for _ in range(6):
        norm.extend(n)
    # Top face (y = half)
    n = [0, 1, 0]
    pos.extend([[half, half, -half], [half, half, half], [-half, half, half],
                [half, half, -half], [-half, half, half], [-half, half, -half]])
    for _ in range(6):
        norm.extend(n)
    # Left face (x = -half)
    n = [-1, 0, 0]
    pos.extend([[-half, -half, -half], [-half, -half, half], [-half, half, half],
                [-half, -half, -half], [-half, half, half], [-half, half, -half]])
    for _ in range(6):
        norm.extend(n)
    # Right face (x = half)
    n = [1, 0, 0]
    pos.extend([[half, half, half], [half, -half, -half], [half, -half, half],
                [half, half, half], [half, half, -half], [half, -half, -half]])
    for _ in range(6):
        norm.extend(n)
    return pos, norm

def generate_torus_triangles(rings=16, sides=32):
    """
    Generates vertex positions and normals for a torus using triangles.
    Returns lists of [x,y,z] for positions and normals.
    """
    pos = []
    norm = []
    inner_radius = 0.4
    outer_radius = 1.0
    for i in range(rings):
        for j in range(sides):
            for k in range(2):
                s = (i + k) % rings
                t = j % sides
                
                theta = s * 2.0 * math.pi / rings
                phi = t * 2.0 * math.pi / sides
                
                x = (outer_radius + inner_radius * math.cos(phi)) * math.cos(theta)
                y = (outer_radius + inner_radius * math.cos(phi)) * math.sin(theta)
                z = inner_radius * math.sin(phi)
                
                nx = math.cos(phi) * math.cos(theta)
                ny = math.cos(phi) * math.sin(theta)
                nz = math.sin(phi)
                
                pos.append([x, y, z])
                norm.append([nx, ny, nz])
            
            # Second set for the quad
            s1 = (i + 1) % rings
            t = j % sides
            
            theta1 = s1 * 2.0 * math.pi / rings
            phi = t * 2.0 * math.pi / sides
            
            x1 = (outer_radius + inner_radius * math.cos(phi)) * math.cos(theta1)
            y1 = (outer_radius + inner_radius * math.cos(phi)) * math.sin(theta1)
            z1 = inner_radius * math.sin(phi)
            
            nx1 = math.cos(phi) * math.cos(theta1)
            ny1 = math.cos(phi) * math.sin(theta1)
            nz1 = math.sin(phi)
            
            pos.append([x1, y1, z1])
            norm.append([nx1, ny1, nz1])
            
            # For triangles, but this is approximate; adjust for proper triangulation
            # Actually, for quad strip to triangles, but for simplicity, this generates more verts
    # Note: This is a simplified generation; for exact, use proper triangle list
    # But for demo, use the loop to append 6 verts per quad
    pos = []
    norm = []
    for i in range(rings):
        theta0 = i * 2.0 * math.pi / rings
        theta1 = (i + 1) * 2.0 * math.pi / rings
        for j in range(sides):
            phi0 = j * 2.0 * math.pi / sides
            phi1 = (j + 1) * 2.0 * math.pi / sides
            
            # Quad vertices
            # v0
            x0 = (outer_radius + inner_radius * math.cos(phi0)) * math.cos(theta0)
            y0 = (outer_radius + inner_radius * math.cos(phi0)) * math.sin(theta0)
            z0 = inner_radius * math.sin(phi0)
            n0x = math.cos(phi0) * math.cos(theta0)
            n0y = math.cos(phi0) * math.sin(theta0)
            n0z = math.sin(phi0)
            # v1
            x1 = (outer_radius + inner_radius * math.cos(phi1)) * math.cos(theta0)
            y1 = (outer_radius + inner_radius * math.cos(phi1)) * math.sin(theta0)
            z1 = inner_radius * math.sin(phi1)
            n1x = math.cos(phi1) * math.cos(theta0)
            n1y = math.cos(phi1) * math.sin(theta0)
            n1z = math.sin(phi1)
            # v2
            x2 = (outer_radius + inner_radius * math.cos(phi1)) * math.cos(theta1)
            y2 = (outer_radius + inner_radius * math.cos(phi1)) * math.sin(theta1)
            z2 = inner_radius * math.sin(phi1)
            n2x = math.cos(phi1) * math.cos(theta1)
            n2y = math.cos(phi1) * math.sin(theta1)
            n2z = math.sin(phi1)
            # v3
            x3 = (outer_radius + inner_radius * math.cos(phi0)) * math.cos(theta1)
            y3 = (outer_radius + inner_radius * math.cos(phi0)) * math.sin(theta1)
            z3 = inner_radius * math.sin(phi0)
            n3x = math.cos(phi0) * math.cos(theta1)
            n3y = math.cos(phi0) * math.sin(theta1)
            n3z = math.sin(phi0)
            
            # Triangle 1: v0, v1, v2
            pos.extend([[x0, y0, z0], [x1, y1, z1], [x2, y2, z2]])
            norm.extend([[n0x, n0y, n0z], [n1x, n1y, n1z], [n2x, n2y, n2z]])
            # Triangle 2: v0, v2, v3
            pos.extend([[x0, y0, z0], [x2, y2, z2], [x3, y3, z3]])
            norm.extend([[n0x, n0y, n0z], [n2x, n2y, n2z], [n3x, n3y, n3z]])
    return pos, norm

def generate_pyramid_triangles():
    """
    Generates vertex positions and normals for a pyramid using triangles.
    Returns lists of [x,y,z] for positions and normals.
    """
    pos = []
    norm = []
    apex = [0, 1.5, 0]
    base = [
        [-1, -1, 1],   # 0 front left
        [1, -1, 1],    # 1 front right
        [1, -1, -1],   # 2 back right
        [-1, -1, -1]   # 3 back left
    ]
    # Base (quad as two triangles), normal [0,-1,0]
    n_base = [0, -1, 0]
    # Tri 1: 0,1,2
    pos.extend([base[0], base[1], base[2]])
    norm.extend([n_base, n_base, n_base])
    # Tri 2: 0,2,3
    pos.extend([base[0], base[2], base[3]])
    norm.extend([n_base, n_base, n_base])
    # Front face tri: apex,0,1 normal [0,0.5,1] normalized? but approx
    n_front = [0, 0.707, 0.707]  # normalized [0,0.5,1]
    pos.extend([apex, base[0], base[1]])
    norm.extend([n_front, n_front, n_front])
    # Right face: apex,1,2 [0.707,0.707,0]
    n_right = [0.707, 0.707, 0]
    pos.extend([apex, base[1], base[2]])
    norm.extend([n_right, n_right, n_right])
    # Back face: apex,2,3 [0,0.707,-0.707]
    n_back = [0, 0.707, -0.707]
    pos.extend([apex, base[2], base[3]])
    norm.extend([n_back, n_back, n_back])
    # Left face: apex,3,0 [-0.707,0.707,0]
    n_left = [-0.707, 0.707, 0]
    pos.extend([apex, base[3], base[0]])
    norm.extend([n_left, n_left, n_left])
    return pos, norm

def draw_phong(estado):
    """
    Draws the selected shape using Phong shader with VBO rendering.
    Uses the current OpenGL matrices and estado for light and material.
    """
    global shaderprogram
    if not shaderprogram:
        return
    
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
    
    # Compute normal matrix
    modelview_3x3 = modelview[:3, :3]
    normal_mat = np.transpose(np.linalg.inv(modelview_3x3)).astype(np.float32)
    
    # Set matrix uniforms
    glUniformMatrix4fv(modelView_loc, 1, GL_FALSE, modelview)
    glUniformMatrix4fv(projection_loc, 1, GL_FALSE, projection)
    glUniformMatrix3fv(normalMatrix_loc, 1, GL_FALSE, normal_mat)
    
    # Light properties
    light_pos = np.array(estado.light_pos[:3], dtype=np.float32)
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
        pos_list, norm_list = generate_sphere_triangles(20, 20)
    elif shape == 'cube':
        pos_list, norm_list = generate_cube_triangles()
    elif shape == 'torus':
        pos_list, norm_list = generate_torus_triangles(16, 32)
    elif shape == 'pyramid':
        pos_list, norm_list = generate_pyramid_triangles()
    else:
        pos_list, norm_list = generate_sphere_triangles(20, 20)  # Default to sphere
    
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
    glDrawArrays(GL_TRIANGLES, 0, len(pos_data) // 3)
    
    # Clean up
    glDisableVertexAttribArray(pos_loc)
    glDisableVertexAttribArray(norm_loc)
    glDeleteBuffers(2, [vbo_pos, vbo_norm])

def get_name():
    """Return the display name of this lighting model."""
    return "Phong"

def get_description():
    """Return a description of this lighting model."""
    return "True per-fragment Phong lighting with VBO-based rendering"
