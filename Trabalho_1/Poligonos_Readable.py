
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

# =============================================================================
# IMPORTAÇÃO DE BIBLIOTECAS
# =============================================================================

"""
PyGame é utilizado para criar uma interface gráfica interativa que permite:
- Visualização em tempo real do processo de construção de polígonos
- Interação com mouse e teclado para adicionar/remover vértices
- Demonstração visual do algoritmo de preenchimento scanline
- Exibição de informações de validação do polígono

Futuramente, podemos integrar com OpenGL para melhor performance
em problemas maiores de computação gráfica.
"""

import sys
import math
import pygame
from typing import List, Optional, Tuple


# =============================================================================
# CONSTANTES E CONFIGURAÇÕES DA APLICAÇÃO
# =============================================================================

# Dimensões da grade (matriz de células onde o usuário pode clicar)
COLUNAS_GRADE, LINHAS_GRADE = 60, 60

# Configurações visuais da interface
TAMANHO_CELULA = 20  # Tamanho de cada célula da grade em pixels
MARGEM = 32          # Margem ao redor da grade para o HUD e espaçamento

# Cálculo automático das dimensões da janela
LARGURA_JANELA = COLUNAS_GRADE * TAMANHO_CELULA + MARGEM * 2
ALTURA_JANELA = LINHAS_GRADE * TAMANHO_CELULA + MARGEM * 2
FPS = 60  # Taxa de atualização da tela (frames por segundo)

# =============================================================================
# PALETA DE CORES (RGB)
# =============================================================================

# Cores básicas
BRANCO = (240, 240, 240)
PRETO = (30, 30, 30)

# Elementos da grade
LINHA_GRADE = (120, 120, 120)      # Cor das linhas da grade
XADREZ_A = (210, 210, 210)         # Tom mais escuro do padrão xadrez
XADREZ_B = (245, 245, 245)         # Tom mais claro do padrão xadrez

# Elementos do polígono
VERTICE_ATUAL = (50, 140, 255)     # Azul - vértice sendo posicionado
VERTICE_ANTERIOR = (40, 200, 120)  # Verde - vértices já posicionados
VERTICE_PRIMEIRO = (255, 50, 50)   # Vermelho - primeiro vértice do polígono

# Estados das linhas
LINHA_TEMPORARIA = (255, 200, 0)   # Amarelo - linha temporária até o mouse
LINHA_PREVIEW = (0, 0, 0)          # Preto - linhas do polígono validado

# Preenchimento e interface
CELULA_POLIGONO = (220, 60, 60)    # Vermelho escuro - células preenchidas do polígono
TEXTO_HUD = (20, 20, 20)           # Cinza escuro - texto do painel informativo

# =============================================================================
# TIPOS PERSONALIZADOS
# =============================================================================

# Representa uma coordenada (coluna, linha) na grade
CelulaNaGrade = Tuple[int, int]

# =============================================================================
# FUNÇÕES UTILITÁRIAS - CONVERSÃO DE COORDENADAS
# =============================================================================

"""
Este módulo contém funções para converter coordenadas entre diferentes sistemas:

1. Sistema da Grade: coordenadas discretas (coluna, linha) da matriz de células
2. Sistema da Tela: coordenadas contínuas em pixels da janela PyGame

Essas conversões são essenciais para mapear cliques do mouse na tela
para posições na grade, e vice-versa.
"""

def grade_para_tela(celula: CelulaNaGrade) -> Tuple[int, int]:
    """
    Converte coordenadas da grade para coordenadas da tela (pixels).

    Args:
        celula: Tupla (coluna, linha) representando uma posição na grade

    Returns:
        Tupla (x, y) com as coordenadas em pixels na tela
    """
    col, linha = celula
    x = MARGEM + col * TAMANHO_CELULA
    y = MARGEM + linha * TAMANHO_CELULA
    return x, y

def centro_celula(celula: CelulaNaGrade) -> Tuple[int, int]:
    """
    Calcula o centro de uma célula da grade em coordenadas da tela.

    Args:
        celula: Tupla (coluna, linha) da célula

    Returns:
        Tupla (x, y) do centro da célula em pixels
    """
    x, y = grade_para_tela(celula)
    return x + TAMANHO_CELULA // 2, y + TAMANHO_CELULA // 2

