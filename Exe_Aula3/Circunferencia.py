import sys
import math
import time
from typing import List, Optional, Tuple, Dict

import pygame


# ------------------------------
# Congurando Pygame
# ------------------------------
GRID_COLUMNS: int = 20
GRID_ROWS: int = 20
CELL_SIZE: int = 32
MARGIN: int = 32
WINDOW_WIDTH: int = GRID_COLUMNS * CELL_SIZE + MARGIN * 2
WINDOW_HEIGHT: int = GRID_ROWS * CELL_SIZE + MARGIN * 2
FPS: int = 60

# Colors
WHITE = (240, 240, 240)
BLACK = (30, 30, 30)
GRID_LINE = (120, 120, 120)
CHECKER_A = (210, 210, 210)
CHECKER_B = (245, 245, 245)
ENDPOINT_A = (50, 140, 255)
ENDPOINT_B = (40, 200, 120)
CONTINUOUS_LINE = (255, 210, 0)
RASTER_CELL = (220, 60, 60)
HUD_TEXT = (20, 20, 20)


GridCell = Tuple[int, int]


def grade_para_tela(cell: GridCell) -> Tuple[int, int]:
    col, row = cell
    x = MARGIN + col * CELL_SIZE
    y = MARGIN + row * CELL_SIZE
    return x, y


def centro_celula(cell: GridCell) -> Tuple[int, int]:
    x, y = grade_para_tela(cell)
    return x + CELL_SIZE // 2, y + CELL_SIZE // 2


def restringir_celula(cell: GridCell) -> GridCell:
    col, row = cell
    col = max(0, min(GRID_COLUMNS - 1, col))
    row = max(0, min(GRID_ROWS - 1, row))
    return col, row


def tela_para_grade(pos: Tuple[int, int]) -> Optional[GridCell]:
    x, y = pos
    x_rel = x - MARGIN
    y_rel = y - MARGIN
    if x_rel < 0 or y_rel < 0:
        return None
    col = x_rel // CELL_SIZE
    row = y_rel // CELL_SIZE
    if 0 <= col < GRID_COLUMNS and 0 <= row < GRID_ROWS:
        return int(col), int(row)
    return None


# ------------------------------
# Algoritmos de Rasterização de Circunferência
# ------------------------------

def circulo_seno_cosseno(center: GridCell, radius: int) -> Tuple[List[GridCell], float]:
    """
    Desenha círculo usando seno/cosseno - método trigonométrico.
    Retorna lista de pontos e tempo de execução.
    """
    start_time = time.perf_counter()
    
    cx, cy = center
    points: List[GridCell] = []
    
    # Número de pontos baseado na circunferência para boa qualidade
    num_points = max(8, int(2 * math.pi * radius))
    
    for i in range(num_points):
        angle = 2 * math.pi * i / num_points
        x = cx + int(radius * math.cos(angle) + 0.5)
        y = cy + int(radius * math.sin(angle) + 0.5)
        
        # Evitar pontos duplicados
        if (x, y) not in points:
            points.append((x, y))
    
    end_time = time.perf_counter()
    execution_time = end_time - start_time
    
    return points, execution_time


def circulo_bresenham(center: GridCell, radius: int) -> Tuple[List[GridCell], float]:
    """
    Desenha círculo usando algoritmo de Bresenham - método incremental.
    Retorna lista de pontos e tempo de execução.
    """
    start_time = time.perf_counter()
    
    cx, cy = center
    points: List[GridCell] = []
    
    x = 0
    y = radius
    d = 3 - 2 * radius
    
    # Função auxiliar para adicionar os 8 pontos simétricos
    def add_circle_points(cx: int, cy: int, x: int, y: int) -> None:
        points.extend([
            (cx + x, cy + y), (cx - x, cy + y),
            (cx + x, cy - y), (cx - x, cy - y),
            (cx + y, cy + x), (cx - y, cy + x),
            (cx + y, cy - x), (cx - y, cy - x)
        ])
    
    add_circle_points(cx, cy, x, y)
    
    while y >= x:
        x += 1
        
        if d > 0:
            y -= 1
            d = d + 4 * (x - y) + 10
        else:
            d = d + 4 * x + 6
            
        add_circle_points(cx, cy, x, y)
    
    # Remove duplicatas mantendo ordem
    seen = set()
    unique_points = []
    for point in points:
        if point not in seen:
            seen.add(point)
            unique_points.append(point)
    
    end_time = time.perf_counter()
    execution_time = end_time - start_time
    
    return unique_points, execution_time


