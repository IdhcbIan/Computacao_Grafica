
"""
╭━━━━╮╭╮╱╱╱╱╱╭━━━╮╱╱╱╱╱╱╱╱╱╱╱╱╱╭╮╱╱╱╱╱╱╱╱╱╱╱╭╮╱╱╱╱╱╱╭╮╱╱╱╭━━━╮╱╱╭╮
┃╭╮╭╮┣╯┃╱╱╱╱╱┃╭━╮┃╱╱╱╱╱╱╱╱╱╱╱╱╱┃┃╱╱╱╱╱╱╱╱╱╱╭╯╰╮╱╱╱╱╱┃┃╱╱╱┃╭━╮┃╱╱┃┃
╰╯┃┃╰┻╮┃╱╱╱╱╱┃╰━╯┣━┳━━┳━━┳━╮╭━━┫╰━┳┳╮╭┳━━┳━╋╮╭╋━━╮╭━╯┣━━╮┃╰━╯┣━━┫┃╭┳━━┳━━┳━╮╭━━┳━━╮
╱╱┃┃╱╱┃┃╱╭━━╮┃╭━━┫╭┫┃━┫┃━┫╭╮┫╭━┫╭╮┣┫╰╯┃┃━┫╭╮┫┃┃╭╮┃┃╭╮┃┃━┫┃╭━━┫╭╮┃┃┣┫╭╮┃╭╮┃╭╮┫╭╮┃━━┫
╱╱┃┃╱╭╯╰╮╰━━╯┃┃╱╱┃┃┃┃━┫┃━┫┃┃┃╰━┫┃┃┃┃┃┃┃┃━┫┃┃┃╰┫╰╯┃┃╰╯┃┃━┫┃┃╱╱┃╰╯┃╰┫┃╰╯┃╰╯┃┃┃┃╰╯┣━━┃
╱╱╰╯╱╰━━╯╱╱╱╱╰╯╱╱╰╯╰━━┻━━┻╯╰┻━━┻╯╰┻┻┻┻┻━━┻╯╰┻━┻━━╯╰━━┻━━╯╰╯╱╱╰━━┻━┻┻━╮┣━━┻╯╰┻━━┻━━╯
╱╱╱╱╱╱╱╱╱╱╱╱╱╱╱╱╱╱╱╱╱╱╱╱╱╱╱╱╱╱╱╱╱╱╱╱╱╱╱╱╱╱╱╱╱╱╱╱╱╱╱╱╱╱╱╱╱╱╱╱╱╱╱╱╱╱╱╭━╯┃
----------------------------------------------------------------

Ian de Holanda Cavalcanti Bezerra - 13835412
Julia Graziosi Ortiz - 11797810

"""

#------// Importando bibliotecas //------

"""
     Usamos PyGame para a visualizacao interativa do processo 
de desenho de poligonos. Futuramente podemos integrar pygame com kernels de OpenGl para a melhor
performance em problemas de computacao grafica maiores.
"""

import sys
import math
import pygame
from typing import List, Optional, Tuple


