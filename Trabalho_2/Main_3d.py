from OpenGL.GL import *
from OpenGL.GLU import *
import pygame
from pygame.locals import *
import sys
import multiprocessing as mp

from Aux_3D import (Estado3D, init_opengl, draw_sphere, update_light, render_3d_to_texture, FBO,
                   LARGURA_JANELA, ALTURA_JANELA, FPS, MATERIAL_COLORS, LARGURA_3D, ALTURA_3D, set_lighting_model)

# Layout constants
MARGEM = 15
LARGURA_GUI = 480  
LIGHT_STEP = 0.5
BUTTON_REPEAT_DELAY = 300
BUTTON_REPEAT_INTERVAL = 50

# Colors
COLOR_SCHEME = {
    'bg': (250, 251, 253),
    'panel': (255, 255, 255),
    'panel_alt': (247, 249, 252),
    'border': (190, 200, 215),
    'text': (30, 40, 55),
    'text_light': (110, 120, 135),
    'accent': (66, 135, 245),
    'accent_hover': (90, 160, 255),
    'selected': (225, 240, 255),
    'selected_border': (66, 135, 245),
    'button': (240, 243, 250),
    'button_hover': (220, 235, 255),
    'divider': (210, 220, 235),
}

# Buttons!!
def create_buttons():
    buttons = []
    margin = MARGEM
    width = LARGURA_GUI - 2 * margin

    # Shape selector buttons
    y_start = 55
    btn_w = (width - 3 * 8) // 4  
    btn_h = 40
    spacing = 8
    buttons.extend([
        {"texto": "Sphere", "rect": pygame.Rect(margin, y_start, btn_w, btn_h), "acao": "sphere", "tipo": "shape"},
        {"texto": "Cube", "rect": pygame.Rect(margin + btn_w + spacing, y_start, btn_w, btn_h), "acao": "cube", "tipo": "shape"},
        {"texto": "Torus", "rect": pygame.Rect(margin + 2 * (btn_w + spacing), y_start, btn_w, btn_h), "acao": "torus", "tipo": "shape"},
        {"texto": "Pyramid", "rect": pygame.Rect(margin + 3 * (btn_w + spacing), y_start, btn_w, btn_h), "acao": "pyramid", "tipo": "shape"},
    ])

    # Camera angle buttons 
    y_start = 120
    btn_h = 38
    buttons.extend([
        {"texto": "Front", "rect": pygame.Rect(margin, y_start, btn_w, btn_h), "acao": "front", "tipo": "camera"},
        {"texto": "Top", "rect": pygame.Rect(margin + btn_w + spacing, y_start, btn_w, btn_h), "acao": "top", "tipo": "camera"},
        {"texto": "Side", "rect": pygame.Rect(margin + 2 * (btn_w + spacing), y_start, btn_w, btn_h), "acao": "side", "tipo": "camera"},
        {"texto": "Diagonal", "rect": pygame.Rect(margin + 3 * (btn_w + spacing), y_start, btn_w, btn_h), "acao": "diagonal", "tipo": "camera"},
    ])

    # Lighting model buttons
    y_start = 185
    btn_h = 38
    btn_w_light = (width - 2 * spacing) // 3
    buttons.extend([
        {"texto": "Flat", "rect": pygame.Rect(margin, y_start, btn_w_light, btn_h), "acao": "flat", "tipo": "lighting"},
        {"texto": "Gouraud", "rect": pygame.Rect(margin + btn_w_light + spacing, y_start, btn_w_light, btn_h), "acao": "gouraud", "tipo": "lighting"},
        {"texto": "Phong", "rect": pygame.Rect(margin + 2 * (btn_w_light + spacing), y_start, btn_w_light, btn_h), "acao": "phong", "tipo": "lighting"},
    ])

    # Material color buttons 
    y_start = 250
    swatch_size = 50
    swatch_spacing = (width - 3 * swatch_size) // 4
    buttons.extend([
        {"texto": "", "rect": pygame.Rect(margin + swatch_spacing, y_start, swatch_size, swatch_size), "acao": "orange", "cor": (255, 127, 0)},
        {"texto": "", "rect": pygame.Rect(margin + 2 * swatch_spacing + swatch_size, y_start, swatch_size, swatch_size), "acao": "red", "cor": (220, 60, 60)},
        {"texto": "", "rect": pygame.Rect(margin + 3 * swatch_spacing + 2 * swatch_size, y_start, swatch_size, swatch_size), "acao": "blue", "cor": (140, 190, 215)},
    ])

    # Light control
    y_start = 330
    btn_size = 45
    center_x = margin + width // 2
    spacing_light = 12
    buttons.extend([
        {"texto": "↑", "rect": pygame.Rect(center_x - btn_size // 2, y_start, btn_size, btn_size), "acao": "light_up", "tipo": "light"},
        {"texto": "←", "rect": pygame.Rect(center_x - btn_size - spacing_light, y_start + btn_size + spacing_light, btn_size, btn_size), "acao": "light_left", "tipo": "light"},
        {"texto": "→", "rect": pygame.Rect(center_x + spacing_light, y_start + btn_size + spacing_light, btn_size, btn_size), "acao": "light_right", "tipo": "light"},
        {"texto": "↓", "rect": pygame.Rect(center_x - btn_size // 2, y_start + 2 * (btn_size + spacing_light), btn_size, btn_size), "acao": "light_down", "tipo": "light"},
    ])

    # Action buttons
    y_start = ALTURA_JANELA - 55
    btn_h = 40
    buttons.extend([
        {"texto": "Quit", "rect": pygame.Rect(margin, y_start, width, btn_h), "acao": "quit", "tipo": "action"},
    ])

    return buttons

BOTOES_3D = create_buttons()

def draw_section_header(surface, font, text, y_pos):
    margin = MARGEM
    width = LARGURA_GUI - 2 * margin
    text_surf = font.render(text, True, COLOR_SCHEME['accent'])
    surface.blit(text_surf, (margin, y_pos))
    # Subtle underline
    pygame.draw.line(surface, COLOR_SCHEME['divider'], (margin, y_pos + 20), (margin + width, y_pos + 20), 1)

def desenhar_botoes(gui_surface, font, font_small, font_tiny, cor_atual, shape_atual, camera_atual, lighting_atual):
    gui_surface.fill(COLOR_SCHEME['bg'])

    # Section headers - new positions for wider layout
    draw_section_header(gui_surface, font_tiny, "SHAPES", 30)
    draw_section_header(gui_surface, font_tiny, "CAMERA", 105)
    draw_section_header(gui_surface, font_tiny, "LIGHTING", 165)
    draw_section_header(gui_surface, font_tiny, "MATERIAL", 235)
    draw_section_header(gui_surface, font_tiny, "LIGHT POSITION", 315)
    
    # Draw buttons
    for botao in BOTOES_3D:
        if "cor" in botao:
            # Material color swatches with nice styling
            pygame.draw.rect(gui_surface, botao["cor"], botao["rect"], border_radius=10)
            
            # Border based on selection
            border_color = COLOR_SCHEME['selected_border'] if botao["acao"] == cor_atual else COLOR_SCHEME['border']
            border_width = 4 if botao["acao"] == cor_atual else 2
            pygame.draw.rect(gui_surface, border_color, botao["rect"], width=border_width, border_radius=10)
        else:
            # Regular buttons with improved styling
            is_selected = (
                (botao.get("tipo") == "shape" and botao["acao"] == shape_atual) or
                (botao.get("tipo") == "camera" and botao["acao"] == camera_atual) or
                (botao.get("tipo") == "lighting" and botao["acao"] == lighting_atual)
            )

            # Button background with gradient effect
            if is_selected:
                bg_color = COLOR_SCHEME['selected']
                border_color = COLOR_SCHEME['selected_border']
                border_width = 2.5
            else:
                bg_color = COLOR_SCHEME['button']
                border_color = COLOR_SCHEME['border']
                border_width = 1
            
            pygame.draw.rect(gui_surface, bg_color, botao["rect"], border_radius=8)
            pygame.draw.rect(gui_surface, border_color, botao["rect"], width=int(border_width), border_radius=8)

            # Text rendering with appropriate font
            if botao.get("tipo") == "light":
                texto_render = font.render(botao["texto"], True, COLOR_SCHEME['text'])
            else:
                texto_render = font_small.render(botao["texto"], True, COLOR_SCHEME['text'])

            texto_rect = texto_render.get_rect(center=botao["rect"].center)
            gui_surface.blit(texto_render, texto_rect)

def desenhar_hud(gui_surface, font_small, font_tiny, estado):
    margin = MARGEM
    width = LARGURA_GUI - 2 * margin
    info_rect = pygame.Rect(margin, ALTURA_JANELA - 50, width, 38)

    # Panel styling
    pygame.draw.rect(gui_surface, COLOR_SCHEME['panel_alt'], info_rect, border_radius=8)
    pygame.draw.rect(gui_surface, COLOR_SCHEME['divider'], info_rect, width=1, border_radius=8)

    # Info text with better layout - 3 columns
    col_width = width // 3
    info_items = [
        ("Shape", estado.shape.capitalize()),
        ("Lighting", estado.lighting_model.capitalize()),
        ("Camera", estado.camera_angle.capitalize()),
    ]
    
    y = info_rect.y + 8
    for idx, (label, value) in enumerate(info_items):
        x = margin + idx * col_width + 10
        label_surf = font_tiny.render(label + ":", True, COLOR_SCHEME['text_light'])
        value_surf = font_tiny.render(value, True, COLOR_SCHEME['accent'])
        gui_surface.blit(label_surf, (x, y))
        gui_surface.blit(value_surf, (x, y + 14))

def run_3d_window(cmd_queue, state_queue=None):
    """Process for 3D rendering window!!"""
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
                elif cmd['type'] == 'lighting':
                    estado.lighting_model = cmd['value']
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
        
        # Display the FBO texture to screen
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
    font = pygame.font.SysFont("arial", 20, bold=True)  
    font_small = pygame.font.SysFont("arial", 12, bold=True)  
    font_tiny = pygame.font.SysFont("arial", 10)  
    
    # Enable key repeat for arrow keys
    pygame.key.set_repeat(BUTTON_REPEAT_DELAY, BUTTON_REPEAT_INTERVAL)
    
    estado = Estado3D()  
    current_width = LARGURA_3D  
    current_height = ALTURA_3D
    running = True
    
    # Track mouse (for click and hold functionality!)
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
                    estado.light_pos[1] -= LIGHT_STEP  
                    cmd_queue.put({'type': 'light_pos', 'value': list(estado.light_pos)})
                elif event.key == K_DOWN:
                    estado.light_pos[1] += LIGHT_STEP  
                    cmd_queue.put({'type': 'light_pos', 'value': list(estado.light_pos)})
                elif event.key == K_LEFT:
                    estado.light_pos[0] -= LIGHT_STEP
                    cmd_queue.put({'type': 'light_pos', 'value': list(estado.light_pos)})
                elif event.key == K_RIGHT:
                    estado.light_pos[0] += LIGHT_STEP
                    cmd_queue.put({'type': 'light_pos', 'value': list(estado.light_pos)})
            elif event.type == MOUSEBUTTONDOWN:
                if event.button == 1:  
                    for botao in BOTOES_3D:
                        if botao["rect"].collidepoint(event.pos):
                            acao = botao["acao"]
                            # Store button for hold-and-repeat
                            if acao in ["light_up", "light_down", "light_left", "light_right"]:
                                mouse_held_button = acao
                                mouse_hold_timer = pygame.time.get_ticks()
                                mouse_hold_started = False
                            
                            if acao in ["sphere", "cube", "torus", "pyramid"]:
                                estado.shape = acao
                                cmd_queue.put({'type': 'shape', 'value': acao})
                            elif acao in ["front", "top", "side", "diagonal"]:
                                estado.camera_angle = acao
                                cmd_queue.put({'type': 'camera', 'value': acao})
                            elif acao in ["flat", "gouraud", "phong"]:
                                estado.lighting_model = acao
                                cmd_queue.put({'type': 'lighting', 'value': acao})
                            elif acao in MATERIAL_COLORS:
                                estado.material = acao
                                cmd_queue.put({'type': 'material', 'value': acao})
                            elif acao == "light_up":
                                estado.light_pos[1] -= LIGHT_STEP  
                                cmd_queue.put({'type': 'light_pos', 'value': list(estado.light_pos)})
                            elif acao == "light_down":
                                estado.light_pos[1] += LIGHT_STEP  
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
                    estado.light_pos[1] -= LIGHT_STEP  
                    cmd_queue.put({'type': 'light_pos', 'value': list(estado.light_pos)})
                elif mouse_held_button == "light_down":
                    estado.light_pos[1] += LIGHT_STEP  
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
        
        # Clear GUI surface with background color
        screen_gui.fill(COLOR_SCHEME['bg'])
        
        # Draw title bar with gradient effect
        title_rect = pygame.Rect(0, 0, LARGURA_GUI, 28)
        pygame.draw.rect(screen_gui, COLOR_SCHEME['accent'], title_rect)
        title_surf = font.render("3D Renderer", True, (255, 255, 255))
        title_rect_centered = title_surf.get_rect(center=(LARGURA_GUI // 2, 14))
        screen_gui.blit(title_surf, title_rect_centered)
        
        # Draw GUI controls
        desenhar_botoes(screen_gui, font, font_small, font_tiny, estado.material, estado.shape, estado.camera_angle, estado.lighting_model)
        desenhar_hud(screen_gui, font_small, font_tiny, estado)
        
        pygame.display.flip()
        clock.tick(FPS)
    
    # Cleanup
    pygame.quit()

def main():
    # Create communication queues
    cmd_queue = mp.Queue()  
    state_queue = mp.Queue()  
    
    # Spawn processes
    p3d = mp.Process(target=run_3d_window, args=(cmd_queue, state_queue))
    pgui = mp.Process(target=run_gui_window, args=(cmd_queue, state_queue))
    
    p3d.start()
    pgui.start()
    
    p3d.join()
    pgui.join()
    
    sys.exit()

if __name__ == "__main__":
    mp.set_start_method('spawn')  
    main()
