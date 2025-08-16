#!/usr/bin/env python3
"""
Benchmark script para comparar algoritmos de círculo.
Este script executa testes automáticos com diferentes raios para comparar performance.
"""

import time
import math
from typing import List, Tuple

# Importar as funções de círculo do arquivo principal
from Circunferencia import circulo_seno_cosseno, circulo_bresenham

def benchmark_algorithms(center: Tuple[int, int], radii: List[int], iterations: int = 100) -> None:
    """
    Executa benchmark dos algoritmos de círculo com diferentes raios.
    
    Args:
        center: Centro do círculo (x, y)
        radii: Lista de raios para testar
        iterations: Número de iterações para cada teste (para obter média mais confiável)
    """
    print("=" * 60)
    print("BENCHMARK DE ALGORITMOS DE CÍRCULO")
    print("=" * 60)
    print(f"Centro: {center}")
    print(f"Iterações por teste: {iterations}")
    print()
    
    results = []
    
    for radius in radii:
        print(f"Testando raio {radius}...")
        
        # Teste Sine/Cosine
        sine_times = []
        for _ in range(iterations):
            _, exec_time = circulo_seno_cosseno(center, radius)
            sine_times.append(exec_time)
        avg_sine_time = sum(sine_times) / len(sine_times)
        
        # Teste Bresenham  
        bresenham_times = []
        for _ in range(iterations):
            _, exec_time = circulo_bresenham(center, radius)
            bresenham_times.append(exec_time)
        avg_bresenham_time = sum(bresenham_times) / len(bresenham_times)
        
        # Calcular speedup
        if avg_bresenham_time > 0:
            speedup = avg_sine_time / avg_bresenham_time
        else:
            speedup = float('inf')
        
        faster_algorithm = "Bresenham" if avg_bresenham_time < avg_sine_time else "Seno/Cosseno"
        
        results.append({
            'radius': radius,
            'sine_time': avg_sine_time,
            'bresenham_time': avg_bresenham_time,
            'speedup': speedup,
            'faster': faster_algorithm
        })
        
        print(f"  Seno/Cosseno: {avg_sine_time:.8f}s")
        print(f"  Bresenham:   {avg_bresenham_time:.8f}s")
        print(f"  Mais rápido: {faster_algorithm}")
        print(f"  Speedup:     {speedup:.2f}x")
        print()
    
    # Resumo dos resultados
    print("=" * 60)
    print("RESUMO DOS RESULTADOS")
    print("=" * 60)
    print(f"{'Raio':<6} {'Seno/Cos (s)':<15} {'Bresenham (s)':<15} {'Speedup':<10} {'Mais Rápido'}")
    print("-" * 60)
    
    for result in results:
        print(f"{result['radius']:<6} "
              f"{result['sine_time']:.8f}    "
              f"{result['bresenham_time']:.8f}    "
              f"{result['speedup']:<8.2f}  "
              f"{result['faster']}")
    
    # Estatísticas finais
    sine_wins = sum(1 for r in results if r['faster'] == 'Seno/Cosseno')
    bresenham_wins = sum(1 for r in results if r['faster'] == 'Bresenham')
    
    print()
    print("ESTATÍSTICAS FINAIS:")
    print(f"Vitórias Seno/Cosseno: {sine_wins}")
    print(f"Vitórias Bresenham:   {bresenham_wins}")
    
    avg_speedup = sum(r['speedup'] for r in results) / len(results)
    print(f"Speedup médio:        {avg_speedup:.2f}x")


def main():
    """Executa o benchmark com diferentes configurações de teste."""
    
    # Centro na metade da grid (baseado no arquivo original)
    center = (10, 10)
    
    # Diferentes raios para testar
    small_radii = [1, 2, 3, 4, 5]
    medium_radii = [6, 7, 8, 9, 10]
    large_radii = [15, 20, 25, 30]
    
    print("Executando benchmarks...")
    print()
    
    # Teste com raios pequenos
    print("TESTE 1: Raios Pequenos (1-5)")
    benchmark_algorithms(center, small_radii, iterations=1000)
    
    # Teste com raios médios  
    print("\nTESTE 2: Raios Médios (6-10)")
    benchmark_algorithms(center, medium_radii, iterations=500)
    
    # Teste com raios grandes
    print("\nTESTE 3: Raios Grandes (15-30)")
    benchmark_algorithms(center, large_radii, iterations=100)
    
    print("\nBenchmark completo!")
    print("\nOBSERVAÇÕES:")
    print("- Algoritmo Bresenham geralmente é mais rápido por usar apenas aritmética inteira")
    print("- Algoritmo Sine/Cosine pode ser mais preciso mas usa funções trigonométricas custosas")
    print("- Performance pode variar dependendo do hardware e implementação do Python")


if __name__ == "__main__":
    main()
