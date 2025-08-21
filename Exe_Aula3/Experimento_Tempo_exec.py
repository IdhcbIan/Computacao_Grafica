# Oi Julia!!


"""

 Vamos primeiro importar copiar as duas funcoes que criamos no codigo anterior...

 Mas vamos desta vez inserir os pontos nao no Pygame mas sim em um array de NUMPY.

 Queremos apenas comparar o tempo de cauculo dos dois algoritmos, nao o tempo do Pygame

  Usamos o comando abaixo para executar o codigo com prioridade mais alta para reduzir 
      interferencias de outros processos em CPU!! Conseguimos graficos limpos com isso!!
      Tambem rodamos cada plot 100 veses para ter uma media mais precisa!!


    sudo nice -n -20 python3 Experimento_Tempo_exec.py 

 """

# Vamos importar as bibliotecas necessárias
import numpy as np
import time
import math
import matplotlib.pyplot as plt
from typing import List, Tuple, Dict

size = 10000
tabuleiro = np.zeros((size, size))   # Temos um tabuleiro!!

# Vamos definir as dimensões da grade baseado no tamanho do tabuleiro(melhor do que mudar todas as vars do codigo passado)
LINHAS_GRADE = size
COLUNAS_GRADE = size

# Vamos criar um tipo para uma coordenada na grade
CelulaNaGrade = Tuple[int, int]

# ------------------------------
# Algoritmo de Seno/Cosseno
# ------------------------------


def circulo_seno_cosseno(centro: CelulaNaGrade, raio, tabuleiro) -> Tuple[List[CelulaNaGrade], float, Dict[str, any]]:
    """
    Desenha círculo usando seno/cosseno - método trigonométrico melhorado.
    Marca os pontos no tabuleiro numpy e retorna lista de pontos, tempo de execução e métricas detalhadas.
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
            # Marcar ponto no tabuleiro
            tabuleiro[y, x] = 1
    
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
    
    return pontos_finais, tempo_execucao, metricas, tabuleiro

# ------------------------------
# Algoritmo de Bresenham
# ------------------------------

def circulo_bresenham(centro: CelulaNaGrade, raio, tabuleiro) -> Tuple[List[CelulaNaGrade], float, Dict[str, any]]:
    """
    Desenha círculo usando algoritmo de Bresenham - método incremental.
    Marca os pontos no tabuleiro numpy e retorna lista de pontos, tempo de execução e métricas.
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
                # Marcar ponto no tabuleiro
                tabuleiro[py, px] = 1
    
    # Chamada inicial do CirclePoints
    adicionar_pontos_circulo(cx, cy, x, y)
    
    iteracoes = 0
    # Condição.
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
    
    return pontos_finais, tempo_execucao, metricas, tabuleiro


# ------------------------------
# Função auxiliar para limpar o tabuleiro
# ------------------------------

def limpar_tabuleiro(tabuleiro):
    """Limpa o tabuleiro zerando todos os valores"""
    tabuleiro.fill(0)
    return tabuleiro

def kill_tabuleiro(tabuleiro):
    """Matamos o tabuleiro"""
    del tabuleiro

# ------------------------------
# Função para testar os algoritmos
# ------------------------------

