import sys
import math
import time
from typing import List, Optional, Tuple, Dict

import pygame


# ------------------------------
# Configurando Pygame
# ------------------------------
COLUNAS_GRADE: int = 20
LINHAS_GRADE: int = 20
TAMANHO_CELULA: int = 32
MARGEM: int = 32
LARGURA_JANELA: int = COLUNAS_GRADE * TAMANHO_CELULA + MARGEM * 2
ALTURA_JANELA: int = LINHAS_GRADE * TAMANHO_CELULA + MARGEM * 2
FPS: int = 60

# Cores
BRANCO = (240, 240, 240)
PRETO = (30, 30, 30)
LINHA_GRADE = (120, 120, 120)
XADREZ_A = (210, 210, 210)
XADREZ_B = (245, 245, 245)
PONTO_EXTREMO_A = (50, 140, 255)
PONTO_EXTREMO_B = (40, 200, 120)
LINHA_CONTINUA = (255, 210, 0)
CELULA_RASTER = (220, 60, 60)
TEXTO_HUD = (20, 20, 20)

CelulaNaGrade = Tuple[int, int]


def grade_para_tela(celula: CelulaNaGrade) -> Tuple[int, int]:
    """Converte coordenadas da grade para coordenadas da tela."""
    col, linha = celula
    x = MARGEM + col * TAMANHO_CELULA
    y = MARGEM + linha * TAMANHO_CELULA
    return x, y


def centro_celula(celula: CelulaNaGrade) -> Tuple[int, int]:
    """Retorna o centro da célula em coordenadas da tela."""
    x, y = grade_para_tela(celula)
    return x + TAMANHO_CELULA // 2, y + TAMANHO_CELULA // 2


def restringir_celula(celula: CelulaNaGrade) -> CelulaNaGrade:
    """Restringe a célula aos limites da grade."""
    col, linha = celula
    col = max(0, min(COLUNAS_GRADE - 1, col))
    linha = max(0, min(LINHAS_GRADE - 1, linha))
    return col, linha


def tela_para_grade(pos: Tuple[int, int]) -> Optional[CelulaNaGrade]:
    """Converte coordenadas da tela para coordenadas da grade."""
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


# ------------------------------
# Algoritmos de Rasterização de Circunferência
# ------------------------------

def circulo_seno_cosseno(centro: CelulaNaGrade, raio: int) -> Tuple[List[CelulaNaGrade], float, Dict[str, any]]:
    """
    Desenha círculo usando seno/cosseno - método trigonométrico melhorado.
    Retorna lista de pontos, tempo de execução e métricas detalhadas.
    Agora com verificação de limites e contagem correta.
    """
    tempo_inicio = time.perf_counter()
    
    cx, cy = centro
    pontos: List[CelulaNaGrade] = []
    
    # Melhor cálculo do número de pontos para círculo mais uniforme
    # Baseado no perímetro e densidade de pixels
    perimetro = 2 * math.pi * raio
    # Densidade adaptativa - mais pontos para raios maiores
    densidade = max(1.0, min(3.0, raio / 5.0))
    num_pontos_calculados = max(16, int(perimetro * densidade))
    
    # Usar conjunto para evitar duplicatas de forma mais eficiente
    pontos_set = set()
    
    for i in range(num_pontos_calculados):
        angulo = 2 * math.pi * i / num_pontos_calculados
        # Melhor arredondamento para posicionamento mais preciso
        x = cx + round(raio * math.cos(angulo))
        y = cy + round(raio * math.sin(angulo))
        
        # Verificar se o ponto está dentro dos limites da grade
        if 0 <= x < COLUNAS_GRADE and 0 <= y < LINHAS_GRADE:
            # Adicionar ao conjunto (automaticamente evita duplicatas)
            pontos_set.add((x, y))
    
    # Converter conjunto para lista ordenada por ângulo
    pontos = []
    for ponto in pontos_set:
        x, y = ponto
        angulo = math.atan2(y - cy, x - cx)
        pontos.append((ponto, angulo))
    
    # Ordenar por ângulo para melhor visualização
    pontos.sort(key=lambda item: item[1])
    pontos_finais = [ponto for ponto, _ in pontos]
    
    tempo_fim = time.perf_counter()
    tempo_execucao = tempo_fim - tempo_inicio
    
    # Métricas detalhadas - agora com contagem correta!
    metricas = {
        'pontos_calculados': num_pontos_calculados,  # Pontos que tentamos gerar
        'pontos_gerados': len(pontos_finais),        # Pontos únicos e válidos realmente gerados
        'perimetro_teorico': perimetro,
        'pontos_unicos': len(pontos_set)             # Confirmação (deve ser igual a pontos_gerados)
    }
    
    return pontos_finais, tempo_execucao, metricas