def restringir_celula(celula: CelulaNaGrade) -> CelulaNaGrade:
    """
    Restringe uma coordenada da grade aos limites válidos da matriz.

    Args:
        celula: Tupla (coluna, linha) que pode estar fora dos limites

    Returns:
        Tupla (coluna, linha) garantidamente dentro dos limites da grade
    """
    col, linha = celula
    col = max(0, min(COLUNAS_GRADE - 1, col))
    linha = max(0, min(LINHAS_GRADE - 1, linha))
    return col, linha

def tela_para_grade(pos: Tuple[int, int]) -> Optional[CelulaNaGrade]:
    """
    Converte coordenadas da tela (pixels) para coordenadas da grade.

    Args:
        pos: Tupla (x, y) com posição em pixels na tela

    Returns:
        Tupla (coluna, linha) se a posição estiver dentro da grade, None caso contrário
    """
    x, y = pos
    x_rel = x - MARGEM  # Remove a margem esquerda
    y_rel = y - MARGEM  # Remove a margem superior

    # Verifica se o clique está dentro da área da grade
    if x_rel < 0 or y_rel < 0:
        return None

    # Converte pixels para índices da grade
    col = x_rel // TAMANHO_CELULA
    linha = y_rel // TAMANHO_CELULA

    # Verifica se os índices estão dentro dos limites da grade
    if 0 <= col < COLUNAS_GRADE and 0 <= linha < LINHAS_GRADE:
        return int(col), int(linha)
    return None

# =============================================================================
# ALGORITMO DE DETECÇÃO DE INTERSEÇÃO ENTRE SEGMENTOS
# =============================================================================

"""
Este módulo implementa o algoritmo matemático para detectar se dois segmentos de reta
se interceptam no plano cartesiano. É fundamental para validar se um polígono
possui auto-interseção (arestas que se cruzam).

O algoritmo utiliza o conceito de "orientação" dos pontos:
- Se três pontos são colineares: orientação = 0
- Se formam uma curva à esquerda: orientação = 1 (sentido anti-horário)
- Se formam uma curva à direita: orientação = 2 (sentido horário)

Dois segmentos se interceptam se:
1. Os pontos de cada segmento estiverem em lados opostos da reta do outro segmento
2. Ou se houver sobreposição/colinearidade entre os segmentos
"""

def segmentos_se_interceptam(p1, q1, p2, q2):
    """
    Verifica se dois segmentos de reta se interceptam.

    Args:
        p1, q1: Pontos extremos do primeiro segmento [(x1,y1), (x2,y2)]
        p2, q2: Pontos extremos do segundo segmento [(x3,y3), (x4,y4)]

    Returns:
        True se os segmentos se interceptam, False caso contrário

    Algoritmo:
    1. Calcula a orientação dos pontos para determinar posições relativas
    2. Verifica se os segmentos se cruzam (caso geral)
    3. Trata casos especiais de colinearidade e sobreposição
    """

    def orientacao(p, q, r):
        """
        Calcula a orientação de três pontos no plano.

        Args:
            p, q, r: Três pontos no plano cartesiano

        Returns:
            0: pontos colineares (na mesma reta)
            1: orientação anti-horária (esquerda)
            2: orientação horária (direita)
        """
        # Fórmula matemática: (q_y - p_y) * (r_x - q_x) - (q_x - p_x) * (r_y - q_y)
        # Resultado positivo = anti-horário, negativo = horário, zero = colinear
        val = (q[1] - p[1]) * (r[0] - q[0]) - (q[0] - p[0]) * (r[1] - q[1])
        if val == 0: return 0  # Colineares
        return 1 if val > 0 else 2  # 1 = esquerda, 2 = direita

    def ponto_no_segmento(p, q, r):
        """
        Verifica se o ponto q está sobre o segmento de reta definido por p e r.

        Args:
            p, r: Pontos extremos do segmento
            q: Ponto a ser testado

        Returns:
            True se q estiver sobre o segmento pr, False caso contrário
        """
        # Verifica se q está dentro da bounding box do segmento
        return (q[0] <= max(p[0], r[0]) and q[0] >= min(p[0], r[0]) and
                q[1] <= max(p[1], r[1]) and q[1] >= min(p[1], r[1]))

    # Calcula orientações dos pontos dos segmentos
    o1 = orientacao(p1, q1, p2)  # Orientação de p2 em relação ao segmento p1q1
    o2 = orientacao(p1, q1, q2)  # Orientação de q2 em relação ao segmento p1q1
    o3 = orientacao(p2, q2, p1)  # Orientação de p1 em relação ao segmento p2q2
    o4 = orientacao(p2, q2, q1)  # Orientação de q1 em relação ao segmento p2q2

    # Caso geral: segmentos se cruzam se os pontos estiverem em lados opostos
    if o1 != o2 and o3 != o4:
        return True

    # Casos especiais: tratamento de colinearidade e sobreposição
    if o1 == 0 and ponto_no_segmento(p1, p2, q1): return True  # p2 sobre p1q1
    if o2 == 0 and ponto_no_segmento(p1, q2, q1): return True  # q2 sobre p1q1
    if o3 == 0 and ponto_no_segmento(p2, p1, q2): return True  # p1 sobre p2q2
    if o4 == 0 and ponto_no_segmento(p2, q1, q2): return True  # q1 sobre p2q2

    return False

