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
    Funcoes para verificar se um poligono e valido.
"""
def checar_vertices_alinhados(vertices: List[CelulaNaGrade]) -> bool:
    """
    Verifica se os vértices estão alinhados (colineares).
    Retorna True se todos os vértices estão em linha reta (horizontal, vertical ou diagonal).
    """
    
    # Caso Reta-Horizontal: todos os vértices têm a mesma coordenada y
    if all(v[1] == vertices[0][1] for v in vertices):
        return True
    
    # Caso Reta-Vertical: todos os vértices têm a mesma coordenada x
    if all(v[0] == vertices[0][0] for v in vertices):
        return True
    
    # Caso Reta-Obliqua: verificar se todos os vértices têm a mesma inclinação
    # Usando o primeiro e segundo vértice como referência
    x1, y1 = vertices[0]
    x2, y2 = vertices[1]
    
    
    # Para cada vértice subsequente, verificar se está na mesma linha
    for i in range(2, len(vertices)):
        x3, y3 = vertices[i]
        
        # Usar produto cruzado para verificar colinearidade
        # Se (x2-x1)(y3-y1) - (y2-y1)(x3-x1) == 0, então os pontos são colineares
        produto_cruzado = (x2 - x1) * (y3 - y1) - (y2 - y1) * (x3 - x1)
        
        if produto_cruzado != 0:
            return False  # Não são colineares
    
    return True  # Todos os vértices são colineares 



def poligono_e_valido(vertices: List[CelulaNaGrade]) -> Tuple[bool, str]:
    """
    Valida se um polígono é válido para preenchimento.
    Aceita qualquer polígono fechado, incluindo com auto-interseções,
    pois o algoritmo de preenchimento pode lidar com eles.
    """
    
    # Remove vértices duplicados consecutivos
    vertices_limpos = []
    for i, vertice in enumerate(vertices):
        if i == 0 or vertice != vertices[i-1]:
            vertices_limpos.append(vertice)
    
    # Verifica se o polígono está fechado
    if vertices_limpos[0] != vertices_limpos[-1]:
        return False, "Polígono não está fechado (último vértice deve ser igual ao primeiro)"
    
    # Verifica se os vértices não estão todos alinhados (formando uma linha reta)
    if checar_vertices_alinhados(vertices_limpos):
        return False, "Polígono inválido: todos os vértices estão alinhados (formam uma linha reta)"
    
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
    Algoritmo de preenchimento por varredura (Scanline Fill Algorithm) - BOTTOM-UP.
    Implementa o Algoritmo 4.3 da apostila modificado para escaneamento de baixo para cima.
    
    Passos:
    1. Obtém a maior coordenada y armazenada na ET (começando de baixo)
    2. Inicializa AET como vazia
    3. Repita até que ET e AET estejam vazias:
       3.1. Transfere do cesto y na ET para AET as arestas cujo ymax = y (invertido)
       3.2. Retira os lados que possuem y = ymin (invertido) 
       3.3. Desenhe os pixels do bloco na linha de varredura y usando pares de coordenadas x da AET
       3.4. Decrementa y de 1 (escaneamento bottom-up)
       3.5. Para cada aresta não vertical que permanece na AET, atualiza x para o novo y (direção invertida)
       3.6. Como o passo anterior pode ter desordenado a AET, reordena a AET
    """
    
    # Reconstrói ET para bottom-up: indexa por ymax em vez de ymin
    ET_bottomup = {}
    for y_entry in ET:
        for edge in ET[y_entry]:
            ymax_edge = edge.ymax
            ymin_edge = y_entry
            
            # Para bottom-up, começamos em ymax com x_final
            if edge.inv_slope != 0:
                x_final = edge.x + edge.inv_slope * (ymax_edge - ymin_edge)
            else:
                x_final = edge.x
                
            # Cria nova entrada invertida
            edge_invertida = EdgeEntry(ymin_edge, x_final, -edge.inv_slope)
            
            if ymax_edge not in ET_bottomup:
                ET_bottomup[ymax_edge] = []
            ET_bottomup[ymax_edge].append(edge_invertida)
    
    # Ordena arestas por x em cada bucket da ET invertida
    for y in ET_bottomup:
        ET_bottomup[y].sort(key=lambda e: e.x)
    
    AET = []  # Active Edge Table (inicialmente vazia)
    y = ymax  # Linha de varredura atual (começando de baixo)
    resultados_scanline = []
    
    # Repita até que ET e AET estejam vazias
    while y >= ymin or AET:
        # 3.1. Transfere do cesto y na ET para AET as arestas cujo ymax = y
        if y in ET_bottomup:
            AET.extend(ET_bottomup[y])
            # Remove as arestas transferidas da ET (opcional, para economia de memória)
            del ET_bottomup[y]
        
        # 3.2. Retira os lados que possuem y = ymin (não mais envolvidos nesta linha)
        AET = [aresta for aresta in AET if aresta.ymax != y]
        
        # 3.6. Reordena AET por coordenada x
        AET.sort(key=lambda aresta: aresta.x)
        
        # 3.3. Coleta coordenadas x para desenho (pares de interceptos)
        interceptos_x = [aresta.x for aresta in AET]
        resultados_scanline.append((y, interceptos_x.copy()))
        
        # 3.4. Decrementa y de 1 (próxima linha de varredura - bottom-up)
        y -= 1
        
        # 3.5. Para cada aresta não vertical que permanece na AET, atualiza x para o novo y
        for aresta in AET:
            aresta.x += aresta.inv_slope  # inv_slope já foi invertido na construção
    
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
                    # Só permite validação com pelo menos 3 vértices distintos
                    vertices_distintos = []
                    for vertice in estado.vertices:
                        if vertice not in vertices_distintos:
                            vertices_distintos.append(vertice)
                    
                    if len(vertices_distintos) >= 3:
                        estado.validar_e_desenhar_poligono()
                    else:
                        estado.bloqueado_por_poucos_vertices = True
                        print(f"Polígono bloqueado: apenas {len(vertices_distintos)} vértices distintos encontrados (mínimo: 3). Use SPACE para limpar.")
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
        desenhar_hud(tela, fonte, estado.vertices, estado.poligono_validado, estado.resultado_validacao, len(estado.pontos_raster), len(estado.pontos_raster), estado.bloqueado_por_poucos_vertices)
        pygame.display.flip()
        relogio.tick(FPS)

    pygame.quit()

if __name__ == "__main__":
    main()