def calcular_raio(center: GridCell, point: GridCell) -> int:
    """Calcula o raio baseado na distância entre centro e ponto."""
    cx, cy = center
    px, py = point
    return int(math.sqrt((px - cx) ** 2 + (py - cy) ** 2) + 0.5)


# ------------------------------
# Renderizando
# ------------------------------

def desenhar_tabuleiro(surface: pygame.Surface) -> None:
    for row in range(GRID_ROWS):
        for col in range(GRID_COLUMNS):
            x, y = grade_para_tela((col, row))
            rect = pygame.Rect(x, y, CELL_SIZE, CELL_SIZE)
            color = CHECKER_A if (row + col) % 2 == 0 else CHECKER_B
            surface.fill(color, rect)

    # Grid lines
    for c in range(GRID_COLUMNS + 1):
        x = MARGIN + c * CELL_SIZE
        pygame.draw.line(surface, GRID_LINE, (x, MARGIN), (x, MARGIN + GRID_ROWS * CELL_SIZE), 1)
    for r in range(GRID_ROWS + 1):
        y = MARGIN + r * CELL_SIZE
        pygame.draw.line(surface, GRID_LINE, (MARGIN, y), (MARGIN + GRID_COLUMNS * CELL_SIZE, y), 1)


def desenhar_pontos_extremos(surface: pygame.Surface, a: Optional[GridCell], b: Optional[GridCell]) -> None:
    if a is not None:
        ax, ay = centro_celula(a)
        pygame.draw.circle(surface, ENDPOINT_A, (ax, ay), CELL_SIZE // 3)
    if b is not None:
        bx, by = centro_celula(b)
        pygame.draw.circle(surface, ENDPOINT_B, (bx, by), CELL_SIZE // 3)


def desenhar_circulo_continuo(surface: pygame.Surface, center: GridCell, radius: int) -> None:
    """Desenha círculo contínuo usando pygame para referência visual."""
    cx, cy = centro_celula(center)
    pygame.draw.circle(surface, CONTINUOUS_LINE, (cx, cy), radius * CELL_SIZE, 2)


def desenhar_celulas_raster(surface: pygame.Surface, points: List[GridCell], steps_to_show: int) -> None:
    for i, (col, row) in enumerate(points[:steps_to_show]):
        x, y = grade_para_tela((col, row))
        rect = pygame.Rect(x + 2, y + 2, CELL_SIZE - 4, CELL_SIZE - 4)
        surface.fill(RASTER_CELL, rect)


def desenhar_hud(surface: pygame.Surface, font: pygame.font.Font, center: Optional[GridCell], 
             radius_point: Optional[GridCell], radius: int, algorithm: str, 
             timing_results: Dict[str, float], shown: int, total: int) -> None:
    lines = [
        "=== Comparação de Algoritmos de Circunferência ===",
        "Click: Centro -> Raio | SPACE: Alternar Algoritmo | R: Reset",
        "1-9: Raios pré-definidos | N: Próximo passo | ENTER: Todos os passos",
        "",
        f"Algoritmo Atual: {algorithm}",
    ]
    
    if center is not None:
        lines.append(f"Centro: {center}")
    if radius_point is not None:
        lines.append(f"Ponto do Raio: {radius_point}")
    if radius > 0:
        lines.append(f"Raio: {radius}")
    
    if total > 0:
        lines.append(f"Pontos: {shown}/{total}")
    
    # Resultados de timing
    if timing_results:
        lines.append("")
        lines.append("=== Tempos de Execução ===")
        for alg, time_val in timing_results.items():
            lines.append(f"{alg}: {time_val:.6f}s")
        
        if len(timing_results) == 2:
            times = list(timing_results.values())
            if times[1] > 0:  # Evitar divisão por zero
                speedup = times[0] / times[1]
                faster_alg = min(timing_results.keys(), key=lambda k: timing_results[k])
                lines.append(f"Mais rápido: {faster_alg}")
                lines.append(f"Speedup: {speedup:.2f}x")

    x = 16
    y = 8
    for text in lines:
        color = HUD_TEXT
        if "===" in text:
            color = (0, 100, 200)  # Azul para títulos
        elif "Algoritmo Atual:" in text:
            color = (200, 100, 0)  # Laranja para algoritmo atual
        elif "Mais rápido:" in text:
            color = (0, 150, 0)    # Verde para resultado
            
        surf = font.render(text, True, color)
        surface.blit(surf, (x, y))
        y += surf.get_height() + 2


# ------------------------------
# App State and Loop
# ------------------------------

class AppState:
    def __init__(self) -> None:
        self.center: Optional[GridCell] = None
        self.radius_point: Optional[GridCell] = None
        self.radius: int = 0
        self.current_algorithm: str = "Seno/Cosseno"
        self.raster_points: List[GridCell] = []
        self.steps_shown: int = 0
        self.timing_results: Dict[str, float] = {}

    def limpar_raster(self) -> None:
        self.raster_points = []
        self.steps_shown = 0

    def definir_centro(self, cell: GridCell) -> None:
        self.center = restringir_celula(cell)
        # When center changes, clear radius point and raster
        self.radius_point = None
        self.radius = 0
        self.limpar_raster()
        self.timing_results.clear()

    def definir_ponto_raio(self, cell: GridCell) -> None:
        self.radius_point = restringir_celula(cell)
        if self.center is not None:
            self.radius = calcular_raio(self.center, self.radius_point)
            self.recomputar_raster()

    def definir_raio(self, radius: int) -> None:
        self.radius = max(1, radius)
        self.radius_point = None  # Clear manual radius point
        if self.center is not None:
            self.recomputar_raster()

    def alternar_algoritmo(self) -> None:
        if self.current_algorithm == "Seno/Cosseno":
            self.current_algorithm = "Bresenham"
        else:
            self.current_algorithm = "Seno/Cosseno"
        
        if self.center is not None and self.radius > 0:
            self.recomputar_raster()

    def recomputar_raster(self) -> None:
        self.limpar_raster()
        if self.center is not None and self.radius > 0:
            # Executar ambos os algoritmos para comparação
            sine_points, sine_time = circulo_seno_cosseno(self.center, self.radius)
            bresenham_points, bresenham_time = circulo_bresenham(self.center, self.radius)
            
            # Armazenar tempos
            self.timing_results = {
                "Seno/Cosseno": sine_time,
                "Bresenham": bresenham_time
            }
            
            # Usar pontos do algoritmo atual
            if self.current_algorithm == "Seno/Cosseno":
                self.raster_points = sine_points
            else:
                self.raster_points = bresenham_points

    def passo(self) -> None:
        if not self.raster_points and self.center is not None and self.radius > 0:
            self.recomputar_raster()
        if self.steps_shown < len(self.raster_points):
            self.steps_shown += 1

    def executar_todos(self) -> None:
        if not self.raster_points and self.center is not None and self.radius > 0:
            self.recomputar_raster()
        self.steps_shown = len(self.raster_points)

    def resetar(self) -> None:
        self.center = None
        self.radius_point = None
        self.radius = 0
        self.limpar_raster()
        self.timing_results.clear()


def main() -> None:
    pygame.init()
    try:
        screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    except Exception as exc:
        print(f"Erro ao criar a janela: {exc}")
        pygame.quit()
        sys.exit(1)

    pygame.display.set_caption("Comparação de Algoritmos de Circunferência")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("consolas,monospace", 16)

    state = AppState()

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_r:
                    state.resetar()
                elif event.key == pygame.K_c:
                    # Clear only the rasterization (keep center and radius)
                    state.limpar_raster()
                elif event.key == pygame.K_n:
                    state.passo()
                elif event.key == pygame.K_RETURN:
                    state.executar_todos()
                elif event.key == pygame.K_SPACE:
                    state.alternar_algoritmo()
                # Raios pré-definidos (teclas 1-9)
                elif pygame.K_1 <= event.key <= pygame.K_9:
                    radius = event.key - pygame.K_0
                    if state.center is not None:
                        state.definir_raio(radius)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click: set center, then radius point
                    cell = tela_para_grade(event.pos)
                    if cell is not None:
                        if state.center is None:
                            state.definir_centro(cell)
                        else:
                            state.definir_ponto_raio(cell)
                elif event.button == 3:  # Right click: set center directly
                    cell = tela_para_grade(event.pos)
                    if cell is not None:
                        state.definir_centro(cell)

        screen.fill(WHITE)
        desenhar_tabuleiro(screen)

        # Draw circle overlays if center is set
        if state.center is not None:
            if state.radius > 0:
                desenhar_circulo_continuo(screen, state.center, state.radius)
            desenhar_pontos_extremos(screen, state.center, state.radius_point)

        if state.raster_points:
            desenhar_celulas_raster(screen, state.raster_points, state.steps_shown)

        desenhar_hud(
            screen,
            font,
            state.center,
            state.radius_point,
            state.radius,
            state.current_algorithm,
            state.timing_results,
            state.steps_shown,
            len(state.raster_points),
        )

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()


if __name__ == "__main__":
    main()
