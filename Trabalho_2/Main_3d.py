from OpenGL.GL import *
from OpenGL.GLU import *
import pygame
from pygame.locals import *
import sys
import multiprocessing as mp

from Aux_3D import (Estado3D, init_opengl, draw_sphere, update_light, render_3d_to_texture, FBO,
                   LARGURA_JANELA, ALTURA_JANELA, FPS, MATERIAL_COLORS, LARGURA_3D, ALTURA_3D)

# Layout constants (similar to Aux.py)
MARGEM = 10
PANEL_3D_POS = (MARGEM, MARGEM)  # Not used now, but kept for reference
PANEL_3D_SIZE = (LARGURA_3D, ALTURA_3D)
LARGURA_GUI = LARGURA_JANELA - LARGURA_3D - MARGEM * 2

# Light control settings
LIGHT_STEP = 0.5  # Larger step for light movement
BUTTON_REPEAT_DELAY = 300  # ms before repeat starts
BUTTON_REPEAT_INTERVAL = 50  # ms between repeats

# Color scheme
COLOR_SCHEME = {
    'bg': (245, 247, 250),
    'panel': (255, 255, 255),
    'border': (200, 210, 220),
    'text': (40, 50, 60),
    'text_light': (100, 110, 120),
    'accent': (70, 130, 220),
    'accent_hover': (90, 150, 240),
    'selected': (230, 240, 255),
    'button': (240, 243, 248),
    'button_hover': (220, 230, 245),
}

# Button system (pure Pygame, positioned in GUI area)
BOTOES_3D = [
    # Shape selector buttons
    {"texto": "Sphere", "rect": pygame.Rect(15, 60, 55, 32), "acao": "sphere", "tipo": "shape"},
    {"texto": "Cube", "rect": pygame.Rect(75, 60, 50, 32), "acao": "cube", "tipo": "shape"},
    {"texto": "Torus", "rect": pygame.Rect(130, 60, 50, 32), "acao": "torus", "tipo": "shape"},
    
    # Camera angle buttons
    {"texto": "Front", "rect": pygame.Rect(15, 135, 42, 28), "acao": "front", "tipo": "camera"},
    {"texto": "Top", "rect": pygame.Rect(62, 135, 38, 28), "acao": "top", "tipo": "camera"},
    {"texto": "Side", "rect": pygame.Rect(105, 135, 38, 28), "acao": "side", "tipo": "camera"},
    {"texto": "Diag", "rect": pygame.Rect(148, 135, 38, 28), "acao": "diagonal", "tipo": "camera"},
    
    # Color buttons (material selection)
    {"texto": "", "rect": pygame.Rect(25, 205, 40, 40), "acao": "orange", "cor": (255, 127, 0)},
    {"texto": "", "rect": pygame.Rect(75, 205, 40, 40), "acao": "red", "cor": (220, 60, 60)},
    {"texto": "", "rect": pygame.Rect(125, 205, 40, 40), "acao": "blue", "cor": (140, 190, 215)},
    
    # Light control buttons (grouped)
    {"texto": "↑", "rect": pygame.Rect(75, 295, 45, 38), "acao": "light_up", "tipo": "light"},
    {"texto": "↓", "rect": pygame.Rect(75, 378, 45, 38), "acao": "light_down", "tipo": "light"},
    {"texto": "←", "rect": pygame.Rect(20, 336, 45, 38), "acao": "light_left", "tipo": "light"},
    {"texto": "→", "rect": pygame.Rect(130, 336, 45, 38), "acao": "light_right", "tipo": "light"},
    
    # Re-render button
    {"texto": "🔄 Re-render", "rect": pygame.Rect(20, 450, 150, 40), "acao": "rerender", "tipo": "action"},
    
    # Quit button (bottom)
    {"texto": "✕ Quit", "rect": pygame.Rect(20, ALTURA_JANELA - 55, 150, 40), "acao": "quit", "tipo": "action"},
]

