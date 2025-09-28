
import pygame
import math
from typing import List, Optional, Tuple

# Import constants from Main.py
# Note: This will create a circular import, so we'll define constants here instead
COLUNAS_GRADE, LINHAS_GRADE = 30, 30
TAMANHO_CELULA, MARGEM = 20, 32
MARGEM_ESQ = MARGEM * 13
LARGURA_JANELA = COLUNAS_GRADE * TAMANHO_CELULA + MARGEM + MARGEM_ESQ
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

BOTOES = [
        {"texto": "Limpar Tela",
         "rect": pygame.Rect(MARGEM, ALTURA_JANELA - 2*MARGEM, 120, 40),
         "acao": "limpar"},
        {"texto": "Scanline",
         "rect": pygame.Rect(MARGEM + 180, ALTURA_JANELA - 5*MARGEM, 120, 40),
         "acao": "scanline"},
        {"texto": "Validar",
         "rect": pygame.Rect(MARGEM, ALTURA_JANELA - 5*MARGEM, 120, 40),
         "acao": "validar"},
        {"texto": "Remover Último",
         "rect": pygame.Rect(MARGEM + 180, ALTURA_JANELA - 2*MARGEM, 180, 40),
         "acao": "remover"},
    ]

#------// Funcoes //------

"""
    Funcoes para converter coordenadas da grade para coordenadas da tela e vice-versa.
"""

def grade_para_tela(celula: CelulaNaGrade) -> Tuple[int, int]:
    col, linha = celula
    x = MARGEM_ESQ + col * TAMANHO_CELULA
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
    x_rel = x - MARGEM_ESQ
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
    Funcoes de desenho(PyGame).