# =============================================================================
# VALIDAÇÃO DE POLÍGONOS
# =============================================================================

"""
Este módulo contém funções para validar se um conjunto de vértices forma um polígono válido.
Um polígono é considerado válido se:

1. Possui pelo menos 3 vértices (mínimo para formar uma forma fechada)
2. Não possui vértices duplicados consecutivos
3. Está fechado (último vértice igual ao primeiro)
4. Não possui auto-interseção (arestas não se cruzam)

A validação é crucial para garantir que o polígono pode ser preenchido
corretamente pelo algoritmo scanline sem ambiguidades.
"""

def poligono_e_valido(vertices: List[CelulaNaGrade]) -> Tuple[bool, str]:
    """
    Valida se um conjunto de vértices forma um polígono válido.

    Args:
        vertices: Lista de coordenadas (coluna, linha) dos vértices do polígono

    Returns:
        Tupla (válido, mensagem):
        - válido: True se o polígono é válido, False caso contrário
        - mensagem: Descrição detalhada do resultado da validação

    Critérios de validação:
    1. Mínimo de 3 vértices
    2. Sem vértices duplicados consecutivos
    3. Polígono fechado (último = primeiro vértice)
    4. Sem auto-interseção entre arestas
    """

    # =================================================================
    # VALIDAÇÃO 1: Número mínimo de vértices
    # =================================================================
    if len(vertices) < 3:
        return False, "❌ Polígono precisa ter pelo menos 3 vértices"

    # =================================================================
    # VALIDAÇÃO 2: Vértices duplicados consecutivos
    # =================================================================
    for i in range(len(vertices) - 1):
        if vertices[i] == vertices[i + 1]:
            return False, "❌ Polígono possui vértices duplicados consecutivos"

    # =================================================================
    # VALIDAÇÃO 3: Polígono fechado
    # =================================================================
    if vertices[0] != vertices[-1]:
        return False, "❌ Polígono não está fechado (último vértice deve ser igual ao primeiro)"

    # =================================================================
    # VALIDAÇÃO 4: Auto-interseção
    # =================================================================

    # Remove o último vértice duplicado para análise (polígono já validado como fechado)
    vertices_unicos = vertices[:-1]
    n = len(vertices_unicos)

    # Verifica todas as combinações de arestas para detectar interseções
    for i in range(n):
        for j in range(i + 2, n):
            # Pula a verificação da aresta que conecta o último ao primeiro vértice
            # quando i=0 e j=n-1 (essa aresta é adjacente e não pode se auto-intersetar)
            if (i == 0 and j == n - 1):
                continue

            # Define os pontos das duas arestas a serem comparadas
            p1, q1 = vertices_unicos[i], vertices_unicos[(i + 1) % n]  # Aresta i
            p2, q2 = vertices_unicos[j], vertices_unicos[(j + 1) % n]  # Aresta j

            # Verifica se as arestas se interceptam
            if segmentos_se_interceptam(p1, q1, p2, q2):
                return False, "❌ Polígono possui auto-interseção (linhas se cruzam)"

    # =================================================================
    # POLÍGONO VÁLIDO
    # =================================================================
    return True, "✅ Polígono válido: fechado e sem auto-interseção"

# =============================================================================
# ALGORITMO SCANLINE FILL - PREENCHIMENTO DE POLÍGONOS
# =============================================================================

