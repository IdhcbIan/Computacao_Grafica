import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import math
import numpy as np

# Constants
LARGURA_JANELA = 800
ALTURA_JANELA = 850
FPS = 60
LARGURA_3D = 700
ALTURA_3D = 700

# Colors for materials
MATERIAL_COLORS = {
    'orange': {'ambient': [0.2, 0.1, 0.05, 1.0], 'diffuse': [1.0, 0.5, 0.2, 1.0], 'specular': [1.0, 1.0, 1.0, 1.0], 'shininess': 50.0},
    'red': {'ambient': [0.2, 0.0, 0.0, 1.0], 'diffuse': [0.8, 0.2, 0.2, 1.0], 'specular': [1.0, 1.0, 1.0, 1.0], 'shininess': 30.0},
    'blue': {'ambient': [0.0, 0.0, 0.2, 1.0], 'diffuse': [0.2, 0.2, 0.8, 1.0], 'specular': [1.0, 1.0, 1.0, 1.0], 'shininess': 50.0},}

LIGHT_AMBIENT = [0.2, 0.2, 0.2, 1.0]
LIGHT_DIFFUSE = [1.0, 1.0, 1.0, 1.0]

class Estado3D:
    def __init__(self):
        self.light_pos = [3.0, 3.0, 3.0, 1.0]
        self.material = 'orange'
        self.shape = 'sphere'  # Shape that apears on initialization!!
        self.camera_angle = 'front'  # Defaut Camera angle!!
        self.lighting_model = 'gouraud'  # Default Lighting model
        self.running = True
        self.projecao = 'perspectiva'
        self.tipo = None
        self.eixo = None
        self.direcao = None
        self.posicao = [0.0, 0.0, 0.0]   # Translacao
        self.rotacao = [0.0, 0.0, 0.0]   # Rotacao (graus)
        self.escala = [1.0, 1.0, 1.0]    # Escala

    def reset_transformacoes(self):
        self.posicao = [0.0, 0.0, 0.0]
        self.rotacao = [0.0, 0.0, 0.0]
        self.escala = [1.0, 1.0, 1.0]
        self.tipo = None
        self.eixo = None
        self.direcao = None

class FBO:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.fbo = glGenFramebuffers(1)
        self.texture = glGenTextures(1)
        self.depth_buffer = glGenRenderbuffers(1)

        glBindFramebuffer(GL_FRAMEBUFFER, self.fbo)

        # Texture
        glBindTexture(GL_TEXTURE_2D, self.texture)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, width, height, 0, GL_RGBA, GL_UNSIGNED_BYTE, None)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glFramebufferTexture2D(GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT0, GL_TEXTURE_2D, self.texture, 0)

        # Depth buffer
        glBindRenderbuffer(GL_RENDERBUFFER, self.depth_buffer)
        glRenderbufferStorage(GL_RENDERBUFFER, GL_DEPTH_COMPONENT, width, height)
        glFramebufferRenderbuffer(GL_FRAMEBUFFER, GL_DEPTH_ATTACHMENT, GL_RENDERBUFFER, self.depth_buffer)

        glBindFramebuffer(GL_FRAMEBUFFER, 0)

    def bind(self):
        glBindFramebuffer(GL_FRAMEBUFFER, self.fbo)
        glViewport(0, 0, self.width, self.height)

    def unbind(self):
        glBindFramebuffer(GL_FRAMEBUFFER, 0)

    def get_texture_surface(self):
        glBindFramebuffer(GL_FRAMEBUFFER, self.fbo)
        pixels = glReadPixels(0, 0, self.width, self.height, GL_RGBA, GL_UNSIGNED_BYTE)
        glBindFramebuffer(GL_FRAMEBUFFER, 0)
        # Convert to numpy array and reshape for flipping
        pixels = np.frombuffer(pixels, dtype=np.uint8).reshape((self.height, self.width, 4))
        # Flip vertically for Pygame (OpenGL origin is bottom-left)
        pixels = np.flipud(pixels)
        # Flatten back to bytes
        pixels_bytes = pixels.tobytes()
        image = pygame.image.frombuffer(pixels_bytes, (self.width, self.height), "RGBA")
        return image

def init_opengl():
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)
    glLightfv(GL_LIGHT0, GL_AMBIENT, LIGHT_AMBIENT)
    glLightfv(GL_LIGHT0, GL_DIFFUSE, LIGHT_DIFFUSE)
    glShadeModel(GL_SMOOTH)
    glEnable(GL_NORMALIZE)