"""

def desenhar_tabuleiro(surface):
    # Quadriculado
    for linha in range(LINHAS_GRADE):
        for col in range(COLUNAS_GRADE):
            x, y = grade_para_tela((col, linha))
            rect = pygame.Rect(x, y, TAMANHO_CELULA, TAMANHO_CELULA)
            cor = XADREZ_A if (linha + col) % 2 == 0 else XADREZ_B
            surface.fill(cor, rect)
    # Linhas verticais
    for c in range(COLUNAS_GRADE + 1):
        x = MARGEM_ESQ + c * TAMANHO_CELULA
        pygame.draw.line(surface, LINHA_GRADE, (x, MARGEM), (x, MARGEM + LINHAS_GRADE * TAMANHO_CELULA), 1)
    # Linhas horizontais
    for r in range(LINHAS_GRADE + 1):
        y = MARGEM + r * TAMANHO_CELULA
        pygame.draw.line(surface, LINHA_GRADE, (MARGEM_ESQ, y), (MARGEM_ESQ + COLUNAS_GRADE * TAMANHO_CELULA, y), 1)

def desenhar_botoes(surface,fonte,botoes):
    for botao in botoes:
        pygame.draw.rect(surface, (200,200,200) , botao["rect"], border_radius=6)
        pygame.draw.rect(surface, (50,50,50), botao["rect"], width=2, border_radius=6)
        texto_render = fonte.render(botao["texto"], True, PRETO)
        texto_rect = texto_render.get_rect(center=botao["rect"].center)
        surface.blit(texto_render, texto_rect)

def desenhar_vertices(surface, vertices, poligono_validado):
    if not vertices: return
    poligono_fechado_bool = len(vertices) >= 4 and vertices[0] == vertices[-1]
    for i, vertice in enumerate(vertices):
        vx, vy = centro_celula(vertice)
        if poligono_fechado_bool and i == len(vertices) - 1:
            continue
        # Vértices com cores diferentes
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

def desenhar_poligonos_finalizados(surface, poligonos_finalizados):
    """Desenha todos os polígonos já finalizados/validados"""
    for vertices_poligono, pontos_raster in poligonos_finalizados:
        # Desenha os vértices do polígono finalizado
        desenhar_vertices(surface, vertices_poligono, True)  # True = poligono_validado

        # Desenha as linhas do polígono finalizado
        desenhar_linhas_preview(surface, vertices_poligono, True)  # True = poligono_validado

        # Desenha o preenchimento se houver pontos raster
        if pontos_raster:
            desenhar_celulas_poligono(surface, pontos_raster, len(pontos_raster))

def desenhar_interceptos(surface, interceptos, passo_atual):
    if passo_atual >= len(interceptos): return
    y, xs = interceptos[passo_atual]
    y_tela = MARGEM + y * TAMANHO_CELULA
    pygame.draw.line(surface, (255, 0, 0), (MARGEM_ESQ, y_tela + TAMANHO_CELULA // 2), (LARGURA_JANELA - MARGEM, y_tela + TAMANHO_CELULA // 2), 2)
    for x in xs:
        x_int = int(x)
        x_tela = MARGEM_ESQ + x_int * TAMANHO_CELULA + TAMANHO_CELULA // 2
        pygame.draw.circle(surface, (0, 255, 0), (x_tela, y_tela + TAMANHO_CELULA // 2), 5)

def desenhar_hud(surface, font, vertices, poligono_validado, resultado_validacao, passos_mostrados, total_pontos, bloqueado_por_poucos_vertices=False, poligonos_finalizados=None):
    # Verifica se scanline está disponível
    tem_poligonos_para_scanline = poligono_validado or (poligonos_finalizados and len(poligonos_finalizados) > 0)
    scanline_texto = "N: Scanline GLOBAL" if tem_poligonos_para_scanline else "N: Scanline (indisponível)"

    linhas = [
        " ",
        "Algoritmo de Preenchimento de Polígonos",
        " ",
        "Click: Adicionar vértice",
        #"ENTER: Validar | SPACE: Limpar TUDO",
        #"BACKSPACE: Remover | ESC: Sair",
        #f"{scanline_texto}",
        "",
    ]

    # Adicionar informações sobre polígonos finalizados
    if poligonos_finalizados is not None and len(poligonos_finalizados) > 0:
        linhas.append(f"Polígonos finalizados: {len(poligonos_finalizados)}")
        linhas.append("")
    num_vertices = len(vertices)

    # Conta vértices distintos
    vertices_distintos = []
    for vertice in vertices:
        if vertice not in vertices_distintos:
            vertices_distintos.append(vertice)
    num_vertices_distintos = len(vertices_distintos)

    linhas.append(f"Vértices: {num_vertices} (distintos: {num_vertices_distintos})")
    if num_vertices > 0:
        linhas.append(f"Último vértice: {vertices[-1]}")

    if poligono_validado:
        linhas.insert(0,"Status: Polígono validado ✓ - Use 'N' para scanline ou clique para novo polígono")
    elif bloqueado_por_poucos_vertices:
        linhas.insert(0,"Status: BLOQUEADO - Poucos vértices distintos! Use SPACE para limpar")
    elif num_vertices_distintos < 3:
        linhas.insert(0,f"Status: Adicione mais vértices distintos (atual: {num_vertices_distintos}/3)")
    elif num_vertices >= 4 and vertices[0] == vertices[-1]:
        linhas.insert(0,"Status: Polígono fechado! Pressione ENTER para validar")
    elif num_vertices >= 3:
        linhas.insert(0,"Status: Clique no primeiro vértice para fechar, ou ENTER para validar")
    else:
        linhas.insert(2,"Status: Adicione mais vértices (mín. 3)")
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

    # Cores das mensagens na tela
    for texto in linhas:
        cor = TEXTO_HUD
        if "===" in texto or "Algoritmo" in texto: cor = (0, 100, 200) # azul claro
        elif "Status:" in texto:
            if "validado" in texto: cor = (0, 150, 0) # verde
            elif "BLOQUEADO" in texto: cor = (200, 0, 0) # vermelho
            elif "ENTER" in texto: cor = (200, 100, 0) # laranja
            else: cor = (150, 150, 0)
        elif "válido" in texto.lower(): cor = (200, 50, 50)
            #if "sem auto-interseção" in texto: cor = (0, 150, 0)
            #else: cor = (200, 50, 50)
        elif texto.startswith("🔴") or texto.startswith("🔵") or texto.startswith("⚪"): cor = (100, 100, 100)
        surf = font.render(texto, True, cor)
        surface.blit(surf, (x, y))
        y += surf.get_height() + 2

class EstadoApp:
    def __init__(self):
        # Polígono atual sendo desenhado
        self.vertices: List[CelulaNaGrade] = []
        self.poligono_validado: bool = False
        self.pontos_raster: List[CelulaNaGrade] = []
        self.resultado_validacao: str = ""
        self.interceptos_scanline: List[Tuple[int, List[float]]] = []
        self.scanline_step: int = 0
        self.bloqueado_por_poucos_vertices: bool = False

        # Lista de polígonos finalizados (cada um com seus vértices e pontos raster)
        self.poligonos_finalizados: List[Tuple[List[CelulaNaGrade], List[CelulaNaGrade]]] = []

    def limpar_raster(self):
        self.pontos_raster = []
        self.interceptos_scanline = []
        self.scanline_step = 0
        self.bloqueado_por_poucos_vertices = False

    def adicionar_vertice(self, celula: CelulaNaGrade):
        # Se há um polígono validado e vamos começar um novo, finaliza o anterior
        if self.poligono_validado and len(self.vertices) > 0:
            print("Finalizando polígono anterior e começando novo...")
            self.finalizar_poligono()

        if not self.poligono_validado:
            # Desbloqueia automaticamente quando tentar adicionar vértice
            if self.bloqueado_por_poucos_vertices:
                self.bloqueado_por_poucos_vertices = False
                print("Desbloqueado! Continuando a desenhar polígono...")

            vertice_restrito = restringir_celula(celula)
            if len(self.vertices) >= 3 and vertice_restrito == self.vertices[0]:
                self.vertices.append(vertice_restrito)
                print("Polígono fechado! Pressione ENTER para validar.")
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
                print("Polígono validado! Agora você pode usar 'N' para scanline ou começar um novo polígono.")
        else:
            self.resultado_validacao = "Adicione pelo menos 3 vértices antes de validar"
            print(f"\n{self.resultado_validacao}\n")

    def finalizar_poligono(self):
        """Finaliza o polígono atual e prepara para desenhar um novo"""
        if self.poligono_validado:
            # Salva o polígono atual na lista de finalizados (com pontos raster vazios inicialmente)
            self.poligonos_finalizados.append((self.vertices.copy(), []))

            # Reset do estado para um novo polígono
            self.vertices = []
            self.poligono_validado = False
            self.pontos_raster = []
            self.resultado_validacao = ""
            self.interceptos_scanline = []
            self.scanline_step = 0
            self.bloqueado_por_poucos_vertices = False

            print(f"Novo polígono pronto! Total de polígonos finalizados: {len(self.poligonos_finalizados)}")

    def limpar_tudo(self):
        """Limpa polígono atual e todos os finalizados"""
        self.vertices = []
        self.poligono_validado = False
        self.pontos_raster = []
        self.resultado_validacao = ""
        self.interceptos_scanline = []
        self.scanline_step = 0
        self.blqueado_por_poucos_vertices = False
        self.poligonos_finalizados = []
        print("Todos os polígonos foram limpos!")

    def remover_ultimo_vertice(self):
        if self.vertices and not self.poligono_validado:
            self.vertices.pop()
            self.limpar_raster()

    def iniciar_preenchimento_scanline(self):
        if not self.interceptos_scanline:
            # Import the algorithm functions from Main.py to avoid circular imports
            from Main import construir_tabela_arestas, algoritmo_preenchimento_scanline

            # Coleta todos os polígonos (finalizados + atual se validado)
            todos_poligonos = []

            # Adiciona polígonos finalizados
            for vertices_poligono, _ in self.poligonos_finalizados:
                todos_poligonos.append(vertices_poligono)

            # Adiciona polígono atual se validado
            if self.poligono_validado and len(self.vertices) > 0:
                todos_poligonos.append(self.vertices)

            if not todos_poligonos:
                print("Nenhum polígono validado encontrado para scanline.")
                return

            # Constrói tabela de arestas global e encontra limites globais
            ET_global = {}
            ymin_global = float('inf')
            ymax_global = float('-inf')

            for vertices in todos_poligonos:
                ET, ymin, ymax = construir_tabela_arestas(vertices)

                # Atualiza limites globais
                ymin_global = min(ymin_global, ymin)
                ymax_global = max(ymax_global, ymax)

                # Combina ET deste polígono com ET global
                for y_bucket in ET:
                    if y_bucket not in ET_global:
                        ET_global[y_bucket] = []
                    ET_global[y_bucket].extend(ET[y_bucket])

            # Ordena arestas por x em cada bucket da ET global
            for y in ET_global:
                ET_global[y].sort(key=lambda e: e.x)

            self.interceptos_scanline = algoritmo_preenchimento_scanline(ET_global, ymin_global, ymax_global)
            self.scanline_step = 0
            print(f"Algoritmo de preenchimento iniciado para {len(todos_poligonos)} polígono(s) com {len(self.interceptos_scanline)} linhas de varredura.")
            print(f"Limites Y: {ymin_global} até {ymax_global}")

    def avancar_scanline(self):
        # Permite scanline se há polígono atual validado OU polígonos finalizados
        if not self.poligono_validado and not self.poligonos_finalizados:
            return
        if self.scanline_step < len(self.interceptos_scanline):
            y, xs = self.interceptos_scanline[self.scanline_step]
            for i in range(0, len(xs), 2):
                if i + 1 < len(xs):
                    x_start = int(math.ceil(xs[i]))
                    x_end = int(math.floor(xs[i + 1]))
                    for x in range(x_start, x_end):
                        self.pontos_raster.append((x, y))
            self.scanline_step += 1