"""
Este módulo implementa o algoritmo Scanline Fill, uma técnica clássica de
computação gráfica para preencher o interior de polígonos rasterizando linha por linha.

O algoritmo funciona em duas fases principais:

FASE 1: CONSTRUÇÃO DA TABELA DE ARESTAS (EDGE TABLE)
- Analisa todas as arestas do polígono
- Agrupa arestas por coordenada Y mínima
- Calcula inclinações e pontos de interseção

FASE 2: VARREDURA LINHA A LINHA (SCANLINE SWEEP)
- Processa cada linha Y da parte superior à inferior
- Mantém lista de arestas ativas que interceptam a linha atual
- Calcula intervalos de preenchimento entre interseções pares
"""

class Edge:
    """
    Representa uma aresta do polígono na tabela de arestas.

    Atributos:
        ymax: Coordenada Y máxima da aresta (ponto final)
        xmin: Coordenada X atual da aresta (atualizada durante varredura)
        inv_slope: Inverso da inclinação (1/m) para atualizar X durante varredura
    """
    def __init__(self, ymax, xmin, inv_slope):
        self.ymax = ymax          # Y máximo (limite superior da aresta)
        self.xmin = xmin          # X atual (atualizado durante scanline)
        self.inv_slope = inv_slope # Δx/Δy (usado para mover aresta)

def build_edge_table(vertices: List[CelulaNaGrade]):
    """
    Constrói a Edge Table (ET) organizando todas as arestas do polígono.

    Args:
        vertices: Lista de vértices do polígono (x, y)

    Returns:
        Tupla (ET, min_y, max_y):
        - ET: Dicionário onde chave=y_min e valor=lista de arestas
        - min_y, max_y: Limites Y do polígono para varredura

    Algoritmo:
    1. Para cada aresta do polígono (conectando vértices consecutivos)
    2. Calcula y_min, y_max, x_min inicial e inclinação
    3. Agrupa arestas por y_min na Edge Table
    4. Ordena arestas em cada nível Y por coordenada X
    """

    ET = {}  # Edge Table: {y_min: [lista_de_arestas]}
    n = len(vertices)

    # Inicializa limites Y com primeiro vértice
    min_y = vertices[0][1]
    max_y = vertices[0][1]

    # Processa cada aresta do polígono
    for i in range(n):
        x1, y1 = vertices[i]
        x2, y2 = vertices[(i + 1) % n]  # Próximo vértice (circular)

        # Pula arestas horizontais (não contribuem para preenchimento)
        if y1 == y2:
            continue

        # Calcula parâmetros da aresta
        ymin = min(y1, y2)          # Y mínimo da aresta
        ymax = max(y1, y2)          # Y máximo da aresta
        inv_slope = (x2 - x1) / (y2 - y1)  # Inclinação (Δx/Δy)
        xmin = x1 if y1 == ymin else x2    # X inicial (no ponto y_min)

        # Adiciona aresta à Edge Table
        if ymin not in ET:
            ET[ymin] = []
        ET[ymin].append(Edge(ymax, xmin, inv_slope))

        # Atualiza limites globais Y
        min_y = min(min_y, ymin)
        max_y = max(max_y, ymax)

    # Ordena arestas em cada nível Y por coordenada X (importante para scanline)
    for k in ET:
        ET[k].sort(key=lambda e: e.xmin)

    return ET, min_y, max_y

def scanline_fill(ET, min_y, max_y):
    """
    Executa o algoritmo scanline para calcular pontos de preenchimento.

    Args:
        ET: Edge Table com arestas organizadas por y_min
        min_y, max_y: Limites Y para varredura

    Returns:
        Lista de tuplas (y, [x_interseções]) para cada linha varrida

    Algoritmo:
    1. Para cada linha Y de min_y até max_y:
       a. Adiciona arestas que começam nesta linha (ET[y])
       b. Remove arestas que terminam nesta linha (ymax == y)
       c. Calcula interseções X ordenadas
       d. Registra interseções para preenchimento posterior
       e. Atualiza posições X das arestas ativas
    """

    AET = []  # Active Edge Table - arestas interceptando linha atual
    y = min_y
    scanline_results = []  # Resultados: [(y, [x1, x2, x3, ...]), ...]

    while y <= max_y:
        # 1. Adiciona arestas que começam nesta linha Y
        if y in ET:
            AET.extend(ET[y])  # Adiciona todas as arestas que começam em y

        # 2. Remove arestas que terminam nesta linha Y
        AET = [e for e in AET if e.ymax != y]

        # 3. Ordena arestas ativas por coordenada X atual
        AET.sort(key=lambda e: e.xmin)

        # 4. Extrai coordenadas X das interseções
        intercepts = [e.xmin for e in AET]

        # 5. Registra resultado desta linha para preenchimento posterior
        scanline_results.append((y, intercepts.copy()))

        # 6. Atualiza posições X das arestas ativas para próxima linha
        for e in AET:
            e.xmin += e.inv_slope  # Move aresta pela inclinação

        y += 1  # Próxima linha de varredura

    return scanline_results