# ------------------------------
# Algoritmo de Bresenham
# ------------------------------

def circulo_bresenham(centro: CelulaNaGrade, raio: int) -> Tuple[List[CelulaNaGrade], float, Dict[str, any]]:
    """
    Desenha círculo usando algoritmo de Bresenham - método incremental.
    Agora com tratamento correto de duplicatas e verificação de limites.
    """
    tempo_inicio = time.perf_counter()
    
    cx, cy = centro
    pontos_set = set()  # Usar set para evitar duplicatas automaticamente
    
    # Valores iniciais
    x = 0
    y = raio
    d = 1 - raio  
    deltaE = 3
    deltaSE = -2 * raio + 5
    
    # Função auxiliar para adicionar os 8 pontos simétricos com verificação
    def adicionar_pontos_circulo(cx: int, cy: int, x: int, y: int) -> None:
        # Lista dos 8 pontos simétricos possíveis
        candidatos = [
            (cx + x, cy + y), (cx - x, cy + y),
            (cx + x, cy - y), (cx - x, cy - y),
            (cx + y, cy + x), (cx - y, cy + x),
            (cx + y, cy - x), (cx - y, cy - x)
        ]
        
        # Adicionar apenas pontos válidos (dentro dos limites da grade)
        for ponto in candidatos:
            px, py = ponto
            if 0 <= px < COLUNAS_GRADE and 0 <= py < LINHAS_GRADE:
                pontos_set.add(ponto)
    
    # Chamada inicial do CirclePoints
    adicionar_pontos_circulo(cx, cy, x, y)
    
    iteracoes = 0
    # Condição correta: x < y
    while x < y:
        iteracoes += 1
        
        if d < 0:                             # Selecionamos E
            d += deltaE
            deltaE += 2
            deltaSE += 2
        else:                                 # Selecionamos SE  
            d += deltaSE
            deltaE += 2
            deltaSE += 4
            y -= 1
            
        x += 1
        # CirclePoints chamado APÓS as atualizações
        adicionar_pontos_circulo(cx, cy, x, y)
    
    # Converter set para lista ordenada (para visualização consistente)
    pontos = []
    for ponto in pontos_set:
        px, py = ponto
        # Calcular ângulo para ordenação
        angulo = math.atan2(py - cy, px - cx)
        pontos.append((ponto, angulo))
    
    # Ordenar por ângulo para melhor visualização
    pontos.sort(key=lambda item: item[1])
    pontos_finais = [ponto for ponto, _ in pontos]
    
    tempo_fim = time.perf_counter()
    tempo_execucao = tempo_fim - tempo_inicio

    # Métricas detalhadas - agora com contagem correta!
    metricas = {
        'iteracoes': iteracoes,
        'pontos_gerados': len(pontos_finais),  # Contagem real sem duplicatas
        'pontos_unicos': len(pontos_set),      # Confirmação
    }
    
    return pontos_finais, tempo_execucao, metricas



# Funcao auxiliar para calcular o raio
def calcular_raio(centro: CelulaNaGrade, ponto: CelulaNaGrade) -> int:
    """Calcula o raio baseado na distância entre centro e ponto."""
    cx, cy = centro
    px, py = ponto
    return int(math.sqrt((px - cx) ** 2 + (py - cy) ** 2) + 0.5)










# ------------------------------
# Renderização
# ------------------------------

