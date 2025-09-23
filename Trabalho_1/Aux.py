
import pygame
import math
from typing import List, Optional, Tuple

# Import constants from Main.py
# Note: This will create a circular import, so we'll define constants here instead
COLUNAS_GRADE, LINHAS_GRADE = 60, 60
TAMANHO_CELULA, MARGEM = 20, 32
LARGURA_JANELA = COLUNAS_GRADE * TAMANHO_CELULA + MARGEM * 2
ALTURA_JANELA = LINHAS_GRADE * TAMANHO_CELULA + MARGEM * 2
FPS = 60

BRANCO = (240, 240, 240)
PRETO = (30, 30, 30)
LINHA_GRADE = (120, 120, 120)
XADREZ_A = (210, 210, 210)
XADREZ_B = (245, 245, 245)
VERTICE_ATUAL = (50, 140, 255)
VERTICE_ANTERIOR = (40, 200, 120)
LINHA_TEMPORARIA = (255, 200, 0)
LINHA_PREVIEW = (0, 0, 0)  # Preview lines black after validation
CELULA_POLIGONO = (220, 60, 60)
VERTICE_PRIMEIRO = (255, 50, 50)
TEXTO_HUD = (20, 20, 20)
CelulaNaGrade = Tuple[int, int]

#------// Funcoes //------

"""
    Funcoes para converter coordenadas da grade para coordenadas da tela e vice-versa.
"""

def grade_para_tela(celula: CelulaNaGrade) -> Tuple[int, int]:
    col, linha = celula
    x = MARGEM + col * TAMANHO_CELULA
    y = MARGEM + linha * TAMANHO_CELULA
    return x, y

def centro_celula(celula: CelulaNaGrade) -> Tuple[int, int]:
    x, y = grade_para_tela(celula)
    return x + TAMANHO_CELULA // 2, y + TAMANHO_CELULA // 2

def restringir_celula(celula: CelulaNaGrade) -> CelulaNaGrade:
    col, linha = celula
    col = max(0, min(COLUNAS_GRADE - 1, col))
    linha = max(0, min(LINHAS_GRADE - 1, linha))
    return col, linha

def tela_para_grade(pos: Tuple[int, int]) -> Optional[CelulaNaGrade]:
    x, y = pos
    x_rel = x - MARGEM
    y_rel = y - MARGEM
    if x_rel < 0 or y_rel < 0:
        return None
    col = x_rel // TAMANHO_CELULA
    linha = y_rel // TAMANHO_CELULA
    if 0 <= col < COLUNAS_GRADE and 0 <= linha < LINHAS_GRADE:
        return int(col), int(linha)
    return None

"""
    Classe para representar uma aresta da tabela de arestas (ET/AET).
    Segue a estrutura acadêmica para algoritmo de preenchimento por varredura.
"""

class EdgeEntry:
    def __init__(self, ymax, x, inv_slope):
        """
        Entrada da tabela de arestas.
        ymax: coordenada y máxima da aresta
        x: coordenada x atual (xmin inicial)
        inv_slope: inverso da inclinação (1/m) para atualização de x
        """
        self.ymax = ymax
        self.x = x  # Coordenada x atual
        self.inv_slope = inv_slope  # 1/m para incremento de x
    
    def __str__(self):
        return f"Edge(ymax={self.ymax}, x={self.x:.2f}, inv_slope={self.inv_slope:.2f})"

"""
    Algoritmo de preenchimento de polígonos por varredura (Scanline Fill).
    
    Estruturas de dados utilizadas:
    
    1. Edge Table (ET): Tabela de arestas indexada por ymin
       - Cada entrada y contém lista de arestas que começam em y
       - Ordenada por x (coordenada x inicial)
    
    2. Active Edge Table (AET): Lista de arestas ativas na linha de varredura atual
       - Contém apenas arestas que interceptam a scanline atual
       - Ordenada por coordenada x
       - Atualizada a cada linha varrida
"""



"""
    Funcoes de desenho(PyGame).
"""

def desenhar_tabuleiro(surface):
    for linha in range(LINHAS_GRADE):
        for col in range(COLUNAS_GRADE):
            x, y = grade_para_tela((col, linha))
            rect = pygame.Rect(x, y, TAMANHO_CELULA, TAMANHO_CELULA)
            cor = XADREZ_A if (linha + col) % 2 == 0 else XADREZ_B
            surface.fill(cor, rect)
    for c in range(COLUNAS_GRADE + 1):
        x = MARGEM + c * TAMANHO_CELULA
        pygame.draw.line(surface, LINHA_GRADE, (x, MARGEM), (x, MARGEM + LINHAS_GRADE * TAMANHO_CELULA), 1)
    for r in range(LINHAS_GRADE + 1):
        y = MARGEM + r * TAMANHO_CELULA
        pygame.draw.line(surface, LINHA_GRADE, (MARGEM, y), (MARGEM + COLUNAS_GRADE * TAMANHO_CELULA, y), 1)