# FUNÇÕES DE RENDERIZAÇÃO GRÁFICA (PYGAME)

def desenhar_tabuleiro(surface):
    # Preenche cada célula com cor alternada (padrão xadrez)
    for linha in range(LINHAS_GRADE):
        for col in range(COLUNAS_GRADE):
            x, y = grade_para_tela((col, linha))  # Converte coordenadas da grade
            rect = pygame.Rect(x, y, TAMANHO_CELULA, TAMANHO_CELULA)

            # Alterna cores baseado na soma linha + coluna (padrão xadrez)
            cor = XADREZ_A if (linha + col) % 2 == 0 else XADREZ_B
            surface.fill(cor, rect)

    # Desenha linhas verticais da grade
    for c in range(COLUNAS_GRADE + 1):
        x = MARGEM + c * TAMANHO_CELULA
        pygame.draw.line(surface, LINHA_GRADE,
                        (x, MARGEM),  # Ponto inicial
                        (x, MARGEM + LINHAS_GRADE * TAMANHO_CELULA),  # Ponto final
                        1)  # Espessura da linha

    # Desenha linhas horizontais da grade
    for r in range(LINHAS_GRADE + 1):
        y = MARGEM + r * TAMANHO_CELULA
        pygame.draw.line(surface, LINHA_GRADE,
                        (MARGEM, y),  # Ponto inicial
                        (MARGEM + COLUNAS_GRADE * TAMANHO_CELULA, y),  # Ponto final
                        1)  # Espessura da linha