def desenhar_tabuleiro(surface: pygame.Surface) -> None:
    """Desenha o tabuleiro xadrez de fundo com linhas de grade."""
    for linha in range(LINHAS_GRADE):
        for col in range(COLUNAS_GRADE):
            x, y = grade_para_tela((col, linha))
            rect = pygame.Rect(x, y, TAMANHO_CELULA, TAMANHO_CELULA)
            cor = XADREZ_A if (linha + col) % 2 == 0 else XADREZ_B
            surface.fill(cor, rect)

    # Linhas da grade
    for c in range(COLUNAS_GRADE + 1):
        x = MARGEM + c * TAMANHO_CELULA
        pygame.draw.line(surface, LINHA_GRADE, (x, MARGEM), (x, MARGEM + LINHAS_GRADE * TAMANHO_CELULA), 1)
    for r in range(LINHAS_GRADE + 1):
        y = MARGEM + r * TAMANHO_CELULA
        pygame.draw.line(surface, LINHA_GRADE, (MARGEM, y), (MARGEM + COLUNAS_GRADE * TAMANHO_CELULA, y), 1)


def desenhar_pontos_extremos(surface: pygame.Surface, a: Optional[CelulaNaGrade], b: Optional[CelulaNaGrade]) -> None:
    """Desenha os pontos extremos (centro e ponto do raio)."""
    if a is not None:
        ax, ay = centro_celula(a)
        pygame.draw.circle(surface, PONTO_EXTREMO_A, (ax, ay), TAMANHO_CELULA // 3)
    if b is not None:
        bx, by = centro_celula(b)
        pygame.draw.circle(surface, PONTO_EXTREMO_B, (bx, by), TAMANHO_CELULA // 3)


def desenhar_circulo_continuo(surface: pygame.Surface, centro: CelulaNaGrade, raio: int) -> None:
    """Desenha círculo contínuo usando pygame para referência visual."""
    cx, cy = centro_celula(centro)
    pygame.draw.circle(surface, LINHA_CONTINUA, (cx, cy), raio * TAMANHO_CELULA, 2)


def desenhar_celulas_raster(surface: pygame.Surface, pontos: List[CelulaNaGrade], 
                          passos_mostrados: int) -> None:
    """Desenha as células rasterizadas."""
    for i, (col, linha) in enumerate(pontos[:passos_mostrados]):
        x, y = grade_para_tela((col, linha))
        rect = pygame.Rect(x + 2, y + 2, TAMANHO_CELULA - 4, TAMANHO_CELULA - 4)
        surface.fill(CELULA_RASTER, rect)


def desenhar_hud(surface: pygame.Surface, font: pygame.font.Font, centro: Optional[CelulaNaGrade], 
             ponto_raio: Optional[CelulaNaGrade], raio: int, algoritmo: str, 
             resultados_tempo: Dict[str, float], metricas: Dict[str, Dict[str, any]], 
             passos_mostrados: int, total_pontos: int) -> None:
    """Desenha a interface do usuário com métricas expandidas."""
    linhas = [
        "=== Comparação de Algoritmos de Circunferência ===",
        "Click: Centro -> Raio | ESPAÇO: Alternar Algoritmo | R: Reiniciar",
        "1-9: Raios pré-definidos | N: Próximo passo | ENTER: Todos os passos",
        "",
        f"Algoritmo Atual: {algoritmo}",
    ]
    
    if centro is not None:
        linhas.append(f"Centro: {centro}")
    if ponto_raio is not None:
        linhas.append(f"Ponto do Raio: {ponto_raio}")
    if raio > 0:
        linhas.append(f"Raio: {raio}")
    
    if total_pontos > 0:
        linhas.append(f"Pontos: {passos_mostrados}/{total_pontos}")
    
    # Resultados de tempo e métricas expandidas
    if resultados_tempo:
        linhas.append("")
        linhas.append("=== Análise de Performance ===")
        
        for alg, tempo_val in resultados_tempo.items():
            linhas.append(f"{alg}:")
            linhas.append(f"  Tempo: {tempo_val*1000:.3f}ms")
            
            if alg in metricas:
                m = metricas[alg]
                if alg == "Seno/Cosseno":
                    linhas.append(f"  Pontos únicos: {m['pontos_gerados']}")
                elif alg == "Bresenham":
                    linhas.append(f"  Pontos únicos: {m['pontos_gerados']}")
            linhas.append("")
        
        if len(resultados_tempo) == 2:
            tempos = list(resultados_tempo.values())
            if tempos[1] > 0:  # Evitar divisão por zero
                aceleracao = tempos[0] / tempos[1]
                alg_mais_rapido = min(resultados_tempo.keys(), key=lambda k: resultados_tempo[k])
                linhas.append(f"=== Comparação ===")
                linhas.append(f"Mais rápido: {alg_mais_rapido}")
                linhas.append(f"Aceleração: {aceleracao:.2f}x")
                
                # Comparação de qualidade
                if "Seno/Cosseno" in metricas and "Bresenham" in metricas:
                    seno_pontos = metricas["Seno/Cosseno"]["pontos_gerados"]
                    bres_pontos = metricas["Bresenham"]["pontos_gerados"]
                    linhas.append(f"Qualidade (pontos): S/C={seno_pontos}, B={bres_pontos}")

    x = 16
    y = 8
    for texto in linhas:
        cor = TEXTO_HUD
        if "===" in texto:
            cor = (0, 100, 200)  # Azul para títulos
        elif "Algoritmo Atual:" in texto:
            cor = (200, 100, 0)  # Laranja para algoritmo atual
        elif "Mais rápido:" in texto:
            cor = (0, 150, 0)    # Verde para resultado
        elif texto.startswith("  "):
            cor = (100, 100, 100)  # Cinza para sub-itens
            
        surf = font.render(texto, True, cor)
        surface.blit(surf, (x, y))
        y += surf.get_height() + 2


# ------------------------------
# Estado da Aplicação e Loop Principal
# ------------------------------

class EstadoApp:
    def __init__(self) -> None:
        self.centro: Optional[CelulaNaGrade] = None
        self.ponto_raio: Optional[CelulaNaGrade] = None
        self.raio: int = 0
        self.algoritmo_atual: str = "Seno/Cosseno"
        self.pontos_raster: List[CelulaNaGrade] = []
        self.passos_mostrados: int = 0
        self.resultados_tempo: Dict[str, float] = {}
        self.metricas_detalhadas: Dict[str, Dict[str, any]] = {}

    def limpar_raster(self) -> None:
        """Limpa todos os dados de rasterização."""
        self.pontos_raster = []
        self.passos_mostrados = 0

    def definir_centro(self, celula: CelulaNaGrade) -> None:
        """Define o centro do círculo."""
        self.centro = restringir_celula(celula)
        # Quando o centro muda, limpar ponto do raio e raster
        self.ponto_raio = None
        self.raio = 0
        self.limpar_raster()
        self.resultados_tempo.clear()
        self.metricas_detalhadas.clear()

    def definir_ponto_raio(self, celula: CelulaNaGrade) -> None:
        """Define o ponto que determina o raio."""
        self.ponto_raio = restringir_celula(celula)
        if self.centro is not None:
            self.raio = calcular_raio(self.centro, self.ponto_raio)
            self.recomputar_raster()

    def definir_raio(self, raio: int) -> None:
        """Define o raio diretamente."""
        self.raio = max(1, raio)
        self.ponto_raio = None  # Limpar ponto manual do raio
        if self.centro is not None:
            self.recomputar_raster()

    def alternar_algoritmo(self) -> None:
        """Alterna entre os algoritmos de rasterização."""
        if self.algoritmo_atual == "Seno/Cosseno":
            self.algoritmo_atual = "Bresenham"
        else:
            self.algoritmo_atual = "Seno/Cosseno"
        
        if self.centro is not None and self.raio > 0:
            self.recomputar_raster()

    def recomputar_raster(self) -> None:
        """Recomputa a rasterização do círculo."""
        self.limpar_raster()
        if self.centro is not None and self.raio > 0:
            # Executar ambos os algoritmos para comparação
            pontos_seno, tempo_seno, metricas_seno = circulo_seno_cosseno(self.centro, self.raio)
            pontos_bresenham, tempo_bresenham, metricas_bresenham = circulo_bresenham(self.centro, self.raio)
            
            # Armazenar tempos e métricas
            self.resultados_tempo = {
                "Seno/Cosseno": tempo_seno,
                "Bresenham": tempo_bresenham
            }
            
            self.metricas_detalhadas = {
                "Seno/Cosseno": metricas_seno,
                "Bresenham": metricas_bresenham
            }
            
            # Usar pontos do algoritmo atual
            if self.algoritmo_atual == "Seno/Cosseno":
                self.pontos_raster = pontos_seno
            else:
                self.pontos_raster = pontos_bresenham

    def proximo_passo(self) -> None:
        """Avança para o próximo passo na visualização."""
        if not self.pontos_raster and self.centro is not None and self.raio > 0:
            self.recomputar_raster()
        if self.passos_mostrados < len(self.pontos_raster):
            self.passos_mostrados += 1

    def executar_todos(self) -> None:
        """Executa todos os passos de uma vez."""
        if not self.pontos_raster and self.centro is not None and self.raio > 0:
            self.recomputar_raster()
        self.passos_mostrados = len(self.pontos_raster)

    def reiniciar(self) -> None:
        """Reinicia o estado da aplicação."""
        self.centro = None
        self.ponto_raio = None
        self.raio = 0
        self.limpar_raster()
        self.resultados_tempo.clear()
        self.metricas_detalhadas.clear()


def main() -> None:
    """Função principal da aplicação."""
    pygame.init()
    try:
        tela = pygame.display.set_mode((LARGURA_JANELA, ALTURA_JANELA))
    except Exception as exc:
        print(f"Erro ao criar a janela: {exc}")
        pygame.quit()
        sys.exit(1)

    pygame.display.set_caption("Comparação de Algoritmos de Circunferência - Análise de Performance")
    relogio = pygame.time.Clock()
    fonte = pygame.font.SysFont("consolas,monospace", 16)

    estado = EstadoApp()

    executando = True
    while executando:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                executando = False
            elif evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_ESCAPE:
                    executando = False
                elif evento.key == pygame.K_r:
                    estado.reiniciar()
                elif evento.key == pygame.K_c:
                    # Limpar apenas a rasterização (manter centro e raio)
                    estado.limpar_raster()
                elif evento.key == pygame.K_n:
                    estado.proximo_passo()
                elif evento.key == pygame.K_RETURN:
                    estado.executar_todos()
                elif evento.key == pygame.K_SPACE:
                    estado.alternar_algoritmo()
                # Raios pré-definidos (teclas 1-9)
                elif pygame.K_1 <= evento.key <= pygame.K_9:
                    raio = evento.key - pygame.K_0
                    if estado.centro is not None:
                        estado.definir_raio(raio)
            elif evento.type == pygame.MOUSEBUTTONDOWN:
                if evento.button == 1:  # Click esquerdo: definir centro, depois ponto do raio
                    celula = tela_para_grade(evento.pos)
                    if celula is not None:
                        if estado.centro is None:
                            estado.definir_centro(celula)
                        else:
                            estado.definir_ponto_raio(celula)
                elif evento.button == 3:  # Click direito: definir centro diretamente
                    celula = tela_para_grade(evento.pos)
                    if celula is not None:
                        estado.definir_centro(celula)

        tela.fill(BRANCO)
        desenhar_tabuleiro(tela)

        # Desenhar sobreposições do círculo se o centro estiver definido
        if estado.centro is not None:
            if estado.raio > 0:
                desenhar_circulo_continuo(tela, estado.centro, estado.raio)
            desenhar_pontos_extremos(tela, estado.centro, estado.ponto_raio)

        # Desenhar rasterização
        if estado.pontos_raster:
            desenhar_celulas_raster(tela, estado.pontos_raster, estado.passos_mostrados)

        desenhar_hud(
            tela,
            fonte,
            estado.centro,
            estado.ponto_raio,
            estado.raio,
            estado.algoritmo_atual,
            estado.resultados_tempo,
            estado.metricas_detalhadas,
            estado.passos_mostrados,
            len(estado.pontos_raster),
        )

        pygame.display.flip()
        relogio.tick(FPS)

    pygame.quit()


if __name__ == "__main__":
    main()