#------// Constantes //------

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
    y = ALTURA_JANELA - (MARGEM - linha * TAMANHO_CELULA)
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
    linha = LINHAS_GRADE - (y_rel // TAMANHO_CELULA)
    if 0 <= col < COLUNAS_GRADE and 0 <= linha < LINHAS_GRADE:
        return int(col), int(linha)
    return None

"""
    Funcoes para verificar se dois segmentos se interceptam.
"""

def segmentos_se_interceptam(p1, q1, p2, q2):
    def orientacao(p, q, r):
        val = (q[1] - p[1]) * (r[0] - q[0]) - (q[0] - p[0]) * (r[1] - q[1])
        if val == 0: return 0
        return 1 if val > 0 else 2
    def ponto_no_segmento(p, q, r):
        return (q[0] <= max(p[0], r[0]) and q[0] >= min(p[0], r[0]) and
                q[1] <= max(p[1], r[1]) and q[1] >= min(p[1], r[1]))
    o1, o2 = orientacao(p1, q1, p2), orientacao(p1, q1, q2)
    o3, o4 = orientacao(p2, q2, p1), orientacao(p2, q2, q1)
    if o1 != o2 and o3 != o4: return True
    if o1 == 0 and ponto_no_segmento(p1, p2, q1): return True
    if o2 == 0 and ponto_no_segmento(p1, q2, q1): return True
    if o3 == 0 and ponto_no_segmento(p2, p1, q2): return True
    if o4 == 0 and ponto_no_segmento(p2, q1, q2): return True
    return False

"""
    Funcoes para verificar se um poligono e valido.
"""

def poligono_e_valido(vertices: List[CelulaNaGrade]) -> Tuple[bool, str]:
    if len(vertices) < 3:
        return False, "Polígono precisa ter pelo menos 3 vértices"
    for i in range(len(vertices) - 1):
        if vertices[i] == vertices[i + 1]:
            return False, "Polígono possui vértices duplicados consecutivos"
    if vertices[0] != vertices[-1]:
        return False, "Polígono não está fechado (último vértice deve ser igual ao primeiro)"
    vertices_unicos = vertices[:-1]
    n = len(vertices_unicos)
    for i in range(n):
        for j in range(i + 2, n):
            if (i == 0 and j == n - 1):
                continue
            p1, q1 = vertices_unicos[i], vertices_unicos[(i + 1) % n]
            p2, q2 = vertices_unicos[j], vertices_unicos[(j + 1) % n]
            if segmentos_se_interceptam(p1, q1, p2, q2):
                return False, "Polígono possui auto-interseção (linhas se cruzam)"
    return True, "Polígono válido: fechado e sem auto-interseção"

"""
    Classe para representar uma aresta da tabela de arestas.
"""

class Edge:
    def __init__(self, ymax, xmin, inv_slope):
        self.ymax = ymax
        self.xmin = xmin
        self.inv_slope = inv_slope

"""
    Neste codigo usamos duas extruturas de dados.

    1. Edge Table (ET): Armazena as arestas do polígono ordenadas por y_min.
       Cada entrada contém:
       - y_max: coordenada y máxima da aresta
       - x_min: coordenada x mínima da aresta 
       - inv_slope: inverso da inclinação (1/m)

    2. Active Edge Table (AET): Lista de arestas ativas na linha de varredura atual.
       Mantém apenas as arestas que interceptam a scanline.
       Atualizada a cada nova linha varrida.

"""

def build_edge_table(vertices: List[CelulaNaGrade]):
    ET = {}
    n = len(vertices)
    min_y = vertices[0][1]
    max_y = vertices[0][1]
    for i in range(n):
        x1, y1 = vertices[i]
        x2, y2 = vertices[(i + 1) % n]
        if y1 == y2: continue
        ymin = min(y1, y2)
        ymax = max(y1, y2)
        inv_slope = (x2 - x1) / (y2 - y1)
        xmin = x1 if y1 == ymin else x2
        if ymin not in ET: ET[ymin] = []
        ET[ymin].append(Edge(ymax, xmin, inv_slope))
        min_y = min(min_y, ymin)
        max_y = max(max_y, ymax)
    for k in ET: ET[k].sort(key=lambda e: e.xmin)
    return ET, min_y, max_y

def scanline_fill(ET, min_y, max_y):
    AET = []
    y = min_y
    scanline_results = []
    while y <= max_y:
        if y in ET:
            AET.extend(ET[y])
        AET = [e for e in AET if e.ymax != y]
        AET.sort(key=lambda e: e.xmin)
        intercepts = [e.xmin for e in AET]
        scanline_results.append((y, intercepts.copy()))
        for e in AET:
            e.xmin += e.inv_slope
        y += 1
    return scanline_results






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
    y_tela = ALTURA_JANELA - (MARGEM - y * TAMANHO_CELULA)
    pygame.draw.line(surface, (255, 0, 0), (MARGEM, y_tela + TAMANHO_CELULA // 2), (LARGURA_JANELA - MARGEM, y_tela + TAMANHO_CELULA // 2), 2)
    for x in xs:
        x_int = int(x)
        x_tela = MARGEM + x_int * TAMANHO_CELULA + TAMANHO_CELULA // 2
        pygame.draw.circle(surface, (0, 255, 0), (x_tela, y_tela + TAMANHO_CELULA // 2), 5)

def desenhar_hud(surface, font, vertices, poligono_validado, resultado_validacao, passos_mostrados, total_pontos):
    linhas = [
        "=== Validador de Polígonos ===",
        "Click: Adicionar vértice",
        "ENTER: Validar | SPACE: Limpar | BACKSPACE: Remover | ESC: Sair | N: Scanline",
        "",
    ]
    num_vertices = len(vertices)
    linhas.append(f"Vértices: {num_vertices}")
    if num_vertices > 0:
        linhas.append(f"Último vértice: {vertices[-1]}")
    if poligono_validado:
        linhas.append("Status: Polígono validado ✓")
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
            ET, min_y, max_y = build_edge_table(self.vertices)
            self.interceptos_scanline = scanline_fill(ET, min_y, max_y)
            self.scanline_step = 0
            print(f"Scanline filling started with {len(self.interceptos_scanline)} lines.")

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

def main():
    pygame.init()
    tela = pygame.display.set_mode((LARGURA_JANELA, ALTURA_JANELA))
    pygame.display.set_caption("Validador de Polígonos - Verificação de Auto-Interseção")
    relogio = pygame.time.Clock()
    fonte = pygame.font.SysFont("consolas,monospace", 16)
    estado = EstadoApp()
    executando = True

    while executando:
        pos_mouse = pygame.mouse.get_pos()
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                executando = False
            elif evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_ESCAPE:
                    executando = False
                elif evento.key == pygame.K_SPACE:
                    estado.vertices = []
                    estado.poligono_validado = False
                    estado.resultado_validacao = ""
                    estado.limpar_raster()
                elif evento.key == pygame.K_n:
                    if not estado.interceptos_scanline:
                        estado.iniciar_preenchimento_scanline()
                    else:
                        estado.avancar_scanline()
                elif evento.key == pygame.K_RETURN:
                    estado.validar_e_desenhar_poligono()
                elif evento.key == pygame.K_BACKSPACE:
                    estado.remover_ultimo_vertice()
            elif evento.type == pygame.MOUSEBUTTONDOWN:
                if evento.button == 1:
                    celula = tela_para_grade(evento.pos)
                    if celula is not None:
                        estado.adicionar_vertice(celula)

        tela.fill(BRANCO)
        desenhar_tabuleiro(tela)
        if estado.vertices:
            desenhar_vertices(tela, estado.vertices, estado.poligono_validado)
            desenhar_linhas_preview(tela, estado.vertices, estado.poligono_validado)
            poligono_fechado_bool = (len(estado.vertices) >= 4 and estado.vertices[0] == estado.vertices[-1])
            if not estado.poligono_validado and len(estado.vertices) > 0 and not poligono_fechado_bool:
                pygame.draw.line(tela, LINHA_TEMPORARIA, centro_celula(estado.vertices[-1]), pos_mouse, 2)
        if estado.poligono_validado and estado.pontos_raster:
            desenhar_celulas_poligono(tela, estado.pontos_raster, len(estado.pontos_raster))
        if estado.interceptos_scanline and estado.scanline_step < len(estado.interceptos_scanline):
            desenhar_interceptos(tela, estado.interceptos_scanline, estado.scanline_step)
        desenhar_hud(tela, fonte, estado.vertices, estado.poligono_validado, estado.resultado_validacao, len(estado.pontos_raster), len(estado.pontos_raster))
        pygame.display.flip()
        relogio.tick(FPS)

    pygame.quit()

if __name__ == "__main__":
    main()