def desenhar_vertices(surface, vertices, poligono_validado):
    if not vertices:
        return

    poligono_fechado = len(vertices) >= 4 and vertices[0] == vertices[-1]

    for i, vertice in enumerate(vertices):
        vx, vy = centro_celula(vertice)  # Centro da célula em pixels

        if poligono_fechado and i == len(vertices) - 1:
            continue

        if i == 0:
            pygame.draw.circle(surface, VERTICE_PRIMEIRO, (vx, vy), TAMANHO_CELULA // 3)

            if len(vertices) >= 3 and not poligono_fechado:
                pygame.draw.circle(surface, VERTICE_PRIMEIRO, (vx, vy), TAMANHO_CELULA // 2, 2)

        elif i == len(vertices) - 1:
            pygame.draw.circle(surface, VERTICE_ATUAL, (vx, vy), TAMANHO_CELULA // 3)

        else:
            cor = PRETO if poligono_validado else VERTICE_ANTERIOR
            pygame.draw.circle(surface, cor, (vx, vy), TAMANHO_CELULA // 3)

def desenhar_linhas_preview(surface, vertices, poligono_validado):
    if len(vertices) < 2:
        return  # Precisa de pelo menos 2 vértices para desenhar linha

    # Prepara lista de vértices para desenhar (remove duplicata se fechado)
    vertices_para_desenhar = vertices[:]
    poligono_fechado = len(vertices) >= 4 and vertices[0] == vertices[-1]

    if poligono_fechado:
        vertices_para_desenhar = vertices[:-1]  # Remove último vértice duplicado

    # Define cor das linhas baseada na validação
    cor = PRETO if poligono_validado else LINHA_PREVIEW

    # Conecta vértices consecutivos com linhas
    for i in range(len(vertices_para_desenhar) - 1):
        p1_x, p1_y = centro_celula(vertices_para_desenhar[i])     # Vértice atual
        p2_x, p2_y = centro_celula(vertices_para_desenhar[i + 1]) # Próximo vértice

        pygame.draw.line(surface, cor, (p1_x, p1_y), (p2_x, p2_y), 3)

    # Conecta último vértice de volta ao primeiro para fechar o polígono
    if poligono_fechado and len(vertices_para_desenhar) >= 3:
        p1_x, p1_y = centro_celula(vertices_para_desenhar[-1])  # Último vértice
        p2_x, p2_y = centro_celula(vertices_para_desenhar[0])   # Primeiro vértice

        pygame.draw.line(surface, cor, (p1_x, p1_y), (p2_x, p2_y), 3)

def desenhar_celulas_poligono(surface, pontos, passos_mostrados):
    """
    Desenha as células preenchidas do polígono durante a animação scanline.

    Args:
        surface: Superfície PyGame onde desenhar
        pontos: Lista de coordenadas (col, linha) das células a preencher
        passos_mostrados: Número de células a mostrar (para animação gradual)

    Visual:
    - Preenche células com cor vermelha escura
    - Animação progressiva mostra o preenchimento linha por linha
    - Margem interna evita sobrepor as linhas da grade
    """

    # Processa apenas as células até o passo atual da animação
    for i, (col, linha) in enumerate(pontos[:passos_mostrados]):
        x, y = grade_para_tela((col, linha))

        # Cria retângulo menor que a célula (margem de 2 pixels)
        # Evita sobrepor as linhas da grade
        rect = pygame.Rect(x + 2, y + 2, TAMANHO_CELULA - 4, TAMANHO_CELULA - 4)

        # Preenche com cor vermelha escura
        surface.fill(CELULA_POLIGONO, rect)

def desenhar_interceptos(surface, interceptos, passo_atual):
    if passo_atual >= len(interceptos):
        return

    # Obtém dados da linha atual sendo processada
    y, xs = interceptos[passo_atual]

    # Converte coordenada Y da grade para pixels na tela
    y_tela = MARGEM + y * TAMANHO_CELULA

    # Desenha linha vermelha horizontal marcando a scanline atual
    pygame.draw.line(surface, (255, 0, 0),  # Vermelho
                    (MARGEM, y_tela + TAMANHO_CELULA // 2),  # Centro vertical da linha
                    (LARGURA_JANELA - MARGEM, y_tela + TAMANHO_CELULA // 2),
                    2)  # Espessura da linha

    # =================================================================
    # DESENHO DOS PONTOS DE INTERSEÇÃO
    # =================================================================

    # Para cada interseção X na linha atual
    for x in xs:
        x_int = int(x)  # Converte para inteiro (posição da grade)
        x_tela = MARGEM + x_int * TAMANHO_CELULA + TAMANHO_CELULA // 2

        # Desenha círculo verde marcando o ponto de interseção
        pygame.draw.circle(surface, (0, 255, 0),  # Verde
                          (x_tela, y_tela + TAMANHO_CELULA // 2),
                          5)  # Raio do círculo

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
            # Emojis para identificar tipo do vértice
            if i == 0:
                cor_info = "🔴"  # Primeiro vértice
            elif i == len(vertices) - 1:
                cor_info = "🔵"  # Último vértice
            else:
                cor_info = "⚪"  # Vértices intermediários

            linhas.append(f"{cor_info} V{i+1}: {vertice}")

            # Limita o número de linhas para não sobrecarregar a tela
            if len(linhas) > 20:
                linhas.append("...")
                break

    x, y = 16, 8  # Posição inicial do texto

    for texto in linhas:
        # Define cor do texto baseada no conteúdo
        cor = TEXTO_HUD  # Cor padrão (cinza escuro)

        if "===" in texto:
            cor = (0, 100, 200)  # Azul para títulos de seção
        elif "Status:" in texto:
            if "validado" in texto:
                cor = (0, 150, 0)    # Verde para status válido
            elif "ENTER" in texto:
                cor = (200, 100, 0)  # Laranja para instruções
            else:
                cor = (150, 150, 0)  # Amarelo para outros status
        elif "válido" in texto.lower():
            if "sem auto-interseção" in texto:
                cor = (0, 150, 0)    # Verde para válido
            else:
                cor = (200, 50, 50)  # Vermelho para inválido
        elif texto.startswith("🔴") or texto.startswith("🔵") or texto.startswith("⚪"):
            cor = (100, 100, 100)  # Cinza para lista de vértices

        # Renderiza e desenha o texto
        surf = font.render(texto, True, cor)
        surface.blit(surf, (x, y))
        y += surf.get_height() + 2  # Próxima linha

class EstadoApp:
    def __init__(self):
        """Inicializa o estado da aplicação com valores padrão."""

        self.vertices: List[CelulaNaGrade] = []        
        self.poligono_validado: bool = False          
        self.resultado_validacao: str = ""           

        self.pontos_raster: List[CelulaNaGrade] = [] 
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
                # Limpa dados antigos para novo preenchimento
                self.interceptos_scanline = []
                self.scanline_step = 0
                self.pontos_raster = []
        else:
            self.resultado_validacao = "Adicione pelo menos 3 vértices antes de validar"
            print(f"\n{self.resultado_validacao}\n")

    def remover_ultimo_vertice(self):
        """
        Remove o último vértice adicionado ao polígono.

        Regras:
        - Só permite remoção se o polígono não foi validado
        - Limpa dados de rasterização após remoção
        """
        if self.vertices and not self.poligono_validado:
            self.vertices.pop()
            self.limpar_raster()

    def iniciar_preenchimento_scanline(self):
        if self.poligono_validado and not self.interceptos_scanline:
            ET, min_y, max_y = build_edge_table(self.vertices)
            self.interceptos_scanline = scanline_fill(ET, min_y, max_y)
            self.scanline_step = 0
            print(f"Preenchimento scanline iniciado com {len(self.interceptos_scanline)} linhas.")

    def avancar_scanline(self):
        if not self.poligono_validado:
            return

        if self.scanline_step < len(self.interceptos_scanline):
            y, xs = self.interceptos_scanline[self.scanline_step]

            # PREENCHIMENTO DOS INTERVALOS

            # Processa interseções em pares (x_início, x_fim)
            for i in range(0, len(xs), 2):
                if i + 1 < len(xs):
                    # Converte coordenadas float para inteiros
                    x_start = int(math.ceil(xs[i]))   # Arredonda para cima
                    x_end = int(math.floor(xs[i + 1])) # Arredonda para baixo

                    # Preenche todas as células no intervalo [x_start, x_end]
                    for x in range(x_start, x_end + 1):
                        self.pontos_raster.append((x, y))

            # Avança para próxima linha de varredura
            self.scanline_step += 1

def main():
    """
    Controles do usuário:
    - MOUSE: Clique esquerdo para adicionar vértices
    - ENTER: Validar polígono atual
    - SPACE: Limpar tudo e começar novo polígono
    - BACKSPACE: Remover último vértice
    - N: Iniciar/avançar preenchimento scanline
    - ESC: Sair da aplicação
    """

    # INICIALIZAÇÃO DO PYGAME

    pygame.init()
    tela = pygame.display.set_mode((LARGURA_JANELA, ALTURA_JANELA))
    pygame.display.set_caption("Validador de Polígonos - Verificação de Auto-Interseção")
    relogio = pygame.time.Clock()
    fonte = pygame.font.SysFont("consolas,monospace", 16)

    estado = EstadoApp()
    executando = True

    # LOOP PRINCIPAL

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
                if evento.button == 1:  # Clique esquerdo
                    celula = tela_para_grade(evento.pos)
                    if celula is not None:
                        estado.adicionar_vertice(celula)

        # Fundo branco
        tela.fill(BRANCO)

        desenhar_tabuleiro(tela)

        if estado.vertices:
            # Vértices coloridos por estado
            desenhar_vertices(tela, estado.vertices, estado.poligono_validado)

            # Linhas conectando vértices
            desenhar_linhas_preview(tela, estado.vertices, estado.poligono_validado)

            # Verifica se polígono está fechado
            poligono_fechado = (len(estado.vertices) >= 4 and estado.vertices[0] == estado.vertices[-1])

            # Preview da linha do mouse (só se não validado e não fechado)
            if not estado.poligono_validado and len(estado.vertices) > 0 and not poligono_fechado:
                pygame.draw.line(tela, LINHA_TEMPORARIA,
                               centro_celula(estado.vertices[-1]), pos_mouse, 2)

        # Células preenchidas do polígono (se validado)
        if estado.poligono_validado and estado.pontos_raster:
            desenhar_celulas_poligono(tela, estado.pontos_raster, len(estado.pontos_raster))

        # Visualização da linha de varredura atual
        if estado.interceptos_scanline and estado.scanline_step < len(estado.interceptos_scanline):
            desenhar_interceptos(tela, estado.interceptos_scanline, estado.scanline_step)

        desenhar_hud(tela, fonte, estado.vertices, estado.poligono_validado,
                    estado.resultado_validacao, len(estado.pontos_raster), len(estado.pontos_raster))

        pygame.display.flip()  
        relogio.tick(FPS)    

    pygame.quit()

if __name__ == "__main__":
    main()