def draw_shape(shape_name='sphere', material_name='orange'):
    """Draw the specified shape with the given material"""
    # Import shape modules dynamically
    if shape_name == 'sphere':
        from Object import Sphere
        Sphere.draw_sphere(MATERIAL_COLORS, material_name)
    elif shape_name == 'cube':
        from Object import Cube
        Cube.draw_cube(MATERIAL_COLORS, material_name)
    elif shape_name == 'torus':
        from Object import Torus
        Torus.draw_torus(MATERIAL_COLORS, material_name)
    elif shape_name == 'pyramid':
        from Object import Pyramid
        Pyramid.draw_pyramid(MATERIAL_COLORS, material_name)
    else:
        # Default to sphere
        from Object import Sphere
        Sphere.draw_sphere(MATERIAL_COLORS, material_name)

# Keep old function for backward compatibility
def draw_sphere(material_name='orange'):
    draw_shape('sphere', material_name)

def update_light(estado):
    glLightfv(GL_LIGHT0, GL_POSITION, estado.light_pos)

def aplica_transformacao(estado):
    passo = 0.2 # unidades
    ang_rotacao = 5 # graus
    if estado.direcao not in ("mais", "menos"):
        return
    direcao = 1 if estado.direcao == "mais" else -1

    if estado.tipo == 'translacao':
        deslocamento = direcao * passo
        if estado.eixo == 'eixo_x': estado.posicao[0] += deslocamento
        if estado.eixo == 'eixo_y': estado.posicao[1] += deslocamento
        if estado.eixo == 'eixo_z': estado.posicao[2] += deslocamento
        print(estado.posicao)
    elif estado.tipo == 'rotacao':
        angulo = direcao * ang_rotacao
        if estado.eixo == 'eixo_x': estado.rotacao[0] += angulo
        if estado.eixo == 'eixo_y': estado.rotacao[1] += angulo
        if estado.eixo == 'eixo_z': estado.rotacao[2] += angulo
    elif estado.tipo == 'escala':
        fator = 1 + direcao * 0.1
        if estado.eixo == 'eixo_x': estado.escala[0] *= fator
        if estado.eixo == 'eixo_y': estado.escala[1] *= fator
        if estado.eixo == 'eixo_z': estado.escala[2] *= fator

def set_lighting_model(model_name='gouraud'):  # Defaut Shading = gouraud!!
    """
    Configura o modelo de iluminação (flat, gouraud ou phong)

    So um ifelse normal!!
    """
    if model_name == 'phong':
        return  # Handled separately because of custom OpenGL implementation!!
    if model_name == 'flat':
        from Light import LightingFlat
        LightingFlat.enable()
    elif model_name == 'gouraud':
        from Light import LightingGouraud
        LightingGouraud.enable()
    else:
        from Light import LightingGouraud
        LightingGouraud.enable()

def render_3d_to_texture(estado, fbo):
    fbo.bind()
    glClearColor(0.1, 0.1, 0.2, 1.0)  # Dark background!!
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    glEnable(GL_DEPTH_TEST)
    glEnable(GL_LIGHTING)

    # Projecao escolhida
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    aspect_ratio = fbo.width / fbo. height
    if estado.projecao == "ortografica":
        glOrtho(-3 * aspect_ratio, 3 * aspect_ratio, -3, 3, 0.1, 100.0)
    else:
        gluPerspective(45, aspect_ratio, 0.1, 100.0)

    # Set up modelview matrix with camera position
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

    # Camera positions for different angles
    if estado.camera_angle == 'front':
        gluLookAt(0, 0, 8, 0, 0, 0, 0, 1, 0)  # Front view
    elif estado.camera_angle == 'top':
        gluLookAt(0, 8, 0.1, 0, 0, 0, 0, 0, -1)  # Top view
    elif estado.camera_angle == 'side':
        gluLookAt(8, 0, 0, 0, 0, 0, 0, 1, 0)  # Side view
    elif estado.camera_angle == 'diagonal':
        gluLookAt(5, 5, 5, 0, 0, 0, 0, 1, 0)  # Diagonal view
    else:
        gluLookAt(0, 0, 8, 0, 0, 0, 0, 1, 0)  # Default front

    update_light(estado)

    # Transformacoes geometricas
    glTranslatef(*estado.posicao)
    glRotatef(estado.rotacao[0], 1, 0, 0)
    glRotatef(estado.rotacao[1], 0, 1, 0)
    glRotatef(estado.rotacao[2], 0, 0, 1)
    glScalef(*estado.escala)

    # Handle lighting and drawing
    if estado.lighting_model == 'phong':
        from Light import LightingPhong
        LightingPhong.enable(estado)
        LightingPhong.draw_phong(estado)
        LightingPhong.disable()
    else:
        set_lighting_model(estado.lighting_model)
        draw_shape(estado.shape, estado.material)

    fbo.unbind()