def draw_section_header(surface, font, text, y_pos):
    """Draw a beautiful section header"""
    header_rect = pygame.Rect(10, y_pos, 170, 30)
    pygame.draw.rect(surface, COLOR_SCHEME['panel'], header_rect, border_radius=8)
    pygame.draw.line(surface, COLOR_SCHEME['accent'], (15, y_pos + 28), (175, y_pos + 28), 2)
    
    text_surf = font.render(text, True, COLOR_SCHEME['text'])
    text_rect = text_surf.get_rect(center=(header_rect.centerx, header_rect.centery))
    surface.blit(text_surf, text_rect)

def desenhar_botoes(gui_surface, font, font_small, font_tiny, cor_atual, shape_atual, camera_atual):
    # Background for GUI panel with gradient effect
    gui_surface.fill(COLOR_SCHEME['bg'])
    
    # Draw section headers
    draw_section_header(gui_surface, font_small, "🔷 SHAPE", 25)
    draw_section_header(gui_surface, font_tiny, "📷 CAMERA", 100)
    draw_section_header(gui_surface, font_tiny, "🎨 MATERIAL", 170)
    draw_section_header(gui_surface, font_tiny, "💡 LIGHT", 260)
    
    for botao in BOTOES_3D:
        # Color buttons (material swatches)
        if "cor" in botao:
            # Draw shadow
            shadow_rect = botao["rect"].copy()
            shadow_rect.x += 2
            shadow_rect.y += 2
            pygame.draw.rect(gui_surface, (180, 180, 180), shadow_rect, border_radius=10)
            
            # Draw color swatch
            pygame.draw.rect(gui_surface, botao["cor"], botao["rect"], border_radius=10)
            
            # Highlight current material with accent border and glow
            if botao["acao"] == cor_atual:
                pygame.draw.rect(gui_surface, COLOR_SCHEME['accent'], botao["rect"], width=4, border_radius=10)
                # Inner highlight
                inner_rect = botao["rect"].inflate(-8, -8)
                pygame.draw.rect(gui_surface, (255, 255, 255, 128), inner_rect, width=2, border_radius=6)
            else:
                pygame.draw.rect(gui_surface, COLOR_SCHEME['border'], botao["rect"], width=2, border_radius=10)
        else:
            # Regular buttons with modern styling
            is_selected = False
            if botao.get("tipo") == "shape" and botao["acao"] == shape_atual:
                is_selected = True
            elif botao.get("tipo") == "camera" and botao["acao"] == camera_atual:
                is_selected = True
            
            # Draw shadow
            shadow_rect = botao["rect"].copy()
            shadow_rect.x += 2
            shadow_rect.y += 2
            pygame.draw.rect(gui_surface, (200, 200, 200), shadow_rect, border_radius=8)
            
            # Button background
            if is_selected:
                pygame.draw.rect(gui_surface, COLOR_SCHEME['selected'], botao["rect"], border_radius=8)
                pygame.draw.rect(gui_surface, COLOR_SCHEME['accent'], botao["rect"], width=3, border_radius=8)
            else:
                pygame.draw.rect(gui_surface, COLOR_SCHEME['panel'], botao["rect"], border_radius=8)
                pygame.draw.rect(gui_surface, COLOR_SCHEME['border'], botao["rect"], width=2, border_radius=8)
            
            # Text rendering
            if botao.get("tipo") == "light":
                # Arrows for light controls (larger font)
                texto_render = font.render(botao["texto"], True, COLOR_SCHEME['text'])
            elif botao.get("tipo") == "action":
                texto_render = font_small.render(botao["texto"], True, COLOR_SCHEME['text'])
            else:
                texto_render = font_tiny.render(botao["texto"], True, COLOR_SCHEME['text'])
            
            texto_rect = texto_render.get_rect(center=botao["rect"].center)
            gui_surface.blit(texto_render, texto_rect)