def desenhar_vertices(surface, vertices, poligono_validado):
    if not vertices: return
    poligono_fechado_bool = len(vertices) >= 4 and vertices[0] == vertices[-1]
    for i, vertice in enumerate(vertices):
        vx, vy = centro_celula(vertice)
        if poligono_fechado_bool and i == len(vertices) - 1:
            continue
        if i == 0:
            pygame.draw.circle(surface, VERTICE_PRIMEIRO, (vx, vy), TAMANHO_CELULA // 3)
            if len(vertices) >= 3 and not poligono_fechado_bool:
                pygame.draw.circle(surface, VERTICE_PRIMEIRO, (vx, vy), TAMANHO_CELULA // 2, 2)
        elif i == len(vertices) - 1:
            pygame.draw.circle(surface, VERTICE_ATUAL, (vx, vy), TAMANHO_CELULA // 3)
        else:
            cor = PRETO if poligono_validado else VERTICE_ANTERIOR
            pygame.draw.circle(surface, cor, (vx, vy), TAMANHO_CELULA // 3)

def desenhar_linhas_preview(surface, vertices, poligono_validado):
    if len(vertices) < 2: return
    vertices_para_desenhar = vertices[:]
    poligono_fechado_bool = len(vertices) >= 4 and vertices[0] == vertices[-1]
    if poligono_fechado_bool: vertices_para_desenhar = vertices[:-1]
    cor = PRETO if poligono_validado else LINHA_PREVIEW
    for i in range(len(vertices_para_desenhar) - 1):
        p1_x, p1_y = centro_celula(vertices_para_desenhar[i])
        p2_x, p2_y = centro_celula(vertices_para_desenhar[i + 1])
        pygame.draw.line(surface, cor, (p1_x, p1_y), (p2_x, p2_y), 3)
    if poligono_fechado_bool and len(vertices_para_desenhar) >= 3:
        p1_x, p1_y = centro_celula(vertices_para_desenhar[-1])
        p2_x, p2_y = centro_celula(vertices_para_desenhar[0])
        pygame.draw.line(surface, cor, (p1_x, p1_y), (p2_x, p2_y), 3)

def desenhar_celulas_poligono(surface, pontos, passos_mostrados):
    for i, (col, linha) in enumerate(pontos[:passos_mostrados]):
        x, y = grade_para_tela((col, linha))
        rect = pygame.Rect(x + 2, y + 2, TAMANHO_CELULA - 4, TAMANHO_CELULA - 4)
        surface.fill(CELULA_POLIGONO, rect)

def desenhar_interceptos(surface, interceptos, passo_atual):
    if passo_atual >= len(interceptos): return
    y, xs = interceptos[passo_atual]
    y_tela = MARGEM + y * TAMANHO_CELULA
    pygame.draw.line(surface, (255, 0, 0), (MARGEM, y_tela + TAMANHO_CELULA // 2), (LARGURA_JANELA - MARGEM, y_tela + TAMANHO_CELULA // 2), 2)
    for x in xs:
        x_int = int(x)
        x_tela = MARGEM + x_int * TAMANHO_CELULA + TAMANHO_CELULA // 2
        pygame.draw.circle(surface, (0, 255, 0), (x_tela, y_tela + TAMANHO_CELULA // 2), 5)

def desenhar_hud(surface, font, vertices, poligono_validado, resultado_validacao, passos_mostrados, total_pontos):
    linhas = [
        "=== Algoritmo de Preenchimento de Polígonos ===",
        "Click: Adicionar vértice",
        "ENTER: Validar | SPACE: Limpar | BACKSPACE: Remover | ESC: Sair | N: Scanline",
        "",
    ]
    num_vertices = len(vertices)
    linhas.append(f"Vértices: {num_vertices}")
    if num_vertices > 0:
        linhas.append(f"Último vértice: {vertices[-1]}")
    if poligono_validado:
        linhas.append("Status: Polígono validado ✓ - Pronto para preenchimento")
    elif num_vertices >= 4 and vertices[0] == vertices[-1]:
        linhas.append("Status: Polígono fechado! Pressione ENTER para validar")
    elif num_vertices >= 3:
        linhas.append("Status: Clique no primeiro vértice para fechar, ou ENTER para validar")
    else:
        linhas.append("Status: Adicione mais vértices (mín. 3)")
    if resultado_validacao:
        linhas.append("")
        linhas.append("=== Resultado da Validação ===")
        linhas.append(resultado_validacao)
    if total_pontos > 0:
        linhas.append("")
        linhas.append(f"Pontos desenhados: {passos_mostrados}/{total_pontos}")
    if vertices:
        linhas.append("")
        linhas.append("=== Vértices do Polígono ===")
        for i, vertice in enumerate(vertices):
            cor_info = "🔴" if i == 0 else "🔵" if i == len(vertices) - 1 else "⚪"
            linhas.append(f"{cor_info} V{i+1}: {vertice}")
            if len(linhas) > 20: linhas.append("..."); break
    x, y = 16, 8
    for texto in linhas:
        cor = TEXTO_HUD
        if "===" in texto: cor = (0, 100, 200)
        elif "Status:" in texto:
            if "validado" in texto: cor = (0, 150, 0)
            elif "ENTER" in texto: cor = (200, 100, 0)
            else: cor = (150, 150, 0)
        elif "válido" in texto.lower():
            if "sem auto-interseção" in texto: cor = (0, 150, 0)
            else: cor = (200, 50, 50)
        elif texto.startswith("🔴") or texto.startswith("🔵") or texto.startswith("⚪"): cor = (100, 100, 100)
        surf = font.render(texto, True, cor)
        surface.blit(surf, (x, y))
        y += surf.get_height() + 2

class EstadoApp:
    def __init__(self):
        self.vertices: List[CelulaNaGrade] = []
        self.poligono_validado: bool = False
        self.pontos_raster: List[CelulaNaGrade] = []
        self.resultado_validacao: str = ""
        self.interceptos_scanline: List[Tuple[int, List[float]]] = []
        self.scanline_step: int = 0

    def limpar_raster(self):
        self.pontos_raster = []
        self.interceptos_scanline = []
        self.scanline_step = 0

    def adicionar_vertice(self, celula: CelulaNaGrade):
        if not self.poligono_validado:
            vertice_restrito = restringir_celula(celula)
            if len(self.vertices) >= 3 and vertice_restrito == self.vertices[0]:
                self.vertices.append(vertice_restrito)
                print("Polígono fechado automaticamente! Pressione ENTER para validar.")
                return
            if not self.vertices or self.vertices[-1] != vertice_restrito:
                self.vertices.append(vertice_restrito)

    def validar_e_desenhar_poligono(self):
        if len(self.vertices) >= 3:
            # Import here to avoid circular import
            from Main import poligono_e_valido
            eh_valido, mensagem = poligono_e_valido(self.vertices)
            self.resultado_validacao = mensagem
            print(f"\n{'='*50}")
            print(f"RESULTADO DA VALIDAÇÃO:")
            print(f"{'='*50}")
            print(f"Status: {'✓ VÁLIDO' if eh_valido else '✗ INVÁLIDO'}")
            print(f"Detalhes: {mensagem}")
            print(f"Vértices: {self.vertices}")
            print(f"{'='*50}\n")
            if eh_valido:
                self.poligono_validado = True
                self.interceptos_scanline = []
                self.scanline_step = 0
                self.pontos_raster = []
        else:
            self.resultado_validacao = "Adicione pelo menos 3 vértices antes de validar"
            print(f"\n{self.resultado_validacao}\n")

    def remover_ultimo_vertice(self):
        if self.vertices and not self.poligono_validado:
            self.vertices.pop()
            self.limpar_raster()

    def iniciar_preenchimento_scanline(self):
        if self.poligono_validado and not self.interceptos_scanline:
            # Import the algorithm functions from Main.py to avoid circular imports
            from Main import construir_tabela_arestas, algoritmo_preenchimento_scanline
            ET, ymin, ymax = construir_tabela_arestas(self.vertices)
            self.interceptos_scanline = algoritmo_preenchimento_scanline(ET, ymin, ymax)
            self.scanline_step = 0
            print(f"Algoritmo de preenchimento iniciado com {len(self.interceptos_scanline)} linhas de varredura.")

    def avancar_scanline(self):
        if not self.poligono_validado:
            return
        if self.scanline_step < len(self.interceptos_scanline):
            y, xs = self.interceptos_scanline[self.scanline_step]
            for i in range(0, len(xs), 2):
                if i + 1 < len(xs):
                    x_start = int(math.ceil(xs[i]))
                    x_end = int(math.floor(xs[i + 1]))
                    for x in range(x_start, x_end + 1):
                        self.pontos_raster.append((x, y))
            self.scanline_step += 1