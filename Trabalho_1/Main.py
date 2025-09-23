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

# Importando funcoes auxiliares, classes e constantes que deixamos em Aux.py.

from Aux import (
    EstadoApp, EdgeEntry, grade_para_tela, centro_celula, restringir_celula, tela_para_grade,
    desenhar_tabuleiro, desenhar_vertices, desenhar_linhas_preview, 
    desenhar_celulas_poligono, desenhar_interceptos, desenhar_hud,
    COLUNAS_GRADE, LINHAS_GRADE, TAMANHO_CELULA, MARGEM, LARGURA_JANELA, ALTURA_JANELA, FPS,
    BRANCO, PRETO, LINHA_GRADE, XADREZ_A, XADREZ_B, VERTICE_ATUAL, VERTICE_ANTERIOR,
    LINHA_TEMPORARIA, LINHA_PREVIEW, CELULA_POLIGONO, VERTICE_PRIMEIRO, TEXTO_HUD, CelulaNaGrade
)


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
    """
    Valida se um polígono é válido para preenchimento.
    Aceita qualquer polígono fechado, incluindo com auto-interseções,
    pois o algoritmo de preenchimento pode lidar com eles.
    """
    if len(vertices) < 3:
        return False, "Polígono precisa ter pelo menos 3 vértices"
    
    # Remove vértices duplicados consecutivos
    vertices_limpos = []
    for i, vertice in enumerate(vertices):
        if i == 0 or vertice != vertices[i-1]:
            vertices_limpos.append(vertice)
    
    if len(vertices_limpos) < 3:
        return False, "Polígono precisa ter pelo menos 3 vértices únicos"
    
    # Verifica se o polígono está fechado
    if vertices_limpos[0] != vertices_limpos[-1]:
        return False, "Polígono não está fechado (último vértice deve ser igual ao primeiro)"
    
    # Qualquer polígono fechado é válido para preenchimento
    # (incluindo auto-interseções, pois o algoritmo scanline pode lidar com eles)
    return True, "Polígono válido: fechado e pronto para preenchimento"


def construir_tabela_arestas(vertices: List[CelulaNaGrade]):
    """
    Constrói a Edge Table (ET) a partir dos vértices do polígono.
    Retorna: (ET, ymin, ymax)
    """
    ET = {}  # Edge Table
    n = len(vertices)
    
    # Inicializa limites y
    ymin_global = vertices[0][1]
    ymax_global = vertices[0][1]
    
    # Processa cada aresta do polígono
    for i in range(n):
        x1, y1 = vertices[i]
        x2, y2 = vertices[(i + 1) % n]
        
        # Ignora arestas horizontais
        if y1 == y2:
            continue
            
        # Determina ymin, ymax e x inicial
        if y1 < y2:
            ymin, ymax = y1, y2
            x_inicial = x1
        else:
            ymin, ymax = y2, y1
            x_inicial = x2
            
        # Calcula inverso da inclinação (1/m)
        if y2 != y1:
            inv_slope = (x2 - x1) / (y2 - y1)
        else:
            inv_slope = 0
            
        # Adiciona aresta à ET
        if ymin not in ET:
            ET[ymin] = []
        ET[ymin].append(EdgeEntry(ymax, x_inicial, inv_slope))
        
        # Atualiza limites globais
        ymin_global = min(ymin_global, ymin)
        ymax_global = max(ymax_global, ymax)
    
    # Ordena arestas por x em cada bucket da ET
    for y in ET:
        ET[y].sort(key=lambda e: e.x)
    
    return ET, ymin_global, ymax_global

def algoritmo_preenchimento_scanline(ET, ymin, ymax):
    """
    Algoritmo de preenchimento por varredura (Scanline Fill Algorithm).
    Implementa o Algoritmo 4.3 da apostila.
    
    Passos:
    1. Obtém a menor coordenada y armazenada na ET
    2. Inicializa AET como vazia
    3. Repita até que ET e AET estejam vazias:
       3.1. Transfere do cesto y na ET para AET as arestas cujo ymin = y
       3.2. Retira os lados que possuem y = ymax
       3.3. Desenhe os pixels do bloco na linha de varredura y usando pares de coordenadas x da AET
       3.4. Incremente y de 1
       3.5. Para cada aresta não vertical que permanece na AET, atualiza x para o novo y
       3.6. Como o passo anterior pode ter desordenado a AET, reordena a AET
    """
    AET = []  # Active Edge Table (inicialmente vazia)
    y = ymin  # Linha de varredura atual
    resultados_scanline = []
    
    # Repita até que ET e AET estejam vazias
    while y <= ymax or AET:
        # 3.1. Transfere do cesto y na ET para AET as arestas cujo ymin = y
        if y in ET:
            AET.extend(ET[y])
            # Remove as arestas transferidas da ET (opcional, para economia de memória)
            del ET[y]
        
        # 3.2. Retira os lados que possuem y = ymax (não mais envolvidos nesta linha)
        AET = [aresta for aresta in AET if aresta.ymax != y]
        
        # 3.6. Reordena AET por coordenada x
        AET.sort(key=lambda aresta: aresta.x)
        
        # 3.3. Coleta coordenadas x para desenho (pares de interceptos)
        interceptos_x = [aresta.x for aresta in AET]
        resultados_scanline.append((y, interceptos_x.copy()))
        
        # 3.4. Incremente y de 1 (próxima linha de varredura)
        y += 1
        
        # 3.5. Para cada aresta não vertical que permanece na AET, atualiza x para o novo y
        for aresta in AET:
            aresta.x += aresta.inv_slope
    
    return resultados_scanline


def main():
    pygame.init()
    tela = pygame.display.set_mode((LARGURA_JANELA, ALTURA_JANELA))
    pygame.display.set_caption("Algoritmo de Preenchimento de Polígonos - Scanline Fill")
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