def desenhar_hud(gui_surface, font_small, font_tiny, estado, current_width, current_height):
    # Info section background with modern card design
    info_rect = pygame.Rect(10, 500, 170, 90)
    
    # Shadow
    shadow_rect = info_rect.copy()
    shadow_rect.x += 2
    shadow_rect.y += 2
    pygame.draw.rect(gui_surface, (200, 200, 200), shadow_rect, border_radius=10)
    
    # Card background
    pygame.draw.rect(gui_surface, COLOR_SCHEME['panel'], info_rect, border_radius=10)
    pygame.draw.rect(gui_surface, COLOR_SCHEME['border'], info_rect, width=2, border_radius=10)
    
    # Header
    header_surf = font_small.render("ℹ INFO", True, COLOR_SCHEME['accent'])
    gui_surface.blit(header_surf, (info_rect.x + 10, info_rect.y + 8))
    
    # Info lines with icons
    info_data = [
        (f"Shape: {estado.shape.capitalize()}", info_rect.y + 30),
        (f"Material: {estado.material.capitalize()}", info_rect.y + 45),
        (f"Camera: {estado.camera_angle.capitalize()}", info_rect.y + 60),
        (f"Window: {current_width}×{current_height}", info_rect.y + 75),
    ]
    
    for text, y_pos in info_data:
        surf = font_tiny.render(text, True, COLOR_SCHEME['text_light'])
        gui_surface.blit(surf, (info_rect.x + 10, y_pos))

def run_3d_window(cmd_queue, state_queue=None):
    """Process for the 3D rendering window."""
    pygame.init()
    # 3D window with OpenGL context and resizable flag
    screen_3d = pygame.display.set_mode((LARGURA_3D, ALTURA_3D), pygame.OPENGL | pygame.DOUBLEBUF | pygame.RESIZABLE)
    pygame.display.set_caption('3D Sphere Renderer')
    clock = pygame.time.Clock()
    
    # Initialize OpenGL state (for FBO rendering)
    init_opengl()
    
    # Create FBO for offscreen 3D rendering
    fbo = FBO(LARGURA_3D, ALTURA_3D)
    
    estado = Estado3D()
    running = True
    
    # Track current window size
    current_width = LARGURA_3D
    current_height = ALTURA_3D
    
    def display_fbo_texture(fbo, width, height):
        glBindFramebuffer(GL_FRAMEBUFFER, 0)
        glViewport(0, 0, width, height)
        glClearColor(1.0, 1.0, 1.0, 1.0)  # White background
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        
        # Disable depth test and lighting for 2D texture display
        glDisable(GL_DEPTH_TEST)
        glDisable(GL_LIGHTING)
        
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        glOrtho(0, width, 0, height, -1, 1)  # Changed: 0 at bottom, height at top
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        
        glEnable(GL_TEXTURE_2D)
        glBindTexture(GL_TEXTURE_2D, fbo.texture)
        glColor3f(1.0, 1.0, 1.0)
        
        glBegin(GL_QUADS)
        glTexCoord2f(0, 1); glVertex2f(0, 0)        # Bottom-left: flip Y
        glTexCoord2f(1, 1); glVertex2f(width, 0)    # Bottom-right: flip Y
        glTexCoord2f(1, 0); glVertex2f(width, height)  # Top-right: flip Y
        glTexCoord2f(0, 0); glVertex2f(0, height)   # Top-left: flip Y
        glEnd()
        
        glDisable(GL_TEXTURE_2D)
        
        # Re-enable for next frame
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_LIGHTING)
        
        # Optional border
        glColor3f(0.4, 0.4, 0.4)
        glBegin(GL_LINE_LOOP)
        glVertex2f(0, 0)
        glVertex2f(width, 0)
        glVertex2f(width, height)
        glVertex2f(0, height)
        glEnd()
    
    while running:
        for event in pygame.event.get():
            if event.type == QUIT:
                running = False
            elif event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    running = False
            elif event.type == VIDEORESIZE:
                # Handle window resize
                current_width = event.w
                current_height = event.h
                screen_3d = pygame.display.set_mode((current_width, current_height), pygame.OPENGL | pygame.DOUBLEBUF | pygame.RESIZABLE)
                # Reinitialize OpenGL state after resize
                init_opengl()
                # Send window size update to GUI
                if state_queue:
                    state_queue.put({'type': 'window_size', 'width': current_width, 'height': current_height})
        
        # Check for commands from queue
        try:
            while True:  # Non-blocking poll
                cmd = cmd_queue.get_nowait()
                if cmd['type'] == 'light_pos':
                    estado.light_pos = cmd['value']
                elif cmd['type'] == 'material':
                    estado.material = cmd['value']
                elif cmd['type'] == 'shape':
                    estado.shape = cmd['value']
                elif cmd['type'] == 'camera':
                    estado.camera_angle = cmd['value']
                elif cmd['type'] == 'rerender':
                    # Recreate FBO with new size if provided
                    new_width = cmd.get('width', current_width)
                    new_height = cmd.get('height', current_height)
                    print(f"Re-rendering FBO with size: {new_width}x{new_height}")
                    fbo = FBO(new_width, new_height)
                    init_opengl()
                elif cmd['type'] == 'quit':
                    running = False
                    break
        except mp.queues.Empty:
            pass
        
        # Render 3D scene offscreen to FBO
        render_3d_to_texture(estado, fbo)
        
        # Display the FBO texture to screen (scaled to current window size)
        display_fbo_texture(fbo, current_width, current_height)
        
        pygame.display.flip()
        clock.tick(FPS)
    
    # Cleanup
    pygame.quit()

