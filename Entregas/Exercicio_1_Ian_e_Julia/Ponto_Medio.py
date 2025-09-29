import sys
import math
from typing import List, Optional, Tuple

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


def grid_to_screen(cell: GridCell) -> Tuple[int, int]:
    col, row = cell
    x = MARGIN + col * CELL_SIZE
    y = MARGIN + row * CELL_SIZE
    return x, y


def cell_center(cell: GridCell) -> Tuple[int, int]:
    x, y = grid_to_screen(cell)
    return x + CELL_SIZE // 2, y + CELL_SIZE // 2


def clamp_cell(cell: GridCell) -> GridCell:
    col, row = cell
    col = max(0, min(GRID_COLUMNS - 1, col))
    row = max(0, min(GRID_ROWS - 1, row))
    return col, row


def screen_to_grid(pos: Tuple[int, int]) -> Optional[GridCell]:
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
# Rasterizacao do Ponto Medio (Bresenham-style)
# ------------------------------

def metodo_ponto_medio(a: GridCell, b: GridCell) -> List[GridCell]:
    """
    Calcula rasterizacao das celulas entre a e b usando o metodo do Ponto Medio.
    """
    x0, y0 = a
    x1, y1 = b

    points: List[GridCell] = []

    dx = x1 - x0
    dy = y1 - y0

    sx = 1 if dx > 0 else (-1 if dx < 0 else 0)
    sy = 1 if dy > 0 else (-1 if dy < 0 else 0)

    dx = abs(dx)
    dy = abs(dy)

    x = x0
    y = y0
    points.append((x, y))

    if dx == 0 and dy == 0:
        return points

    # Inclinacao suave: iteratar sobre x
    if dx >= dy:
        d = 2 * dy - dx
        incr_e = 2 * dy
        incr_ne = 2 * (dy - dx)
        while x != x1:
            if d <= 0:
                d += incr_e
                x += sx
            else:
                d += incr_ne
                x += sx
                y += sy
            points.append((x, y))
    else:
        # Inclinacao agressiva: iterar sobre y
        d = 2 * dx - dy
        incr_n = 2 * dx
        incr_ne = 2 * (dx - dy)
        while y != y1:
            if d <= 0:
                d += incr_n
                y += sy
            else:
                d += incr_ne
                x += sx
                y += sy
            points.append((x, y))

    return points


# ------------------------------
# Renderizando
# ------------------------------

def draw_checkerboard(surface: pygame.Surface) -> None:
    for row in range(GRID_ROWS):
        for col in range(GRID_COLUMNS):
            x, y = grid_to_screen((col, row))
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


def draw_endpoints(surface: pygame.Surface, a: Optional[GridCell], b: Optional[GridCell]) -> None:
    if a is not None:
        ax, ay = cell_center(a)
        pygame.draw.circle(surface, ENDPOINT_A, (ax, ay), CELL_SIZE // 3)
    if b is not None:
        bx, by = cell_center(b)
        pygame.draw.circle(surface, ENDPOINT_B, (bx, by), CELL_SIZE // 3)


def draw_continuous_line(surface: pygame.Surface, a: GridCell, b: GridCell) -> None:
    ax, ay = cell_center(a)
    bx, by = cell_center(b)
    pygame.draw.aaline(surface, CONTINUOUS_LINE, (ax, ay), (bx, by))


def draw_raster_cells(surface: pygame.Surface, points: List[GridCell], steps_to_show: int) -> None:
    for i, (col, row) in enumerate(points[:steps_to_show]):
        x, y = grid_to_screen((col, row))
        rect = pygame.Rect(x + 2, y + 2, CELL_SIZE - 4, CELL_SIZE - 4)
        surface.fill(RASTER_CELL, rect)


def draw_hud(surface: pygame.Surface, font: pygame.font.Font, a: Optional[GridCell], b: Optional[GridCell], shown: int, total: int) -> None:
    lines = [
        "Algoritmo do Ponto Médio (Rasterização de Reta)",
    ]
    if a is not None:
        lines.append(f"A: {a}")
    if b is not None:
        lines.append(f"B: {b}")
    if total > 0:
        lines.append(f"Passos: {shown}/{total}")

    x = 16
    y = 8
    for text in lines:
        surf = font.render(text, True, HUD_TEXT)
        surface.blit(surf, (x, y))
        y += surf.get_height() + 2


# ------------------------------
# App State and Loop
# ------------------------------

class AppState:
    def __init__(self) -> None:
        self.endpoint_a: Optional[GridCell] = None
        self.endpoint_b: Optional[GridCell] = None
        self.raster_points: List[GridCell] = []
        self.steps_shown: int = 0

    def clear_raster(self) -> None:
        self.raster_points = []
        self.steps_shown = 0

    def set_a(self, cell: GridCell) -> None:
        self.endpoint_a = clamp_cell(cell)
        # When A changes, clear raster and B until user sets B
        self.endpoint_b = None
        self.clear_raster()

    def set_b(self, cell: GridCell) -> None:
        self.endpoint_b = clamp_cell(cell)
        self.recompute_raster()

    def recompute_raster(self) -> None:
        self.clear_raster()
        if self.endpoint_a is not None and self.endpoint_b is not None:
            self.raster_points = metodo_ponto_medio(self.endpoint_a, self.endpoint_b)

    def step(self) -> None:
        if not self.raster_points and self.endpoint_a is not None and self.endpoint_b is not None:
            self.recompute_raster()
        if self.steps_shown < len(self.raster_points):
            self.steps_shown += 1

    def run_all(self) -> None:
        if not self.raster_points and self.endpoint_a is not None and self.endpoint_b is not None:
            self.recompute_raster()
        self.steps_shown = len(self.raster_points)

    def reset(self) -> None:
        self.endpoint_a = None
        self.endpoint_b = None
        self.clear_raster()


def main() -> None:
    pygame.init()
    try:
        screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    except Exception as exc:
        print(f"Erro ao criar a janela: {exc}")
        pygame.quit()
        sys.exit(1)

    pygame.display.set_caption("Midpoint Line Rasterization (Ponto Médio)")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("consolas,monospace", 18)

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
                    state.reset()
                elif event.key == pygame.K_c:
                    # Clear only the rasterization (keep endpoints)
                    state.clear_raster()
                elif event.key == pygame.K_n:
                    state.step()
                elif event.key == pygame.K_SPACE:
                    state.run_all()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click: set A, then B, then redefine A
                    cell = screen_to_grid(event.pos)
                    if cell is not None:
                        if state.endpoint_a is None:
                            state.set_a(cell)
                        elif state.endpoint_b is None:
                            state.set_b(cell)
                        else:
                            state.set_a(cell)
                elif event.button == 3:  # Right click: set B directly (if A exists)
                    cell = screen_to_grid(event.pos)
                    if cell is not None:
                        if state.endpoint_a is None:
                            # Define A first if not set
                            state.set_a(cell)
                        else:
                            state.set_b(cell)

        screen.fill(WHITE)
        draw_checkerboard(screen)

        # Draw overlays if endpoints set
        if state.endpoint_a is not None:
            if state.endpoint_b is not None:
                draw_continuous_line(screen, state.endpoint_a, state.endpoint_b)
            draw_endpoints(screen, state.endpoint_a, state.endpoint_b)

        if state.raster_points:
            draw_raster_cells(screen, state.raster_points, state.steps_shown)

        draw_hud(
            screen,
            font,
            state.endpoint_a,
            state.endpoint_b,
            state.steps_shown,
            len(state.raster_points),
        )

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()


if __name__ == "__main__":
    main()