def testar_algoritmos():
    """Função para testar e comparar os dois algoritmos com diferentes raios"""
    global tabuleiro
    
    # Lista de raios para testar (menor range para performance)
    raios = [10, 25, 50, 100, 200, 500, 1000, 1500, 2000]
    
    print("=== TESTE DOS ALGORITMOS DE CÍRCULO ===")
    centro = (size // 2, size // 2)  # Centro do tabuleiro
    print(f"Centro: {centro}")
    print(f"Tamanho do tabuleiro: {size}x{size}")
    print(f"Testando raios: {raios}")
    print()
    
    # Listas para armazenar os resultados
    tempos_seno = []
    tempos_bresenham = []
    pontos_seno_lista = []
    pontos_bresenham_lista = []
    
    print("Executando testes...")
    print("-" * 70)
    print(f"{'Raio':<8} {'Seno/Cos (s)':<12} {'Bresenham (s)':<13} {'Pts Seno':<10} {'Pts Bres':<10} {'Razão':<8}")
    print("-" * 70)
    
    for raio in raios:
        # 10 execuções para cada algoritmo
        tempos_seno_runs = []
        tempos_bresenham_runs = []
        
        for run in range(100):
            # Testar algoritmo Seno/Cosseno
            tabuleiro = limpar_tabuleiro(tabuleiro)
            pontos_seno, tempo_seno, metricas_seno, tabuleiro = circulo_seno_cosseno(centro, raio, tabuleiro)
            tempos_seno_runs.append(tempo_seno)
            
            # Testar algoritmo Bresenham
            tabuleiro = limpar_tabuleiro(tabuleiro)
            pontos_bresenham, tempo_bresenham, metricas_bresenham, tabuleiro = circulo_bresenham(centro, raio, tabuleiro)
            tempos_bresenham_runs.append(tempo_bresenham)
        
        # Calcular médias
        tempo_seno_medio = np.mean(tempos_seno_runs)
        tempo_bresenham_medio = np.mean(tempos_bresenham_runs)
        
        tempos_seno.append(tempo_seno_medio)
        tempos_bresenham.append(tempo_bresenham_medio)
        pontos_seno_lista.append(metricas_seno['pontos_gerados'])
        pontos_bresenham_lista.append(metricas_bresenham['pontos_gerados'])
        
        # Calcular razão de tempo
        razao = tempo_seno_medio / tempo_bresenham_medio if tempo_bresenham_medio > 0 else float('inf')
        
        # Mostrar resultados desta iteração
        print(f"{raio:<8} {tempo_seno_medio:<12.6f} {tempo_bresenham_medio:<13.6f} {metricas_seno['pontos_gerados']:<10} {metricas_bresenham['pontos_gerados']:<10} {razao:<8.2f}")
    
    print("-" * 70)
    print()
    
    # Análise estatística
    print("=== ANÁLISE ESTATÍSTICA ===")
    tempo_medio_seno = np.mean(tempos_seno)
    tempo_medio_bresenham = np.mean(tempos_bresenham)
    
    print(f"Tempo médio Seno/Cosseno: {tempo_medio_seno:.6f}s")
    print(f"Tempo médio Bresenham: {tempo_medio_bresenham:.6f}s")
    
    if tempo_medio_seno < tempo_medio_bresenham:
        mais_rapido = "Seno/Cosseno"
        diferenca = (tempo_medio_bresenham - tempo_medio_seno) / tempo_medio_seno * 100
    else:
        mais_rapido = "Bresenham"
        diferenca = (tempo_medio_seno - tempo_medio_bresenham) / tempo_medio_bresenham * 100
    
    print(f"Algoritmo mais rápido em média: {mais_rapido}")
    print(f"Diferença média: {diferenca:.2f}% mais rápido")
    print()
    
    # Criar gráficos
    criar_graficos(raios, tempos_seno, tempos_bresenham, pontos_seno_lista, pontos_bresenham_lista)


def criar_graficos(raios, tempos_seno, tempos_bresenham, pontos_seno, pontos_bresenham):
    """Cria gráficos comparativos dos algoritmos"""
    
    # Configurar estilo dos gráficos
    plt.style.use('default')
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 10))
    fig.suptitle('Comparação dos Algoritmos de Círculo: Seno/Cosseno vs Bresenham', fontsize=16, fontweight='bold')
    
    # Gráfico 1: Tempos de execução
    ax1.plot(raios, tempos_seno, 'b-o', label='Seno/Cosseno', linewidth=2, markersize=6)
    ax1.plot(raios, tempos_bresenham, 'r-s', label='Bresenham', linewidth=2, markersize=6)
    ax1.set_xlabel('Raio do Círculo')
    ax1.set_ylabel('Tempo de Execução (segundos)')
    ax1.set_title('Tempo de Execução por Raio')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    ax1.set_xscale('log')
    ax1.set_yscale('log')
    
    # Gráfico 2: Razão de tempos
    razao_tempos = [t_seno / t_bres if t_bres > 0 else 0 for t_seno, t_bres in zip(tempos_seno, tempos_bresenham)]
    ax2.plot(raios, razao_tempos, 'g-^', linewidth=2, markersize=6)
    ax2.axhline(y=1, color='black', linestyle='--', alpha=0.5, label='Tempos iguais')
    ax2.set_xlabel('Raio do Círculo')
    ax2.set_ylabel('Razão Tempo Seno/Cosseno / Tempo Bresenham')
    ax2.set_title('Razão de Tempos (>1 = Seno/Cos mais lento)')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    ax2.set_xscale('log')
    
    # Gráfico 3: Número de pontos gerados
    ax3.plot(raios, pontos_seno, 'b-o', label='Seno/Cosseno', linewidth=2, markersize=6)
    ax3.plot(raios, pontos_bresenham, 'r-s', label='Bresenham', linewidth=2, markersize=6)
    ax3.set_xlabel('Raio do Círculo')
    ax3.set_ylabel('Número de Pontos Gerados')
    ax3.set_title('Pontos Gerados por Raio')
    ax3.legend()
    ax3.grid(True, alpha=0.3)
    ax3.set_xscale('log')
    ax3.set_yscale('log')
    
    # Gráfico 4: Eficiência (pontos por segundo)
    eficiencia_seno = [pts / tempo if tempo > 0 else 0 for pts, tempo in zip(pontos_seno, tempos_seno)]
    eficiencia_bresenham = [pts / tempo if tempo > 0 else 0 for pts, tempo in zip(pontos_bresenham, tempos_bresenham)]
    
    ax4.plot(raios, eficiencia_seno, 'b-o', label='Seno/Cosseno', linewidth=2, markersize=6)
    ax4.plot(raios, eficiencia_bresenham, 'r-s', label='Bresenham', linewidth=2, markersize=6)
    ax4.set_xlabel('Raio do Círculo')
    ax4.set_ylabel('Pontos por Segundo')
    ax4.set_title('Eficiência (Pontos/Segundo)')
    ax4.legend()
    ax4.grid(True, alpha=0.3)
    ax4.set_xscale('log')
    ax4.set_yscale('log')
    
    # Ajustar layout e mostrar
    plt.tight_layout()
    plt.show()
    
    # Salvar o gráfico
    plt.savefig('comparacao_algoritmos_circulo.png', dpi=300, bbox_inches='tight')
    print("Gráfico salvo como 'comparacao_algoritmos_circulo.png'")
    print()
    
    # Estatísticas finais
    print("=== ESTATÍSTICAS FINAIS ===")
    print(f"Eficiência média Seno/Cosseno: {np.mean(eficiencia_seno):.0f} pontos/segundo")
    print(f"Eficiência média Bresenham: {np.mean(eficiencia_bresenham):.0f} pontos/segundo")
    
    # Encontrar o raio onde a diferença é maior
    diferencas_tempo = [abs(t_seno - t_bres) for t_seno, t_bres in zip(tempos_seno, tempos_bresenham)]
    idx_max_diff = diferencas_tempo.index(max(diferencas_tempo))
    print(f"Maior diferença de tempo no raio {raios[idx_max_diff]}: {max(diferencas_tempo):.6f}s")
    
    # Algoritmo consistentemente mais rápido
    seno_mais_rapido = sum(1 for t_seno, t_bres in zip(tempos_seno, tempos_bresenham) if t_seno < t_bres)
    bres_mais_rapido = len(tempos_seno) - seno_mais_rapido
    
    print(f"Seno/Cosseno foi mais rápido em {seno_mais_rapido}/{len(raios)} testes")
    print(f"Bresenham foi mais rápido em {bres_mais_rapido}/{len(raios)} testes")


if __name__ == "__main__":
    testar_algoritmos()