def run_gui_window(cmd_queue, state_queue=None):
    """Process for the GUI controls window."""
    pygame.init()
    # GUI window
    screen_gui = pygame.display.set_mode((LARGURA_GUI, ALTURA_JANELA))
    pygame.display.set_caption('3D Controls')
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("arial", 22, bold=True)  # Larger for arrows
    font_small = pygame.font.SysFont("arial", 13, bold=True)  # Section headers
    font_tiny = pygame.font.SysFont("arial", 11)  # Button text
    
    # Enable key repeat for arrow keys
    pygame.key.set_repeat(BUTTON_REPEAT_DELAY, BUTTON_REPEAT_INTERVAL)
    
    estado = Estado3D()  # Local state for display
    current_width = LARGURA_3D  # Track 3D window size
    current_height = ALTURA_3D
    running = True
    
    # Track mouse button state for click-and-hold
    mouse_held_button = None
    mouse_hold_timer = 0
    mouse_hold_started = False
    
    while running:
        for event in pygame.event.get():
            if event.type == QUIT:
                running = False
                cmd_queue.put({'type': 'quit'})
            elif event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    running = False
                    cmd_queue.put({'type': 'quit'})
                elif event.key == K_UP:
                    estado.light_pos[1] -= LIGHT_STEP  # Inverted: up arrow = decrease Y
                    cmd_queue.put({'type': 'light_pos', 'value': list(estado.light_pos)})
                elif event.key == K_DOWN:
                    estado.light_pos[1] += LIGHT_STEP  # Inverted: down arrow = increase Y
                    cmd_queue.put({'type': 'light_pos', 'value': list(estado.light_pos)})
                elif event.key == K_LEFT:
                    estado.light_pos[0] -= LIGHT_STEP
                    cmd_queue.put({'type': 'light_pos', 'value': list(estado.light_pos)})
                elif event.key == K_RIGHT:
                    estado.light_pos[0] += LIGHT_STEP
                    cmd_queue.put({'type': 'light_pos', 'value': list(estado.light_pos)})
            elif event.type == MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    for botao in BOTOES_3D:
                        if botao["rect"].collidepoint(event.pos):
                            acao = botao["acao"]
                            # Store button for hold-and-repeat (only for light controls)
                            if acao in ["light_up", "light_down", "light_left", "light_right"]:
                                mouse_held_button = acao
                                mouse_hold_timer = pygame.time.get_ticks()
                                mouse_hold_started = False
                            
                            if acao in ["sphere", "cube", "torus"]:
                                estado.shape = acao
                                cmd_queue.put({'type': 'shape', 'value': acao})
                            elif acao in ["front", "top", "side", "diagonal"]:
                                estado.camera_angle = acao
                                cmd_queue.put({'type': 'camera', 'value': acao})
                            elif acao in MATERIAL_COLORS:
                                estado.material = acao
                                cmd_queue.put({'type': 'material', 'value': acao})
                            elif acao == "light_up":
                                estado.light_pos[1] -= LIGHT_STEP  # Inverted: up button = decrease Y
                                cmd_queue.put({'type': 'light_pos', 'value': list(estado.light_pos)})
                            elif acao == "light_down":
                                estado.light_pos[1] += LIGHT_STEP  # Inverted: down button = increase Y
                                cmd_queue.put({'type': 'light_pos', 'value': list(estado.light_pos)})
                            elif acao == "light_left":
                                estado.light_pos[0] -= LIGHT_STEP
                                cmd_queue.put({'type': 'light_pos', 'value': list(estado.light_pos)})
                            elif acao == "light_right":
                                estado.light_pos[0] += LIGHT_STEP
                                cmd_queue.put({'type': 'light_pos', 'value': list(estado.light_pos)})
                            elif acao == "rerender":
                                # Send re-render command with current window size
                                cmd_queue.put({'type': 'rerender', 'width': current_width, 'height': current_height})
                            elif acao == "quit":
                                running = False
                                cmd_queue.put({'type': 'quit'})
                            break
            elif event.type == MOUSEBUTTONUP:
                if event.button == 1:
                    mouse_held_button = None
                    mouse_hold_started = False
        
        # Handle mouse button hold-and-repeat for light controls
        if mouse_held_button:
            current_time = pygame.time.get_ticks()
            # Check if we should start repeating
            if not mouse_hold_started and (current_time - mouse_hold_timer) >= BUTTON_REPEAT_DELAY:
                mouse_hold_started = True
                mouse_hold_timer = current_time
            
            # Repeat action if holding
            if mouse_hold_started and (current_time - mouse_hold_timer) >= BUTTON_REPEAT_INTERVAL:
                mouse_hold_timer = current_time
                if mouse_held_button == "light_up":
                    estado.light_pos[1] -= LIGHT_STEP  # Inverted: up = decrease Y
                    cmd_queue.put({'type': 'light_pos', 'value': list(estado.light_pos)})
                elif mouse_held_button == "light_down":
                    estado.light_pos[1] += LIGHT_STEP  # Inverted: down = increase Y
                    cmd_queue.put({'type': 'light_pos', 'value': list(estado.light_pos)})
                elif mouse_held_button == "light_left":
                    estado.light_pos[0] -= LIGHT_STEP
                    cmd_queue.put({'type': 'light_pos', 'value': list(estado.light_pos)})
                elif mouse_held_button == "light_right":
                    estado.light_pos[0] += LIGHT_STEP
                    cmd_queue.put({'type': 'light_pos', 'value': list(estado.light_pos)})
        
        # Check for window size updates from 3D process
        try:
            while True:
                msg = state_queue.get_nowait() if state_queue else None
                if msg and msg['type'] == 'window_size':
                    current_width = msg['width']
                    current_height = msg['height']
                else:
                    break
        except:
            pass
        
        # Clear GUI surface
        screen_gui.fill((255, 255, 255))
        
        # Draw GUI (buttons and HUD)
        desenhar_botoes(screen_gui, font, font_small, font_tiny, estado.material, estado.shape, estado.camera_angle)
        desenhar_hud(screen_gui, font_small, font_tiny, estado, current_width, current_height)
        
        # Title at top with modern styling
        title_rect = pygame.Rect(5, 2, 180, 20)
        pygame.draw.rect(screen_gui, COLOR_SCHEME['accent'], title_rect, border_radius=5)
        title_surf = font_small.render("✨ 3D Shape Renderer", True, (255, 255, 255))
        screen_gui.blit(title_surf, (12, 5))
        
        pygame.display.flip()
        clock.tick(FPS)
    
    # Cleanup
    pygame.quit()

def main():
    # Create communication queues
    cmd_queue = mp.Queue()  # GUI -> 3D commands
    state_queue = mp.Queue()  # 3D -> GUI state updates
    
    # Spawn processes
    p3d = mp.Process(target=run_3d_window, args=(cmd_queue, state_queue))
    pgui = mp.Process(target=run_gui_window, args=(cmd_queue, state_queue))
    
    p3d.start()
    pgui.start()
    
    # Wait for processes to finish
    p3d.join()
    pgui.join()
    
    sys.exit()

if __name__ == "__main__":
    mp.set_start_method('spawn')  # Necessary for OpenGL in processes on some platforms
    main()
