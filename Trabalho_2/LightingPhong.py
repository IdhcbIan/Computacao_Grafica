"""
Phong Shading Implementation - Implementação Real com Shaders

Phong shading calcula a iluminação em CADA PIXEL usando shaders GLSL.
Este é o modelo de iluminação mais realista dos três.

Como funciona:
- Vertex shader: Passa normais e posições para o fragment shader
- Fragment shader: Calcula iluminação por pixel usando modelo de Phong
  - Componente ambiente (ambient): Luz base constante
  - Componente difusa (diffuse): Luz direta (Lei de Lambert)
  - Componente especular (specular): Reflexos brilhantes
- Resultado: Highlights especulares muito mais realistas

Modelo matemático de Phong:
I = I_ambiente + I_difusa + I_especular
I_difusa = I_luz * k_d * (N · L)
I_especular = I_luz * k_s * (R · V)^shininess

Desenvolvido por Bui Tuong Phong em 1973
"""
from OpenGL.GL import *
from OpenGL.GL.shaders import compileProgram, compileShader
import os

# Variável global para armazenar o programa de shader compilado
shader_program = None

def load_shader_source(filename):
    """
    Carrega o código fonte de um arquivo de shader

    Args:
        filename: Nome do arquivo shader (.glsl)

    Returns:
        String contendo o código fonte do shader
    """
    # Obter o diretório onde este arquivo Python está localizado
    current_dir = os.path.dirname(os.path.abspath(__file__))
    shader_path = os.path.join(current_dir, filename)

    try:
        with open(shader_path, 'r') as f:
            return f.read()
    except FileNotFoundError:
        print(f"Erro: Arquivo shader não encontrado: {shader_path}")
        return None

def compile_phong_shaders():
    """
    Compila os shaders de vértice e fragmento para Phong shading

    Returns:
        ID do programa de shader compilado, ou None se houver erro
    """
    # Carregar o código fonte dos shaders
    vertex_source = load_shader_source("phong_vertex.glsl")
    fragment_source = load_shader_source("phong_fragment.glsl")

    if not vertex_source or not fragment_source:
        print("Erro: Não foi possível carregar os shaders")
        return None

    try:
        # Compilar vertex shader
        vertex_shader = compileShader(vertex_source, GL_VERTEX_SHADER)

        # Compilar fragment shader
        fragment_shader = compileShader(fragment_source, GL_FRAGMENT_SHADER)

        # Linkar os shaders em um programa
        program = compileProgram(vertex_shader, fragment_shader)

        print("Shaders Phong compilados com sucesso!")
        return program

    except Exception as e:
        print(f"Erro ao compilar shaders: {e}")
        return None

def enable():
    """
    Ativa o Phong shading usando shaders GLSL customizados

    Esta função:
    1. Compila os shaders (se ainda não foram compilados)
    2. Ativa o programa de shader
    3. Configura o OpenGL para usar iluminação por pixel
    """
    global shader_program

    # Compilar shaders apenas uma vez
    if shader_program is None:
        shader_program = compile_phong_shaders()

    # Ativar o programa de shader
    if shader_program:
        glUseProgram(shader_program)
    else:
        # Fallback: usar GL_SMOOTH se os shaders falharem
        print("Aviso: Usando GL_SMOOTH como fallback")
        glUseProgram(0)  # Desativar shaders
        glShadeModel(GL_SMOOTH)

def disable():
    """
    Desativa o Phong shading e retorna ao pipeline fixo do OpenGL
    """
    glUseProgram(0)

def get_name():
    """Retorna o nome de exibição deste modelo de iluminação"""
    return "Phong"

def get_description():
    """Retorna uma descrição deste modelo de iluminação"""
    return "Iluminação por pixel com shaders GLSL"
